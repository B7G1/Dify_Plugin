"""Isolated SQL Server driver/runtime probe.

This script is intentionally outside product imports and verification matrices.
It audits SQL Server runtime readiness without changing Provider/Tool/Adapter
logic.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_ENV = (
    "SQLSERVER_HOST",
    "SQLSERVER_PORT",
    "SQLSERVER_DATABASE",
    "SQLSERVER_USERNAME",
    "SQLSERVER_PASSWORD",
)
OPTIONAL_DEFAULTS = {
    "SQLSERVER_PORT": "1433",
    "SQLSERVER_SCHEMA": "plugin_test",
    "SQLSERVER_CONNECT_TIMEOUT": "5",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--env-file", help="Optional KEY=VALUE env file loaded before the probe runs.")
    args = parser.parse_args()

    if args.env_file:
        load_env_file(Path(args.env_file))

    result = run_probe()
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")

    return int(result["exit_code"])


def run_probe() -> dict[str, Any]:
    report: dict[str, Any] = {
        "suite": "sqlserver_driver_probe",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": None,
        "reason": None,
        "exit_code": None,
        "python": {
            "version": sys.version.splitlines()[0],
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "checks": {},
        "connection_env": {},
        "safe_url": None,
        "connection_probe": None,
        "error": None,
    }

    config = resolved_env()
    missing_env = [name for name in REQUIRED_ENV if not os.getenv(name)]
    report["connection_env"] = {
        "required_names": list(REQUIRED_ENV),
        "optional_defaults": dict(OPTIONAL_DEFAULTS),
        "present_names": sorted(name for name in REQUIRED_ENV if os.getenv(name)),
        "missing_env": missing_env,
        "schema": config["schema"],
        "host": config["host"],
        "port": config["port"],
        "database": config["database"],
        "username": config["username"],
    }

    sqlalchemy_mod, sqlalchemy_error = try_import("sqlalchemy")
    pymssql_mod, pymssql_error = try_import("pymssql")

    report["checks"]["sqlalchemy_import"] = import_check(sqlalchemy_mod, sqlalchemy_error)
    report["checks"]["pymssql_import"] = import_check(pymssql_mod, pymssql_error)

    if sqlalchemy_mod is None or pymssql_mod is None:
        report["status"] = "FAIL_IMPORT"
        report["reason"] = "MISSING_DRIVER_DEPENDENCY"
        report["exit_code"] = 3
        return report

    try:
        url, dialect = build_sqlalchemy_artifacts(sqlalchemy_mod, config)
        safe_url = url.render_as_string(hide_password=True)
        report["safe_url"] = safe_url
        report["checks"]["url_build"] = {
            "ok": True,
            "drivername": url.drivername,
            "dialect_name": url.get_dialect().name,
            "safe_url_has_password": contains_password(safe_url, config["password"]),
        }
        report["checks"]["dialect_load"] = {
            "ok": True,
            "dialect_name": dialect.name,
            "driver": dialect.driver,
        }
    except Exception as exc:  # noqa: BLE001
        report["status"] = "NO_GO"
        report["reason"] = "SQLALCHEMY_DIALECT_OR_URL_FAILURE"
        report["exit_code"] = 5
        report["error"] = error_payload(exc)
        return report

    if missing_env:
        report["status"] = "BLOCKED"
        report["reason"] = "MISSING_ENV"
        report["exit_code"] = 2
        return report

    try:
        probe = run_connection_probe(sqlalchemy_mod, url, config)
        report["connection_probe"] = probe
        report["status"] = "PASS"
        report["reason"] = "CONNECTION_PROBE_OK"
        report["exit_code"] = 0
        return report
    except Exception as exc:  # noqa: BLE001
        report["connection_probe"] = {"ok": False}
        report["status"] = "FAIL"
        report["reason"] = "CONNECTION_PROBE_FAILED"
        report["exit_code"] = 4
        report["error"] = error_payload(exc)
        return report


def resolved_env() -> dict[str, Any]:
    return {
        "host": os.getenv("SQLSERVER_HOST", ""),
        "port": int(os.getenv("SQLSERVER_PORT", OPTIONAL_DEFAULTS["SQLSERVER_PORT"])),
        "database": os.getenv("SQLSERVER_DATABASE", ""),
        "username": os.getenv("SQLSERVER_USERNAME", ""),
        "password": os.getenv("SQLSERVER_PASSWORD", ""),
        "schema": os.getenv("SQLSERVER_SCHEMA", OPTIONAL_DEFAULTS["SQLSERVER_SCHEMA"]),
        "connect_timeout": int(os.getenv("SQLSERVER_CONNECT_TIMEOUT", OPTIONAL_DEFAULTS["SQLSERVER_CONNECT_TIMEOUT"])),
    }


def load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def try_import(module_name: str) -> tuple[Any | None, str | None]:
    try:
        return importlib.import_module(module_name), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{exc.__class__.__name__}: {exc}"


def import_check(module: Any | None, error: str | None) -> dict[str, Any]:
    if module is None:
        return {"ok": False, "error": error}
    return {"ok": True, "module": module.__name__, "version": str(getattr(module, "__version__", "unknown"))}


def build_sqlalchemy_artifacts(sqlalchemy_mod: Any, config: dict[str, Any]) -> tuple[Any, Any]:
    url = sqlalchemy_mod.URL.create(
        "mssql+pymssql",
        username=config["username"] or "probe_user",
        password=config["password"] or "probe_password",
        host=config["host"] or "localhost",
        port=config["port"],
        database=config["database"] or "plugin_test",
    )
    from sqlalchemy.dialects import registry  # type: ignore

    dialect = registry.load("mssql.pymssql")
    return url, dialect


def run_connection_probe(sqlalchemy_mod: Any, url: Any, config: dict[str, Any]) -> dict[str, Any]:
    text = sqlalchemy_mod.text
    create_engine = sqlalchemy_mod.create_engine
    engine = create_engine(
        url,
        connect_args={"timeout": config["connect_timeout"]},
        pool_pre_ping=True,
    )
    try:
        with engine.connect() as connection:
            probe_value = summarize_mapping(connection.execute(text("SELECT 1 AS probe_value")).mappings().first())
            table_probe = None
            try:
                table_probe = connection.execute(
                    text(f"SELECT TOP 5 * FROM [{config['schema']}].[plugin_test_users] ORDER BY [id]")
                ).mappings().all()
            except Exception as exc:  # noqa: BLE001
                table_probe = {"skipped_or_failed": f"{exc.__class__.__name__}: {exc}"}
    finally:
        engine.dispose()

    row_count = len(table_probe) if isinstance(table_probe, list) else None
    return {
        "ok": True,
        "select_1": probe_value,
        "top_5_row_count": row_count,
        "top_5_probe": summarize_rows(table_probe),
    }


def summarize_rows(rows: Any) -> Any:
    if not isinstance(rows, list):
        return rows
    summary = []
    for row in rows[:5]:
        summary.append(summarize_mapping(row))
    return summary


def summarize_mapping(row: Any) -> Any:
    if row is None:
        return None
    item = {}
    for key, value in dict(row).items():
        item[str(key)] = None if value is None else str(value)
    return item


def contains_password(safe_url: str, password: str) -> bool:
    if password and password in safe_url:
        return True
    return "probe_password" in safe_url


def error_payload(exc: Exception) -> dict[str, Any]:
    return {
        "type": exc.__class__.__name__,
        "message": str(exc),
        "traceback_tail": traceback.format_exc(limit=3).splitlines()[-6:],
    }


if __name__ == "__main__":
    raise SystemExit(main())
