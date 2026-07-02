"""Independent Provider, Tool, and Dify Workflow verification suites."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib import error, request

from sqlalchemy import text

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.database import (  # noqa: E402
    build_connect_args,
    build_database_url,
    build_engine_options,
    create_database_engine,
    execute_read_only_query,
)
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
UNICODE_TEXT = "\u4e2d\u6587\u6d4b\u8bd5"
UNICODE_SQL_PARAMETER = 'SELECT :unicode_text AS "UNICODE_TEXT" FROM DUAL'
UNICODE_SQL_LITERAL = f'SELECT \'{UNICODE_TEXT}\' AS "UNICODE_TEXT" FROM DUAL'

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
    "dm": {
        "database_type": "dm",
        "host": os.getenv("DM_HOST", "127.0.0.1"),
        "port": int(os.getenv("DM_PORT", "5236")),
        "database": os.getenv("DM_DATABASE", "DMSERVER"),
        "username": os.getenv("DM_USERNAME", "PLUGIN_TEST_USER"),
        "password": os.getenv("DM_PASSWORD", "PluginRead_2026!"),
        "connection_timeout": int(os.getenv("DM_CONNECTION_TIMEOUT", "10")),
        "schema": os.getenv("DM_SCHEMA", "PLUGIN_TEST_OWNER"),
        "ssl_mode": "disable",
    },
}

TOOL_QUERIES = [
    ("select_1", "SELECT 1 AS ok", 100, lambda r: r["row_count"] == 1),
    ("limit_5", "SELECT * FROM plugin_test_users LIMIT 5", 100, lambda r: r["row_count"] == 5),
    ("count", "SELECT COUNT(*) AS total FROM plugin_test_users", 100, lambda r: r["row_count"] == 1),
    ("where", "SELECT * FROM plugin_test_orders WHERE status='completed'", 100, lambda r: r["row_count"] == 14),
    (
        "join",
        "SELECT u.username, o.amount FROM plugin_test_users u JOIN plugin_test_orders o ON u.id=o.user_id LIMIT 10",
        100,
        lambda r: r["row_count"] == 10,
    ),
    ("max_rows", "SELECT * FROM plugin_test_users ORDER BY id", 3, lambda r: r["row_count"] == 3 and r["truncated"] is True),
]

BLOCKED_SQL = [
    ("drop", "DROP TABLE plugin_test_users"),
    ("update", "UPDATE plugin_test_users SET username='x'"),
    ("delete", "DELETE FROM plugin_test_users"),
    ("alter", "ALTER TABLE plugin_test_users ADD COLUMN x int"),
    ("create", "CREATE TABLE x(id int)"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=("provider", "tool", "workflow"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    runners = {"provider": run_provider, "tool": run_tool, "workflow": run_workflow}
    report = runners[args.suite]()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if report["summary"]["fail"] else 0


def run_provider() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    expected = {
        "mysql": ("mysql+pymysql", {"connect_timeout": 10}),
        "postgresql": ("postgresql+psycopg2", {"connect_timeout": 10, "sslmode": "disable"}),
        "dm": ("dm", {"connection_timeout": 10, "local_code": 1, "schema": "PLUGIN_TEST_OWNER"}),
    }
    for name, credentials in DATABASES.items():
        started = perf_counter()
        try:
            config = validate_connection_config(credentials)
            result = execute_read_only_query(config, "SELECT 1 AS ok", 1, 30)
            response = success_response(name, result)
            assert_schema(response)
            assert response["row_count"] == 1
            entries.append(entry(name, "provider_credential", "PASS", started, "Credential normalization and SELECT 1 passed."))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry(name, "provider_credential", "FAIL", started, str(exc)))

        started = perf_counter()
        try:
            config = validate_connection_config(credentials)
            driver, connect_args = expected[name]
            assert build_database_url(config).drivername == driver
            assert build_connect_args(config) == connect_args
            assert build_engine_options(config) == {"pool_pre_ping": True, "connect_args": connect_args}
            entries.append(entry(name, "adapter_contract", "PASS", started, "URL, connect_args, and engine options preserved."))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry(name, "adapter_contract", "FAIL", started, str(exc)))
    return report("provider", entries)


def run_tool() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for database_type, credentials in DATABASES.items():
        config = validate_connection_config(credentials)
        for case_name, sql, max_rows, predicate in TOOL_QUERIES:
            started = perf_counter()
            try:
                params = validate_tool_parameters({"sql": sql, "max_rows": max_rows, "timeout_seconds": 30, "readonly": True})
                result = execute_read_only_query(config, params["sql"], params["max_rows"], params["timeout_seconds"])
                response = success_response(database_type, result)
                assert_schema(response)
                assert predicate(response)
                entries.append(entry(database_type, case_name, "PASS", started, compact_result(response)))
            except Exception as exc:  # noqa: BLE001
                entries.append(entry(database_type, case_name, "FAIL", started, str(exc)))

    started = perf_counter()
    try:
        entries.append(entry("dm", "unicode_bind", "PASS", started, verify_dm_unicode_acceptance()))
    except Exception as exc:  # noqa: BLE001
        entries.append(entry("dm", "unicode_bind", "FAIL", started, str(exc)))

    validator = ReadOnlyValidator()
    for case_name, sql in BLOCKED_SQL:
        started = perf_counter()
        try:
            validator.validate(sql)
            entries.append(entry("validator", case_name, "FAIL", started, "Unsafe SQL was accepted."))
        except DatabaseQueryError as exc:
            response = error_response(exc)
            status = "PASS" if response["success"] is False and response["error"] else "FAIL"
            entries.append(entry("validator", case_name, status, started, response["error"]["message"]))

    formatter_cases = [
        ("decimal", ["value"], [(Decimal("12.30"),)], 100),
        ("date_time", ["dt", "d", "t"], [(datetime(2026, 6, 28, 1, 2, 3), date(2026, 6, 28), time(1, 2, 3))], 100),
        ("truncated", ["id"], [(1,), (2,), (3,)], 2),
    ]
    for case_name, columns, rows, max_rows in formatter_cases:
        started = perf_counter()
        try:
            output = format_rows(columns, rows, max_rows=max_rows)
            assert set(output) == {"columns", "rows", "row_count", "truncated", "max_rows"}
            entries.append(entry("formatter", case_name, "PASS", started, json.dumps(output, ensure_ascii=False)))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry("formatter", case_name, "FAIL", started, str(exc)))
    return report("tool", entries)


def run_workflow() -> dict[str, Any]:
    workflow_targets = configured_workflow_targets()
    if not workflow_targets:
        return report(
            "workflow",
            [
                entry(
                    "dify_workflow",
                    "configuration",
                    "FAIL",
                    perf_counter(),
                    "DIFY_WORKFLOW_API_URL and DIFY_WORKFLOW_API_KEY are required; Workflow verification never skips.",
                )
            ],
        )

    entries: list[dict[str, Any]] = []
    for workflow_target in workflow_targets:
        entries.extend(run_workflow_target(workflow_target))

    result = report("workflow", entries)
    result["targets"] = [
        {
            "name": target["name"],
            "database_type": target["database_type"],
            "endpoint": target["api_url"],
            "credential": target["credential_env"],
        }
        for target in workflow_targets
    ]
    return result


def invoke_workflow(api_url: str, api_key: str, sql: str, max_rows: int, workflow_user: str) -> dict[str, Any]:
    payload = {
        "inputs": {"sql": sql, "max_rows": max_rows},
        "response_mode": "blocking",
        "user": workflow_user,
    }
    req = request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as response:  # noqa: S310 - operator-configured Dify endpoint
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Workflow API HTTP {exc.code}: {detail[:1000]}") from exc


def workflow_result(body: dict[str, Any]) -> dict[str, Any]:
    outputs = body.get("data", {}).get("outputs", {})
    raw = outputs.get("result")
    if not isinstance(raw, list) or not raw or not isinstance(raw[0], dict):
        raise AssertionError(f"Workflow output result is missing or malformed: {json.dumps(outputs, ensure_ascii=False)}")
    return raw[0]


def workflow_excerpt(body: dict[str, Any], result: dict[str, Any]) -> str:
    excerpt = {
        "workflow_run_id": body.get("workflow_run_id"),
        "status": body.get("data", {}).get("status"),
        "total_steps": body.get("data", {}).get("total_steps"),
        "success": result.get("success", True),
        "row_count": result.get("row_count"),
        "truncated": result.get("truncated"),
        "error_type": (result.get("error") or {}).get("type"),
    }
    return json.dumps(excerpt, ensure_ascii=False)


def configured_workflow_targets() -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    api_url = os.getenv("DIFY_WORKFLOW_API_URL")
    api_key = os.getenv("DIFY_WORKFLOW_API_KEY")
    if api_url and api_key:
        targets.append(
            {
                "name": os.getenv("DIFY_WORKFLOW_TARGET_NAME", "dify_workflow"),
                "database_type": os.getenv("DIFY_WORKFLOW_DATABASE_TYPE", "mysql"),
                "api_url": api_url,
                "api_key": api_key,
                "credential_env": "DIFY_WORKFLOW_API_KEY",
                "user": os.getenv("DIFY_WORKFLOW_USER", "phase5.5-verifier"),
            }
        )

    dm_api_url = os.getenv("DIFY_DM_WORKFLOW_API_URL")
    dm_api_key = os.getenv("DIFY_DM_WORKFLOW_API_KEY")
    if dm_api_url and dm_api_key:
        targets.append(
            {
                "name": os.getenv("DIFY_DM_WORKFLOW_TARGET_NAME", "dify_workflow_dm"),
                "database_type": "dm",
                "api_url": dm_api_url,
                "api_key": dm_api_key,
                "credential_env": "DIFY_DM_WORKFLOW_API_KEY",
                "user": os.getenv("DIFY_DM_WORKFLOW_USER", "phase7.1-dm-verifier"),
            }
        )
    return targets


def run_workflow_target(target: dict[str, str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    target_name = target["name"]
    api_url = target["api_url"]
    api_key = target["api_key"]
    workflow_user = target["user"]

    for case_name, sql, max_rows, predicate in TOOL_QUERIES:
        started = perf_counter()
        try:
            body = invoke_workflow(api_url, api_key, sql, max_rows, workflow_user)
            result = workflow_result(body)
            assert body["data"]["status"] == "succeeded"
            assert result.get("success", True) is not False
            assert predicate(result)
            entries.append(entry(target_name, case_name, "PASS", started, workflow_excerpt(body, result)))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry(target_name, case_name, "FAIL", started, str(exc)))

    if target["database_type"] == "dm":
        started = perf_counter()
        try:
            body = invoke_workflow(api_url, api_key, UNICODE_SQL_LITERAL, 1, workflow_user)
            result = workflow_result(body)
            assert body["data"]["status"] == "succeeded"
            assert result["rows"][0]["UNICODE_TEXT"] == UNICODE_TEXT
            entries.append(entry(target_name, "unicode_utf8", "PASS", started, workflow_excerpt(body, result)))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry(target_name, "unicode_utf8", "FAIL", started, str(exc)))

    for case_name, sql in BLOCKED_SQL:
        started = perf_counter()
        try:
            body = invoke_workflow(api_url, api_key, sql, 100, workflow_user)
            result = workflow_result(body)
            blocked = result.get("success") is False and result.get("error", {}).get("type") == "ReadOnlyViolationError"
            assert blocked, f"Expected ReadOnlyViolationError, got {json.dumps(result, ensure_ascii=False)}"
            entries.append(entry(target_name, case_name, "PASS", started, workflow_excerpt(body, result)))
        except Exception as exc:  # noqa: BLE001
            entries.append(entry(target_name, case_name, "FAIL", started, str(exc)))
    return entries


def verify_dm_unicode_acceptance() -> str:
    config = validate_connection_config(DATABASES["dm"])
    messages = [verify_dm_dmpython_binding(config), verify_dm_sqlalchemy_binding(config)]
    return " | ".join(messages)


def verify_dm_dmpython_binding(config: dict[str, Any]) -> str:
    build_database_url(config)
    import dmPython

    connection = dmPython.connect(
        user=config["username"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
        schema=config["schema"],
        local_code=1,
    )
    try:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT ? AS "UNICODE_TEXT" FROM DUAL', [UNICODE_TEXT])
            value = cursor.fetchall()[0][0]
        finally:
            cursor.close()
    finally:
        connection.close()

    assert value == UNICODE_TEXT, repr(value)
    return "dmPython parameter binding preserved Unicode."


def verify_dm_sqlalchemy_binding(config: dict[str, Any]) -> str:
    engine = create_database_engine(config)
    try:
        with engine.connect() as connection:
            result = connection.execute(text(UNICODE_SQL_PARAMETER), {"unicode_text": UNICODE_TEXT})
            payload = success_response("dm", format_rows(list(result.keys()), result.fetchall(), max_rows=1))
    finally:
        engine.dispose()

    assert_schema(payload)
    assert payload["rows"][0]["UNICODE_TEXT"] == UNICODE_TEXT, json.dumps(payload, ensure_ascii=False)
    return "SQLAlchemy and Tool JSON preserved Unicode."


def assert_schema(response: dict[str, Any]) -> None:
    missing = SCHEMA_KEYS.difference(response)
    if missing:
        raise AssertionError(f"Response schema missing keys: {sorted(missing)}")


def compact_result(response: dict[str, Any]) -> str:
    return json.dumps({"row_count": response["row_count"], "truncated": response["truncated"], "max_rows": response["max_rows"]})


def entry(target: str, case: str, status: str, started: float, message: str) -> dict[str, Any]:
    return {
        "target": target,
        "case": case,
        "status": status,
        "execution_time_ms": int((perf_counter() - started) * 1000),
        "message": message,
    }


def report(suite: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {"pass": 0, "fail": 0, "skip": 0}
    for item in entries:
        summary[item["status"].lower()] += 1
    return {
        "suite": suite,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
        "summary": summary,
    }


if __name__ == "__main__":
    raise SystemExit(main())
