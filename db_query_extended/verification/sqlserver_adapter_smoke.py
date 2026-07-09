"""Independent SQL Server adapter smoke test."""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.database import build_database_url, create_database_engine, execute_read_only_query  # noqa: E402
from utils.validation import validate_connection_config  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    load_env_file(Path(args.env_file))
    result = run_smoke()
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")
    return int(result["exit_code"])


def run_smoke() -> dict[str, Any]:
    report: dict[str, Any] = {
        "suite": "sqlserver_adapter_smoke",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": None,
        "exit_code": None,
        "safe_url": None,
        "checks": {},
        "error": None,
    }
    try:
        config = validate_connection_config(
            {
                "database_type": "sqlserver",
                "host": env("SQLSERVER_HOST"),
                "port": env("SQLSERVER_PORT", "1433"),
                "database": env("SQLSERVER_DATABASE"),
                "username": env("SQLSERVER_USERNAME"),
                "password": env("SQLSERVER_PASSWORD"),
                "schema": env("SQLSERVER_SCHEMA", "plugin_test"),
                "connection_timeout": env("SQLSERVER_CONNECT_TIMEOUT", "5"),
                "ssl_mode": "disable",
            }
        )
        report["checks"]["adapter_import"] = {"ok": True}
        url = build_database_url(config)
        report["safe_url"] = url.render_as_string(hide_password=True)
        report["checks"]["url_build"] = {
            "ok": True,
            "drivername": url.drivername,
            "dialect_name": url.get_dialect().name,
        }

        engine = create_database_engine(config)
        engine.dispose()
        report["checks"]["engine_creation"] = {"ok": True}

        select_one = execute_read_only_query(config, "SELECT 1 AS probe_value", 1, 5)
        top_five = execute_read_only_query(
            config,
            f"SELECT TOP 5 * FROM [{config['schema']}].[plugin_test_users] ORDER BY [id]",
            5,
            5,
        )
        report["checks"]["select_1"] = {
            "ok": select_one["rows"][0]["probe_value"] == 1,
            "row_count": select_one["row_count"],
            "rows": select_one["rows"],
        }
        report["checks"]["top_5"] = {
            "ok": top_five["row_count"] == 5,
            "row_count": top_five["row_count"],
            "rows": top_five["rows"],
        }
        unicode_values = [row["display_name"] for row in top_five["rows"]]
        report["checks"]["unicode_read"] = {
            "ok": "张伟" in unicode_values and "李娜" in unicode_values and "测试用户🚀" in unicode_values,
            "values": unicode_values,
        }
        report["checks"]["schema_qualified_read"] = {
            "ok": top_five["row_count"] == 5,
            "schema": config["schema"],
        }
        report["status"] = "PASS"
        report["exit_code"] = 0
        return report
    except Exception as exc:  # noqa: BLE001
        report["status"] = "FAIL"
        report["exit_code"] = 1
        report["error"] = {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "traceback_tail": traceback.format_exc(limit=3).splitlines()[-6:],
        }
        return report


def load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
