"""Phase 9.7 Provider/Tool gate in the real plugin-daemon runtime."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

import yaml
from dify_plugin.entities.tool import ToolRuntime
from sqlalchemy import text


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from utils import database as database_utils  # noqa: E402
from utils.database import create_database_engine  # noqa: E402
from utils.errors import DatabaseQueryError  # noqa: E402
from utils.formatter import format_rows  # noqa: E402
from utils.result_formatter import success_response  # noqa: E402
from utils.sql_validator import ReadOnlyValidator  # noqa: E402
from utils.validation import validate_connection_config  # noqa: E402


ROLE = "phase97_readonly"
SCHEMA = "phase97_fixture"
TABLE = f"{SCHEMA}.sample_data"
OUTPUT_KEYS = {
    "success", "database_type", "execution_time_ms", "columns", "rows",
    "row_count", "truncated", "max_rows", "generated_at", "warning", "error",
}


def load_class(path: Path, module_name: str, class_name: str) -> type:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


Provider = load_class(
    PLUGIN_ROOT / "provider" / "db_query_extended.py", "phase97_provider", "DbQueryExtendedProvider"
)
Tool = load_class(PLUGIN_ROOT / "tools" / "db_query_extended.py", "phase97_tool", "DbQueryExtendedTool")


def env_config(prefix: str, database_type: str, *, username_key: str = "USERNAME", password_key: str = "PASSWORD") -> dict[str, Any]:
    return {
        "database_type": database_type,
        "host": required(f"{prefix}_HOST"),
        "port": required(f"{prefix}_PORT"),
        "database": required(f"{prefix}_DATABASE"),
        "username": required(f"{prefix}_{username_key}"),
        "password": required(f"{prefix}_{password_key}"),
        "schema": os.getenv(f"{prefix}_SCHEMA", ""),
        "connection_timeout": os.getenv(f"{prefix}_CONNECTION_TIMEOUT", "5"),
        "ssl_mode": os.getenv(f"{prefix}_SSL_MODE", "disable"),
    }


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def prepare_fixture(admin: dict[str, Any], readonly_password: str) -> None:
    engine = create_database_engine(validate_connection_config(admin))
    try:
        with engine.begin() as connection:
            role_exists = connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :role"), {"role": ROLE}
            ).scalar_one_or_none()
            quoted_password = connection.execute(
                text("SELECT quote_literal(:password)"), {"password": readonly_password}
            ).scalar_one()
            if role_exists is None:
                connection.exec_driver_sql(f"CREATE USER {ROLE} PASSWORD {quoted_password}")
            else:
                connection.exec_driver_sql(f"ALTER USER {ROLE} PASSWORD {quoted_password}")
            connection.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
            connection.exec_driver_sql(
                f"CREATE TABLE IF NOT EXISTS {TABLE} ("
                "id INTEGER PRIMARY KEY, label VARCHAR(80), unicode_text VARCHAR(80), "
                "nullable_text VARCHAR(80), amount NUMERIC(10,2), event_date DATE, event_time TIMESTAMP)"
            )
            connection.exec_driver_sql(f"TRUNCATE TABLE {TABLE}")
            rows = [
                {
                    "id": index,
                    "label": f"row-{index:02d}",
                    "unicode": "金仓只读验证" if index == 1 else f"数据-{index:02d}",
                    "nullable": None if index == 2 else f"value-{index:02d}",
                    "amount": f"{index}.50",
                    "event_date": f"2026-07-{index:02d}",
                    "event_time": f"2026-07-{index:02d} 12:34:56",
                }
                for index in range(1, 13)
            ]
            connection.execute(
                text(
                    f"INSERT INTO {TABLE} "
                    "(id, label, unicode_text, nullable_text, amount, event_date, event_time) "
                    "VALUES (:id, :label, :unicode, :nullable, :amount, :event_date, :event_time)"
                ),
                rows,
            )
            connection.exec_driver_sql(f"REVOKE ALL ON {TABLE} FROM {ROLE}")
            connection.exec_driver_sql(f"REVOKE ALL ON SCHEMA {SCHEMA} FROM {ROLE}")
            connection.exec_driver_sql(f"REVOKE CREATE ON SCHEMA {SCHEMA} FROM PUBLIC")
            connection.exec_driver_sql(f"GRANT USAGE ON SCHEMA {SCHEMA} TO {ROLE}")
            connection.exec_driver_sql(f"GRANT SELECT ON {TABLE} TO {ROLE}")
    finally:
        engine.dispose()


def readonly_config(admin: dict[str, Any], password: str, schema: str = SCHEMA) -> dict[str, Any]:
    config = deepcopy(admin)
    config.update(username=ROLE, password=password, schema=schema)
    return config


def provider_call(config: dict[str, Any]) -> None:
    Provider._validate_credentials(object.__new__(Provider), config)


def tool_call(config: dict[str, Any], sql: str, max_rows: int = 100) -> dict[str, Any]:
    runtime = ToolRuntime(credentials=config, user_id="phase97", session_id="phase97")
    tool = Tool(runtime, None)
    messages = list(tool._invoke({
        "sql": sql, "max_rows": max_rows, "timeout_seconds": 30,
        "readonly": True, "output_format": "json",
    }))
    if len(messages) != 1 or messages[0].type.value != "json":
        raise AssertionError("Tool did not return one JSON message")
    return messages[0].message.json_object


def record(cases: list[dict[str, Any]], name: str, expected: str, action: Callable[[], Any], check: Callable[[Any], bool]) -> Any:
    started = perf_counter()
    try:
        actual = action()
        passed = bool(check(actual))
        cases.append({
            "case": name, "expected": expected, "actual": summarize(actual),
            "status": "PASS" if passed else "FAIL",
            "duration_ms": int((perf_counter() - started) * 1000), "redaction_check": True,
        })
        return actual
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        cases.append({
            "case": name, "expected": expected,
            "actual": {"error_type": exc.__class__.__name__, "message": message},
            "status": "PASS" if check(exc) else "FAIL",
            "duration_ms": int((perf_counter() - started) * 1000), "redaction_check": True,
        })
        return exc


def summarize(value: Any) -> Any:
    if value is None:
        return "completed"
    if isinstance(value, dict):
        return {
            key: value[key] for key in ("success", "database_type", "columns", "rows", "row_count", "truncated", "max_rows", "error")
            if key in value
        }
    return str(value)


def sanitized_failure(secret: str) -> Callable[[Any], bool]:
    def check(value: Any) -> bool:
        message = str(value)
        return isinstance(value, Exception) and secret not in message and "://" not in message
    return check


def provider_suite(admin: dict[str, Any], password: str, dispose_count: dict[str, int]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    base = readonly_config(admin, password)
    for name, schema in (("valid_fixture_schema", SCHEMA), ("valid_public_schema", "public"), ("valid_empty_schema", "")):
        config = deepcopy(base); config["schema"] = schema
        record(cases, name, "credential validation succeeds", lambda c=config: provider_call(c), lambda v: v is None)
    record(cases, "special_character_password", "URL-safe special-character password succeeds", lambda: provider_call(base), lambda v: v is None)
    timeout_config = deepcopy(base); timeout_config["connection_timeout"] = "7"
    record(cases, "explicit_connect_timeout", "explicit timeout succeeds", lambda: provider_call(timeout_config), lambda v: v is None)

    for field in ("host", "port", "database", "username", "password"):
        config = deepcopy(base); config[field] = ""
        record(cases, f"missing_{field}", "validation rejects missing field", lambda c=config: provider_call(c), lambda v: isinstance(v, Exception))

    bad_port = deepcopy(base); bad_port["port"] = "invalid"
    record(cases, "invalid_port", "validation rejects invalid port", lambda: provider_call(bad_port), lambda v: isinstance(v, Exception))
    for name, changes, secret in (
        ("wrong_password", {"password": "phase97-deliberate-wrong-password"}, "phase97-deliberate-wrong-password"),
        ("missing_user", {"username": "phase97_missing_user"}, password),
        ("unreachable", {"port": "1"}, password),
        ("invalid_database", {"database": "phase97_missing_database"}, password),
        ("invalid_schema", {"schema": "phase97_missing_schema"}, password),
        ("unsupported_database_type", {"database_type": "kingbase"}, password),
    ):
        config = deepcopy(base); config.update(changes)
        record(cases, name, "safe validation failure", lambda c=config: provider_call(c), sanitized_failure(secret))
    return suite("provider_validation", cases, {"engine_dispose_calls": dispose_count["count"]})


def tool_suite(admin: dict[str, Any], password: str, dispose_count: dict[str, int]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    config = readonly_config(admin, password)
    queries = (
        ("select_1", "SELECT 1 AS probe", 100, lambda r: r["rows"] == [{"probe": 1}]),
        ("fixture_rows", f"SELECT id, label FROM {TABLE} ORDER BY id", 100, lambda r: r["row_count"] == 12),
        ("unicode", f"SELECT unicode_text FROM {TABLE} WHERE id = 1", 100, lambda r: r["rows"][0]["unicode_text"] == "金仓只读验证"),
        ("null_numeric_date_time", f"SELECT nullable_text, amount, event_date, event_time FROM {TABLE} WHERE id = 2", 100, lambda r: r["rows"][0]["nullable_text"] is None and r["rows"][0]["amount"] == "2.50" and r["rows"][0]["event_date"] == "2026-07-02" and r["rows"][0]["event_time"].startswith("2026-07-02")),
        ("schema_qualified", f"SELECT COUNT(*) AS total FROM {TABLE}", 100, lambda r: r["rows"] == [{"total": 12}]),
        ("default_max_rows", f"SELECT id FROM {TABLE} ORDER BY id", 100, lambda r: r["max_rows"] == 100 and not r["truncated"]),
        ("custom_max_rows_truncation", f"SELECT id FROM {TABLE} ORDER BY id", 5, lambda r: r["row_count"] == 5 and r["truncated"] and r["max_rows"] == 5),
        ("empty_result", f"SELECT id FROM {TABLE} WHERE id < 0", 100, lambda r: r["rows"] == [] and r["row_count"] == 0),
        ("alias_column", f"SELECT label AS fixture_label FROM {TABLE} WHERE id = 1", 100, lambda r: r["columns"] == ["fixture_label"]),
        ("aggregate", f"SELECT SUM(amount) AS total_amount FROM {TABLE}", 100, lambda r: r["rows"][0]["total_amount"] == "84.00"),
        ("order_by", f"SELECT id FROM {TABLE} ORDER BY id DESC", 3, lambda r: [x["id"] for x in r["rows"]] == [12, 11, 10]),
    )
    for name, sql, max_rows, predicate in queries:
        record(cases, name, "formal Tool returns verified content", lambda s=sql, m=max_rows: tool_call(config, s, m), lambda r, p=predicate: isinstance(r, dict) and r.get("success") is True and set(r) == OUTPUT_KEYS and p(r))

    bad = deepcopy(config); bad["password"] = "phase97-tool-wrong-password"
    record(cases, "bad_authentication_redaction", "safe Tool error", lambda: tool_call(bad, "SELECT 1"), lambda r: isinstance(r, dict) and not r["success"] and "phase97-tool-wrong-password" not in json.dumps(r) and "://" not in json.dumps(r))
    unreachable = deepcopy(config); unreachable["port"] = "1"
    record(cases, "unreachable_endpoint_redaction", "safe Tool error", lambda: tool_call(unreachable, "SELECT 1"), lambda r: isinstance(r, dict) and not r["success"] and password not in json.dumps(r) and "://" not in json.dumps(r))
    return suite("tool_validation", cases, {"engine_dispose_calls": dispose_count["count"]})


def readonly_suite(admin: dict[str, Any], password: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    validator = ReadOnlyValidator()
    blocked = {
        "insert": f"INSERT INTO {TABLE} (id) VALUES (99)",
        "update": f"UPDATE {TABLE} SET label = 'x' WHERE id = 1",
        "delete": f"DELETE FROM {TABLE} WHERE id = 1",
        "create": "CREATE TABLE phase97_fixture.forbidden(id int)",
        "alter": f"ALTER TABLE {TABLE} ADD COLUMN forbidden int",
        "drop": f"DROP TABLE {TABLE}",
        "truncate": f"TRUNCATE TABLE {TABLE}",
        "multi_statement": "SELECT 1; SELECT 2",
        "comment_bypass": f"SELECT 1 /* */; DELETE FROM {TABLE}",
        "cte_write": f"WITH changed AS (DELETE FROM {TABLE} RETURNING id) SELECT * FROM changed",
        "procedure_call": "CALL phase97_fixture.missing_procedure()",
    }
    for name, sql in blocked.items():
        record(cases, name, "common validator rejects SQL", lambda s=sql: validator.validate(s), lambda v: isinstance(v, DatabaseQueryError))

    config = validate_connection_config(readonly_config(admin, password))
    def direct_write() -> None:
        engine = create_database_engine(config)
        try:
            with engine.begin() as connection:
                connection.execute(text(f"INSERT INTO {TABLE} (id, label) VALUES (99, 'forbidden')"))
        finally:
            engine.dispose()
    record(cases, "database_permission_insert", "database rejects read-only user write", direct_write, lambda v: isinstance(v, Exception))
    def direct_create() -> None:
        engine = create_database_engine(config)
        try:
            with engine.begin() as connection:
                connection.execute(text(f"CREATE TABLE {SCHEMA}.forbidden_table (id INTEGER)"))
        finally:
            engine.dispose()
    record(cases, "database_permission_create", "database rejects read-only user DDL", direct_create, lambda v: isinstance(v, Exception))
    return suite("readonly_account", cases, {"role": ROLE, "schema": SCHEMA, "password_recorded": False})


def regression_suite(postgres: dict[str, Any], provider_yaml: Path) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    schema = yaml.safe_load(provider_yaml.read_text(encoding="utf-8"))
    options = [item["value"] for item in schema["credentials_for_provider"]["database_type"]["options"]]
    record(cases, "provider_options", "mysql/postgresql/dm preserved; sqlserver remains optional; kingbasees present", lambda: options, lambda v: v == ["mysql", "postgresql", "dm", "sqlserver", "kingbasees"])
    record(cases, "postgresql_provider_real", "real Provider validation succeeds", lambda: provider_call(postgres), lambda v: v is None)
    record(cases, "postgresql_tool_real", "real Tool SELECT 1 succeeds", lambda: tool_call(postgres, "SELECT 1 AS probe"), lambda r: isinstance(r, dict) and r.get("rows") == [{"probe": 1}])
    validator = ReadOnlyValidator()
    record(cases, "common_validator", "SELECT accepted and DML rejected", lambda: (validator.validate("SELECT 1"), capture_error(lambda: validator.validate("DELETE FROM x"))), lambda v: isinstance(v[1], DatabaseQueryError))
    formatted = format_rows(["amount", "when"], [("12.30", "2026-07-12")], max_rows=1)
    record(cases, "common_formatter", "stable formatter contract", lambda: formatted, lambda v: set(v) == {"columns", "rows", "row_count", "truncated", "max_rows"})
    return suite("targeted_regression", cases)


def capture_error(action: Callable[[], Any]) -> Exception | None:
    try:
        action()
    except Exception as exc:  # noqa: BLE001
        return exc
    return None


def suite(name: str, cases: list[dict[str, Any]], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    output = {
        "suite": name, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if cases and all(case["status"] == "PASS" for case in cases) else "FAIL",
        "cases": cases,
        "summary": {"pass": sum(c["status"] == "PASS" for c in cases), "fail": sum(c["status"] == "FAIL" for c in cases)},
    }
    if extra:
        output.update(extra)
    return output


def install_dispose_counter() -> dict[str, int]:
    counter = {"count": 0}
    original = database_utils.create_database_engine
    def tracked(config: dict[str, Any]):
        engine = original(config)
        dispose = engine.dispose
        def counted_dispose(*args: Any, **kwargs: Any):
            counter["count"] += 1
            return dispose(*args, **kwargs)
        engine.dispose = counted_dispose
        return engine
    database_utils.create_database_engine = tracked
    return counter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--log-dir", required=True)
    args = parser.parse_args()
    output_dir, log_dir = Path(args.output_dir), Path(args.log_dir)
    output_dir.mkdir(parents=True, exist_ok=True); log_dir.mkdir(parents=True, exist_ok=True)

    admin = env_config("KINGBASE", "kingbasees")
    password = required("KINGBASE_READONLY_PASSWORD")
    postgres = validate_connection_config(env_config("POSTGRES", "postgresql"))
    prepare_fixture(admin, password)
    dispose_count = install_dispose_counter()
    reports = {
        "kingbasees_phase9_7_provider_validation.json": provider_suite(admin, password, dispose_count),
        "kingbasees_phase9_7_tool_validation.json": tool_suite(admin, password, dispose_count),
        "kingbasees_phase9_7_readonly_account.json": readonly_suite(admin, password),
        "kingbasees_phase9_7_targeted_regression.json": regression_suite(postgres, PLUGIN_ROOT / "provider" / "db_query_extended.yaml"),
    }
    for filename, report in reports.items():
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        (output_dir / filename).write_text(payload, encoding="utf-8")
        (log_dir / filename.replace(".json", ".log")).write_text(payload, encoding="utf-8")
    runtime = {
        "runtime": "dify-plugin_daemon-1", "python": sys.version.split()[0],
        "sqlalchemy": __import__("sqlalchemy").__version__,
        "ksycopg2": getattr(__import__("ksycopg2"), "__version__", "2.9.1"),
        "dependency_boundary": "CANDIDATE_RUNTIME_DEPENDENCY_OVERLAY / NOT_INSTALLED_PLUGIN_DEPENDENCY_CLOSURE",
        "password_recorded": False,
    }
    (log_dir / "phase9_7_runtime_loading.log").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")
    statuses = {name: report["status"] for name, report in reports.items()}
    print(json.dumps(statuses, ensure_ascii=False))
    return 0 if all(status == "PASS" for status in statuses.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
