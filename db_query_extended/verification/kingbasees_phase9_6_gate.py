"""Phase 9.6 scoped dialect, adapter, real runtime, and PostgreSQL checks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import ksycopg2  # noqa: E402
import sqlalchemy  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.dialects import registry  # noqa: E402

from utils.adapters import get_database_adapter  # noqa: E402
from utils.database import create_database_engine, execute_read_only_query, verify_database_connection  # noqa: E402
from utils.dialects.kingbasees import (  # noqa: E402
    KingbaseESDialect_ksycopg2,
    parse_server_version,
    register_kingbasees_dialect,
)
from utils.errors import ConnectionFailedError  # noqa: E402
from utils.errors import ReadOnlyViolationError  # noqa: E402
from utils.sql_validator import ReadOnlyValidator  # noqa: E402
from utils.validation import validate_connection_config  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = {
        "kingbasees_phase9_6_dialect_tests.json": run_suite("dialect", dialect_checks()),
        "kingbasees_phase9_6_adapter_tests.json": run_suite("adapter", adapter_checks()),
        "kingbasees_phase9_6_real_adapter_runtime.json": run_suite("real_adapter", real_checks()),
        "kingbasees_phase9_6_postgresql_regression.json": run_suite("postgresql_regression", postgresql_checks()),
    }
    for filename, report in reports.items():
        (output_dir / filename).write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    summary = {name: report["status"] for name, report in reports.items()}
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if all(status == "PASS" for status in summary.values()) else 1


def run_suite(name: str, checks: list[tuple[str, Callable[[], Any]]]) -> dict[str, Any]:
    entries = []
    for check_name, check in checks:
        try:
            detail = check()
            entries.append({"name": check_name, "status": "PASS", "detail": detail})
        except Exception as exc:  # noqa: BLE001 - gate must retain the failing stage
            entries.append({"name": check_name, "status": "FAIL", "error_type": type(exc).__name__, "detail": str(exc)})
    return {
        "phase": "9.6",
        "suite": name,
        "status": "PASS" if all(entry["status"] == "PASS" for entry in entries) else "FAIL",
        "python": sys.version.split()[0],
        "sqlalchemy": sqlalchemy.__version__,
        "ksycopg2": ksycopg2.__version__,
        "date": "2026-07-12",
        "entries": entries,
    }


def dialect_checks() -> list[tuple[str, Callable[[], Any]]]:
    return [
        ("version_parser", check_version_parser),
        ("registry", check_registry),
        ("dbapi", check_dbapi),
        ("isolation", check_isolation),
        ("disconnect", check_disconnect),
        ("namespace_isolation", check_namespace_isolation),
    ]


def adapter_checks() -> list[tuple[str, Callable[[], Any]]]:
    return [
        ("lookup_and_url", check_adapter_url),
        ("connect_and_engine_options", check_adapter_options),
        ("session_configuration", check_session_configuration),
        ("existing_registry", check_existing_registry),
        ("readonly_contract", check_readonly_contract),
    ]


def real_checks() -> list[tuple[str, Callable[[], Any]]]:
    return [
        ("formal_adapter_queries", check_real_adapter),
        ("public_database_utility", check_public_database_utility),
        ("authentication_redaction", check_authentication_redaction),
        ("unreachable_redaction", check_unreachable_redaction),
    ]


def postgresql_checks() -> list[tuple[str, Callable[[], Any]]]:
    return [
        ("postgresql_identity", check_postgresql_identity),
        ("postgresql_real_select_1", check_postgresql_real),
    ]


def check_version_parser() -> dict[str, Any]:
    assert parse_server_version("KingbaseES V009R001C010") == (9, 1, 10)
    assert parse_server_version(" KingbaseES   V009R001C010B0004 ") == (9, 1, 10)
    try:
        parse_server_version("PostgreSQL 12.0")
    except AssertionError:
        pass
    else:
        raise AssertionError("unknown version format was accepted")
    return {"tuple": [9, 1, 10], "meaning": ["major", "release", "component"]}


def check_registry() -> str:
    register_kingbasees_dialect()
    first = registry.load("kingbasees.ksycopg2")
    register_kingbasees_dialect()
    second = registry.load("kingbasees.ksycopg2")
    assert first is KingbaseESDialect_ksycopg2 and second is first
    return "idempotent kingbasees.ksycopg2 registration"


def check_dbapi() -> dict[str, Any]:
    assert KingbaseESDialect_ksycopg2.import_dbapi() is ksycopg2
    assert KingbaseESDialect_ksycopg2.driver == "ksycopg2"
    assert KingbaseESDialect_ksycopg2.default_paramstyle == "pyformat"
    return {"module": ksycopg2.__name__, "paramstyle": ksycopg2.paramstyle}


class FakeCursor:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, statement: str) -> None:
        self.statements.append(statement)

    def close(self) -> None:
        pass


class FakeDBAPIConnection:
    def __init__(self) -> None:
        self.autocommit = False
        self.cursor_value = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.cursor_value


def check_isolation() -> dict[str, Any]:
    dialect = KingbaseESDialect_ksycopg2()
    connection = FakeDBAPIConnection()
    assert "AUTOCOMMIT" in dialect.get_isolation_level_values(connection)
    dialect.set_isolation_level(connection, "AUTOCOMMIT")
    assert connection.autocommit is True
    dialect.set_isolation_level(connection, "READ COMMITTED")
    assert connection.autocommit is False
    assert connection.cursor_value.statements == [
        "SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED",
        "COMMIT",
    ]
    return {"autocommit": True, "read_committed": True}


def check_disconnect() -> str:
    dialect = KingbaseESDialect_ksycopg2(dbapi=ksycopg2)
    assert dialect.is_disconnect(ksycopg2.OperationalError("connection already closed"), SimpleNamespace(closed=0), None)
    assert dialect.is_disconnect(ksycopg2.OperationalError("other"), SimpleNamespace(closed=1), None)
    assert not dialect.is_disconnect(ValueError("connection already closed"), SimpleNamespace(closed=1), None)
    return "ksycopg2 exception and closed-state checks"


def check_namespace_isolation() -> dict[str, Any]:
    before = sys.modules.get("psycopg2")
    register_kingbasees_dialect()
    KingbaseESDialect_ksycopg2.import_dbapi()
    after = sys.modules.get("psycopg2")
    assert after is before
    assert not (PLUGIN_ROOT / "psycopg2").exists()
    return {"psycopg2_before_is_after": True, "fake_package": False}


def sample_config() -> dict[str, Any]:
    return validate_connection_config(
        {
            "database_type": "kingbasees",
            "host": "host.example",
            "port": 54321,
            "database": "kingbase",
            "schema": "public",
            "username": "name@example",
            "password": "p@ss:/word",
            "connection_timeout": 10,
            "ssl_mode": "disable",
        }
    )


def check_adapter_url() -> dict[str, Any]:
    adapter = get_database_adapter("kingbasees")
    url = adapter.build_database_url(sample_config())
    assert adapter.__class__.__name__ == "KingbaseESAdapter"
    assert url.drivername == "kingbasees+ksycopg2"
    assert url.username == "name@example" and url.password == "p@ss:/word"
    assert url.host == "host.example" and url.port == 54321 and url.database == "kingbase"
    assert "p@ss:/word" not in str(url)
    _, connect_args = registry.load("kingbasees.ksycopg2")().create_connect_args(url)
    assert connect_args["user"] == "name@example" and "username" not in connect_args
    return {"drivername": url.drivername, "redacted": str(url), "dbapi_user_key": "user"}


def check_adapter_options() -> dict[str, Any]:
    adapter = get_database_adapter("kingbasees")
    options = adapter.build_engine_options(sample_config())
    assert options == {"pool_pre_ping": True, "connect_args": {"connect_timeout": 10, "sslmode": "disable"}}
    return options


class FakeSAConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def execute(self, statement: Any, params: dict[str, Any]) -> None:
        self.calls.append((str(statement), params))


def check_session_configuration() -> list[dict[str, Any]]:
    connection = FakeSAConnection()
    get_database_adapter("kingbasees").configure_session(connection, sample_config(), 30)
    assert connection.calls[0][1] == {"timeout_value": "30000ms"}
    assert connection.calls[1][1] == {"schema": "public"}
    return [params for _, params in connection.calls]


def check_existing_registry() -> dict[str, str]:
    expected = {
        "mysql": "mysql+pymysql",
        "postgresql": "postgresql+psycopg2",
        "sqlserver": "mssql+pymssql",
    }
    result = {}
    for database_type, drivername in expected.items():
        config = sample_config()
        config["database_type"] = database_type
        result[database_type] = get_database_adapter(database_type).build_database_url(config).drivername
        assert result[database_type] == drivername
    result["dm"] = get_database_adapter("dm").__class__.__name__
    assert result["dm"] == "DMAdapter"
    return result


def check_readonly_contract() -> str:
    validator = ReadOnlyValidator()
    validator.validate("SELECT 1")
    for statement in ("UPDATE t SET x=1", "DROP TABLE t", "SELECT 1; DELETE FROM t"):
        try:
            validator.validate(statement)
        except ReadOnlyViolationError:
            continue
        raise AssertionError(f"unsafe SQL accepted: {statement}")
    return "shared validator unchanged: SELECT allowed; DML, DDL, and multi-statement blocked"


def runtime_config(**overrides: Any) -> dict[str, Any]:
    required = ("KINGBASE_HOST", "KINGBASE_PORT", "KINGBASE_DATABASE", "KINGBASE_USERNAME", "KINGBASE_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"missing environment names: {missing}")
    values = {
        "database_type": "kingbasees",
        "host": os.environ["KINGBASE_HOST"],
        "port": int(os.environ["KINGBASE_PORT"]),
        "database": os.environ["KINGBASE_DATABASE"],
        "schema": os.getenv("KINGBASE_SCHEMA", "public"),
        "username": os.environ["KINGBASE_USERNAME"],
        "password": os.environ["KINGBASE_PASSWORD"],
        "connection_timeout": 10,
        "ssl_mode": "disable",
    }
    values.update(overrides)
    return validate_connection_config(values)


def check_real_adapter() -> dict[str, Any]:
    config = runtime_config()
    adapter = get_database_adapter("kingbasees")
    engine = create_database_engine(config)
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            adapter.configure_session(connection, config, 30)
            values = {
                "version": connection.execute(text("SELECT pg_catalog.version()")).scalar_one(),
                "search_path": connection.execute(text("SHOW search_path")).scalar_one(),
                "select_1": connection.execute(text("SELECT 1")).scalar_one(),
                "unicode_literal": connection.execute(text("SELECT '金仓数据库'")).scalar_one(),
                "unicode_binding": connection.execute(text("SELECT :value"), {"value": "参数绑定"}).scalar_one(),
                "null": connection.execute(text("SELECT CAST(NULL AS INTEGER)")).scalar_one(),
                "numeric": connection.execute(text("SELECT CAST(42.50 AS NUMERIC(10,2))")).scalar_one(),
                "date": connection.execute(text("SELECT CURRENT_DATE")).scalar_one(),
                "timestamp": connection.execute(text("SELECT CURRENT_TIMESTAMP")).scalar_one(),
                "schema_read": connection.execute(
                    text("SELECT datname FROM pg_catalog.pg_database WHERE datname = current_database()")
                ).scalar_one(),
            }
            transaction.rollback()
            assert values["select_1"] == 1
            assert values["unicode_literal"] == "金仓数据库"
            assert values["unicode_binding"] == "参数绑定"
            assert values["null"] is None
            assert values["numeric"] == Decimal("42.50")
            assert isinstance(values["date"], date) and isinstance(values["timestamp"], datetime)
            assert values["schema_read"] == config["database"]
            assert config["schema"] in values["search_path"]
        return {**values, "rollback": True, "connection_closed": True, "engine_disposed": True}
    finally:
        engine.dispose()


def check_public_database_utility() -> dict[str, Any]:
    result = execute_read_only_query(runtime_config(), "SELECT 1 AS value", max_rows=1, timeout=30)
    assert result["columns"] == ["value"]
    assert result["rows"] == [{"value": 1}]
    assert result["row_count"] == 1 and result["truncated"] is False and result["max_rows"] == 1
    return result


def assert_redacted(config: dict[str, Any]) -> str:
    secret = config["password"]
    try:
        verify_database_connection(config)
    except ConnectionFailedError as exc:
        message = str(exc)
        assert secret not in message
        return message
    raise AssertionError("expected connection failure")


def check_authentication_redaction() -> str:
    return assert_redacted(runtime_config(password="phase96-deliberate-wrong-password"))


def check_unreachable_redaction() -> str:
    return assert_redacted(runtime_config(host="host.docker.internal", port=1, connection_timeout=2))


def check_postgresql_identity() -> dict[str, Any]:
    import psycopg2

    before_module = psycopg2
    before_dialect = registry.load("postgresql.psycopg2")
    register_kingbasees_dialect()
    get_database_adapter("kingbasees").build_database_url(sample_config())
    after_module = sys.modules.get("psycopg2")
    after_dialect = registry.load("postgresql.psycopg2")
    postgresql_url = get_database_adapter("postgresql").build_database_url(sample_config())
    assert before_module is after_module
    assert before_dialect is after_dialect
    assert postgresql_url.drivername == "postgresql+psycopg2"
    return {
        "psycopg2_identity_unchanged": True,
        "postgresql_dialect_identity_unchanged": True,
        "postgresql_url": postgresql_url.drivername,
    }


def check_postgresql_real() -> dict[str, Any]:
    required = ("POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DATABASE", "POSTGRES_USERNAME", "POSTGRES_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"missing environment names: {missing}")
    config = validate_connection_config(
        {
            "database_type": "postgresql",
            "host": os.environ["POSTGRES_HOST"],
            "port": int(os.environ["POSTGRES_PORT"]),
            "database": os.environ["POSTGRES_DATABASE"],
            "username": os.environ["POSTGRES_USERNAME"],
            "password": os.environ["POSTGRES_PASSWORD"],
            "connection_timeout": 10,
            "ssl_mode": "disable",
        }
    )
    engine = create_database_engine(config)
    try:
        with engine.connect() as connection:
            value = connection.execute(text("SELECT 1")).scalar_one()
        assert value == 1
        return {"select_1": value, "connection_closed": True, "engine_disposed": True}
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
