"""Phase 2 verification matrix for db_query_extended.

This script verifies the plugin core without mocking database execution:

- Provider-style credential normalization
- Read-only SQL safety validation
- MySQL and PostgreSQL query execution
- Uniform JSON result schema

Workflow API verification is intentionally environment-driven.  If
``DIFY_WORKFLOW_API_URL`` and ``DIFY_WORKFLOW_API_KEY`` are present, the script
will invoke the real workflow endpoint.  Otherwise it reports that part as
SKIP instead of pretending it passed.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib import request

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.database import build_connect_args, build_database_url, build_engine_options, execute_read_only_query  # noqa: E402
from utils.errors import DatabaseQueryError  # noqa: E402
from utils.formatter import format_rows  # noqa: E402
from utils.result_formatter import error_response, success_response  # noqa: E402
from utils.sql_validator import ReadOnlyValidator  # noqa: E402
from utils.validation import validate_connection_config, validate_tool_parameters  # noqa: E402


SCHEMA_KEYS = {
    "success",
    "database_type",
    "execution_time_ms",
    "columns",
    "rows",
    "row_count",
    "truncated",
    "max_rows",
    "generated_at",
    "warning",
    "error",
}

DATABASES = {
    "mysql": {
        "database_type": "mysql",
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "database": os.getenv("MYSQL_DATABASE", "plugin_test"),
        "username": os.getenv("MYSQL_USERNAME", "plugin_test_user"),
        "password": os.getenv("MYSQL_PASSWORD", "plugin_test_password"),
        "connection_timeout": int(os.getenv("MYSQL_CONNECTION_TIMEOUT", "10")),
        "ssl_mode": "disable",
    },
    "postgresql": {
        "database_type": "postgresql",
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DATABASE", "plugin_test"),
        "username": os.getenv("POSTGRES_USERNAME", "plugin_test_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "plugin_test_password"),
        "connection_timeout": int(os.getenv("POSTGRES_CONNECTION_TIMEOUT", "10")),
        "ssl_mode": os.getenv("POSTGRES_SSL_MODE", "disable"),
    },
}

QUERY_MATRIX = [
    ("LIMIT", "SELECT * FROM plugin_test_users LIMIT 5", 1),
    ("ORDER BY", "SELECT username, created_at FROM plugin_test_users ORDER BY created_at DESC LIMIT 3", 1),
    ("GROUP BY", "SELECT department, COUNT(*) AS total FROM plugin_test_users GROUP BY department ORDER BY total DESC", 1),
    ("JOIN", "SELECT u.username, o.product_name, o.amount FROM plugin_test_users u JOIN plugin_test_orders o ON u.id=o.user_id ORDER BY o.id LIMIT 5", 1),
    ("DISTINCT", "SELECT DISTINCT status FROM plugin_test_orders ORDER BY status", 1),
    ("COUNT", "SELECT COUNT(*) AS total FROM plugin_test_users", 1),
    ("LIKE", "SELECT username FROM plugin_test_users WHERE username LIKE '%a%' ORDER BY id", 1),
    ("BETWEEN", "SELECT id, amount FROM plugin_test_orders WHERE amount BETWEEN 100 AND 500 ORDER BY amount LIMIT 5", 1),
    ("NULL", "SELECT id, username FROM plugin_test_users WHERE email IS NULL ORDER BY id", 1),
    ("DATE", "SELECT id, username FROM plugin_test_users WHERE created_at >= '2025-01-01' ORDER BY id LIMIT 3", 1),
    ("TIMESTAMP", "SELECT id, event_type, created_at FROM plugin_test_logs ORDER BY created_at DESC LIMIT 3", 1),
    ("Chinese", "SELECT id, username FROM plugin_test_users WHERE username = '\u5f20\u4f1f'", 1),
    ("Emoji", "SELECT 'hello \U0001f680' AS emoji_text", 1),
    ("Long Text", "SELECT 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' AS long_text", 1),
]

ALLOWED_SQL = [
    "SELECT * FROM plugin_test_users",
    "select username from plugin_test_users where department is null",
    "WITH active_users AS (SELECT * FROM plugin_test_users) SELECT * FROM active_users",
    "SELECT 'DROP TABLE users' AS text_value",
    "/* comment */ SELECT * FROM plugin_test_users -- trailing comment",
]

BLOCKED_SQL = [
    "",
    "   ",
    "INSERT INTO plugin_test_users(id) VALUES (99)",
    "UpDaTe plugin_test_users SET username='x'",
    "DELETE FROM plugin_test_users",
    "DROP TABLE plugin_test_users",
    "ALTER TABLE plugin_test_users ADD COLUMN x int",
    "CREATE TABLE x(id int)",
    "TRUNCATE TABLE plugin_test_users",
    "CALL do_something()",
    "EXEC do_something",
    "MERGE INTO x USING y ON x.id=y.id WHEN MATCHED THEN UPDATE SET id=1",
    "COPY plugin_test_users TO STDOUT",
    "LOAD DATA INFILE 'x' INTO TABLE plugin_test_users",
    "REPLACE INTO plugin_test_users(id) VALUES (99)",
    "GRANT SELECT ON plugin_test_users TO somebody",
    "REVOKE SELECT ON plugin_test_users FROM somebody",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT s1",
    "SET search_path TO public",
    "USE plugin_test",
    "SELECT * FROM plugin_test_users; DROP TABLE plugin_test_users",
    "SELECT * FROM plugin_test_users;",
    "/* SELECT */ UPDATE plugin_test_users SET username='x'",
    "WITH deleted AS (DELETE FROM plugin_test_users RETURNING *) SELECT * FROM deleted",
    "EXPLAIN SELECT * FROM plugin_test_users",
    "EXPLAIN ANALYZE SELECT * FROM plugin_test_users",
    "SELECT * FROM plugin_test_users -- hidden\n; DROP TABLE plugin_test_users",
    "SELECT * FROM plugin_test_users # hidden\n; DELETE FROM plugin_test_users",
    "SELECT * FROM plugin_test_users /* hidden */; UPDATE plugin_test_users SET username='x'",
    "SELECT * FROM plugin_test_users " + ("-" * 100_001),
]


def main() -> int:
    report: dict[str, Any] = {
        "provider": [],
        "adapter_contract": [],
        "sql_security": [],
        "formatter": [],
        "database_matrix": [],
        "workflow": [],
        "summary": {"pass": 0, "fail": 0, "skip": 0},
    }

    run_provider_checks(report)
    run_adapter_contract(report)
    run_sql_security_matrix(report)
    run_formatter_matrix(report)
    run_database_matrix(report)
    run_workflow_check(report)

    for section, entries in report.items():
        if section == "summary":
            continue
        for entry in entries:
            report["summary"][entry["status"].lower()] += 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["summary"]["fail"] else 0


def run_provider_checks(report: dict[str, Any]) -> None:
    for name, credentials in DATABASES.items():
        started = perf_counter()
        try:
            normalized = validate_connection_config(credentials)
            result = execute_read_only_query(normalized, "SELECT 1 AS ok", 1, 30)
            response = success_response(name, result)
            _assert_schema(response)
            status = "PASS" if response["row_count"] == 1 else "FAIL"
            message = "Provider credentials normalized and SELECT 1 succeeded."
        except Exception as exc:  # noqa: BLE001 - report uniform verification failure
            status = "FAIL"
            message = str(exc)
        report["provider"].append(_entry(name, "provider_connection", status, started, message))


def run_adapter_contract(report: dict[str, Any]) -> None:
    expected = {
        "mysql": ("mysql+pymysql", {"connect_timeout": 10}),
        "postgresql": ("postgresql+psycopg2", {"connect_timeout": 10, "sslmode": "disable"}),
    }
    for name, credentials in DATABASES.items():
        started = perf_counter()
        try:
            config = validate_connection_config(credentials)
            url = build_database_url(config)
            connect_args = build_connect_args(config)
            engine_options = build_engine_options(config)
            expected_driver, expected_args = expected[name]
            assert url.drivername == expected_driver
            assert connect_args == expected_args
            assert engine_options == {"pool_pre_ping": True, "connect_args": expected_args}
            status = "PASS"
            message = "Adapter preserved URL, connect_args, and engine option contracts."
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            message = str(exc)
        report["adapter_contract"].append(_entry(name, "adapter_contract", status, started, message))


def run_sql_security_matrix(report: dict[str, Any]) -> None:
    validator = ReadOnlyValidator()
    for sql in ALLOWED_SQL:
        started = perf_counter()
        try:
            validator.validate(sql)
            status = "PASS"
            message = "Allowed read-only SQL accepted."
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            message = f"Allowed SQL rejected: {exc}"
        report["sql_security"].append(_entry("validator", _short_sql(sql), status, started, message))

    for sql in BLOCKED_SQL:
        started = perf_counter()
        try:
            validator.validate(sql)
            status = "FAIL"
            message = "Blocked SQL was accepted."
        except DatabaseQueryError as exc:
            response = error_response(exc)
            status = "PASS" if response["success"] is False and response["error"] else "FAIL"
            message = response["error"]["message"]
        report["sql_security"].append(_entry("validator", _short_sql(sql), status, started, message))


def run_formatter_matrix(report: dict[str, Any]) -> None:
    cases = [
        ("tuple", ["id", "name"], [(1, "alice")], lambda output: output["rows"][0]["id"] == 1),
        ("dict", ["id", "amount"], [{"id": 1, "amount": Decimal("12.30")}], lambda output: output["rows"][0]["amount"] == "12.30"),
        ("none", ["value"], [(None,)], lambda output: output["rows"][0]["value"] is None),
        (
            "date_time_bytes_bool",
            ["dt", "d", "t", "raw", "flag"],
            [(datetime(2026, 6, 26, 1, 2, 3), date(2026, 6, 26), time(1, 2, 3), b"abc", True)],
            lambda output: output["rows"][0]["raw"] == "abc" and output["rows"][0]["flag"] is True,
        ),
        ("fallback_object", ["value"], [(object(),)], lambda output: isinstance(output["rows"][0]["value"], str)),
        ("truncated", ["id"], [(1,), (2,), (3,)], lambda output: output["truncated"] is True and output["row_count"] == 2),
    ]
    for case_name, columns, rows, predicate in cases:
        started = perf_counter()
        try:
            max_rows = 2 if case_name == "truncated" else 100
            output = format_rows(columns, rows, max_rows=max_rows)
            status = "PASS" if set(output) == {"columns", "rows", "row_count", "truncated", "max_rows"} and predicate(output) else "FAIL"
            message = json.dumps(output, ensure_ascii=False, default=str)
        except Exception as exc:  # noqa: BLE001
            status = "FAIL"
            message = str(exc)
        report["formatter"].append(_entry("formatter", case_name, status, started, message))


def run_database_matrix(report: dict[str, Any]) -> None:
    for database_type, credentials in DATABASES.items():
        normalized = validate_connection_config(credentials)
        for case_name, sql, minimum_rows in QUERY_MATRIX:
            started = perf_counter()
            try:
                params = validate_tool_parameters({
                    "sql": sql,
                    "max_rows": 100,
                    "timeout_seconds": 30,
                    "readonly": True,
                    "output_format": "json",
                })
                result = execute_read_only_query(normalized, params["sql"], params["max_rows"], params["timeout_seconds"])
                response = success_response(database_type, result)
                _assert_schema(response)
                status = "PASS" if response["row_count"] >= minimum_rows else "FAIL"
                message = f"rows={response['row_count']} execution_time_ms={response['execution_time_ms']}"
            except Exception as exc:  # noqa: BLE001
                status = "FAIL"
                message = str(exc)
            report["database_matrix"].append(_entry(database_type, case_name, status, started, message))


def run_workflow_check(report: dict[str, Any]) -> None:
    api_url = os.getenv("DIFY_WORKFLOW_API_URL")
    api_key = os.getenv("DIFY_WORKFLOW_API_KEY")
    if not api_url or not api_key:
        report["workflow"].append({
            "target": "dify_workflow",
            "case": "workflow_api_call",
            "status": "SKIP",
            "execution_time_ms": 0,
            "message": "Set DIFY_WORKFLOW_API_URL and DIFY_WORKFLOW_API_KEY to run real Workflow invocation.",
        })
        return

    started = perf_counter()
    payload = {
        "inputs": {
            "sql": "SELECT * FROM plugin_test_users LIMIT 5",
            "database_type": os.getenv("DIFY_WORKFLOW_DATABASE_TYPE", "mysql"),
        },
        "response_mode": "blocking",
        "user": os.getenv("DIFY_WORKFLOW_USER", "phase2-verifier"),
    }
    req = request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as response:  # noqa: S310 - user-supplied local/API endpoint
            body = response.read().decode("utf-8", errors="replace")
        status = "PASS"
        message = body[:2000]
    except Exception as exc:  # noqa: BLE001
        status = "FAIL"
        message = str(exc)
    report["workflow"].append(_entry("dify_workflow", "workflow_api_call", status, started, message))


def _assert_schema(response: dict[str, Any]) -> None:
    missing = SCHEMA_KEYS.difference(response)
    if missing:
        raise AssertionError(f"Response schema missing keys: {sorted(missing)}")


def _entry(target: str, case: str, status: str, started: float, message: str) -> dict[str, Any]:
    return {
        "target": target,
        "case": case,
        "status": status,
        "execution_time_ms": int((perf_counter() - started) * 1000),
        "message": message,
    }


def _short_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    if not normalized:
        return "<empty>"
    return normalized[:96] + ("..." if len(normalized) > 96 else "")


if __name__ == "__main__":
    raise SystemExit(main())
