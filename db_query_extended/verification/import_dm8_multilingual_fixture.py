"""Import DM8 multilingual fixture with admin/owner credentials from env."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from sqlalchemy import URL, create_engine, text
from sqlalchemy.pool import NullPool

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.adapters.dm import _ensure_dm_runtime  # noqa: E402


REQUIRED_ENV = ("DM_ADMIN_HOST", "DM_ADMIN_PORT", "DM_ADMIN_DATABASE", "DM_ADMIN_USERNAME", "DM_ADMIN_PASSWORD")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    started = perf_counter()
    report: dict[str, Any] = {
        "suite": "dm8_multilingual_fixture_import",
        "generated_at": now(),
        "status": "FAIL",
        "admin_connection": {},
        "sql_file": str(Path(args.sql).resolve()),
        "checks": {},
        "error": None,
    }

    try:
        config = read_admin_env()
        report["admin_connection"] = {
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
        }
        statements = split_sql(Path(args.sql).read_text(encoding="utf-8"))
        engine = admin_engine(config)
        try:
            with engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))

            with engine.connect() as connection:
                row_count = scalar_int(
                    connection,
                    'SELECT COUNT(*) FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"',
                )
                grant_count = scalar_int(
                    connection,
                    """
SELECT COUNT(*)
FROM ALL_TAB_PRIVS
WHERE GRANTEE = 'PLUGIN_TEST_USER'
  AND OWNER = 'PLUGIN_TEST_OWNER'
  AND TABLE_NAME = 'PLUGIN_TEST_MULTILINGUAL'
  AND PRIVILEGE = 'SELECT'
""",
                )
        finally:
            engine.dispose()

        report["checks"] = {
            "statement_count": len(statements),
            "multilingual_row_count": row_count,
            "plugin_test_user_select_grant": grant_count > 0,
        }
        if row_count != 12:
            raise AssertionError(f"Expected MULTILINGUAL_ROW_COUNT=12, got {row_count}")
        if grant_count <= 0:
            raise AssertionError("PLUGIN_TEST_USER SELECT grant was not found.")
        report["status"] = "PASS"
    except Exception as exc:  # noqa: BLE001 - evidence must capture failure
        report["error"] = {"type": exc.__class__.__name__, "message": str(exc)}

    report["duration_ms"] = int((perf_counter() - started) * 1000)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "duration_ms": report["duration_ms"]}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


def read_admin_env() -> dict[str, Any]:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return {
        "host": os.environ["DM_ADMIN_HOST"],
        "port": int(os.environ["DM_ADMIN_PORT"]),
        "database": os.environ["DM_ADMIN_DATABASE"],
        "username": os.environ["DM_ADMIN_USERNAME"],
        "password": os.environ["DM_ADMIN_PASSWORD"],
        "connection_timeout": int(os.getenv("DM_ADMIN_CONNECTION_TIMEOUT", "10")),
    }


def admin_engine(config: dict[str, Any]):
    _ensure_dm_runtime()
    return create_engine(
        URL.create(
            "dm",
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        ),
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={"connection_timeout": config["connection_timeout"], "local_code": 1},
    )


def split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_string = False
    index = 0
    while index < len(sql):
        char = sql[index]
        nxt = sql[index + 1] if index + 1 < len(sql) else ""
        if not in_string and char == "-" and nxt == "-":
            while index < len(sql) and sql[index] not in "\r\n":
                index += 1
            continue
        if char == "'":
            current.append(char)
            if in_string and nxt == "'":
                current.append(nxt)
                index += 2
                continue
            in_string = not in_string
            index += 1
            continue
        if char == ";" and not in_string:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def scalar_int(connection: Any, sql: str) -> int:
    value = connection.execute(text(sql)).scalar()
    return int(value or 0)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
