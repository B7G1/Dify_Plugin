"""Offline KingbaseES contract verification without a database connection."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest.mock import patch

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.adapters import get_database_adapter  # noqa: E402
from utils.drivers.kingbasees import require_kingbase_runtime  # noqa: E402
from utils.errors import ConnectionFailedError, ReadOnlyViolationError  # noqa: E402
from utils.sql_validator import ReadOnlyValidator  # noqa: E402
from utils.validation import validate_connection_config  # noqa: E402


CREDENTIALS = {
    "database_type": "kingbasees",
    "host": "127.0.0.1",
    "port": "54321",
    "database": "plugin_test",
    "schema": "plugin_test",
    "username": "plugin_readonly",
    "password": "not-logged",
    "connection_timeout": "10",
    "ssl_mode": "disable",
}


class FakeConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> None:
        self.calls.append((str(statement), params or {}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    entries: list[dict[str, Any]] = []
    run(entries, "validation", verify_validation)
    run(entries, "adapter_discovery", verify_adapter_discovery)
    run(entries, "url_contract", verify_url)
    run(entries, "connect_args", verify_connect_args)
    run(entries, "engine_options", verify_engine_options)
    run(entries, "session_timeout", verify_session_timeout)
    run(entries, "session_search_path", verify_session_search_path)
    run(entries, "session_without_schema", verify_session_without_schema)
    run(entries, "existing_adapter_contracts", verify_existing_adapters)
    run(entries, "shared_sql_security", verify_shared_security)
    run(entries, "provider_schema", verify_provider_schema)
    run_runtime_gate(entries)

    summary = {"mock_pass": 0, "fail": 0, "blocked": 0}
    for item in entries:
        summary[item["status"].lower()] += 1
    report = {
        "suite": "kingbasees_mock",
        "evidence_level": "MOCK_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
        "summary": summary,
        "real_database_status": "BLOCKED",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if summary["fail"] else 0


def run(entries: list[dict[str, Any]], case: str, check: Any) -> None:
    started = perf_counter()
    try:
        message = check()
        entries.append(entry(case, "MOCK_PASS", started, message))
    except Exception as exc:  # noqa: BLE001 - report uniform mock failures
        entries.append(entry(case, "FAIL", started, f"{type(exc).__name__}: {exc}"))


def verify_validation() -> str:
    config = validate_connection_config(CREDENTIALS)
    assert config["database_type"] == "kingbasees"
    assert config["port"] == 54321
    assert config["database"] == "plugin_test"
    assert config["schema"] == "plugin_test"
    assert config["username"] == "plugin_readonly"
    assert "password" in config
    return "KingbaseES credentials normalize additively with port 54321 and explicit schema."


def verify_adapter_discovery() -> str:
    adapter = get_database_adapter("kingbasees")
    assert adapter.__class__.__name__ == "KingbaseESAdapter"
    return "Dynamic adapter discovery resolves KingbaseESAdapter."


def verify_url() -> str:
    config = validate_connection_config(CREDENTIALS)
    url = get_database_adapter("kingbasees").build_database_url(config)
    assert url.drivername == "kingbase+ksycopg2"
    assert url.host == "127.0.0.1" and url.port == 54321
    assert url.database == "plugin_test" and url.username == "plugin_readonly"
    assert "not-logged" not in str(url)
    return "URL uses kingbase+ksycopg2 and SQLAlchemy redacts the password."


def verify_connect_args() -> str:
    config = validate_connection_config(CREDENTIALS)
    args = get_database_adapter("kingbasees").build_connect_args(config)
    assert args == {"connect_timeout": 10, "sslmode": "disable"}
    return "Connection timeout and SSL mode remain isolated connect_args."


def verify_engine_options() -> str:
    config = validate_connection_config(CREDENTIALS)
    adapter = get_database_adapter("kingbasees")
    with patch("utils.adapters.kingbasees.require_kingbase_runtime", return_value={"mock": True}):
        options = adapter.build_engine_options(config)
    assert options == {
        "pool_pre_ping": True,
        "connect_args": {"connect_timeout": 10, "sslmode": "disable"},
    }
    return "Engine options preserve the base short-lived engine contract after the runtime gate."


def verify_session_timeout() -> str:
    connection = FakeConnection()
    config = validate_connection_config(CREDENTIALS)
    get_database_adapter("kingbasees").configure_session(connection, config, 30)
    assert connection.calls[0][1] == {"timeout_value": "30000ms"}
    return "Statement timeout is parameterized and transaction-local by design."


def verify_session_search_path() -> str:
    connection = FakeConnection()
    config = validate_connection_config(CREDENTIALS)
    get_database_adapter("kingbasees").configure_session(connection, config, 30)
    assert len(connection.calls) == 2
    assert connection.calls[1][1] == {"schema": "plugin_test"}
    return "search_path uses a bound parameter; schema text is not concatenated into SQL."


def verify_session_without_schema() -> str:
    credentials = dict(CREDENTIALS)
    credentials["schema"] = ""
    connection = FakeConnection()
    config = validate_connection_config(credentials)
    get_database_adapter("kingbasees").configure_session(connection, config, 30)
    assert len(connection.calls) == 1
    return "Empty schema leaves the server search_path unchanged."


def verify_existing_adapters() -> str:
    cases = {
        "mysql": (3306, "mysql+pymysql"),
        "postgresql": (5432, "postgresql+psycopg2"),
        "dm": (5236, "dm"),
    }
    for database_type, (port, driver) in cases.items():
        credentials = {
            "database_type": database_type,
            "host": "127.0.0.1",
            "database": "PLUGIN_TEST_OWNER" if database_type == "dm" else "plugin_test",
            "username": "user",
            "password": "not-logged",
            "ssl_mode": "disable",
        }
        config = validate_connection_config(credentials)
        assert config["port"] == port
        assert get_database_adapter(database_type).build_database_url(config).drivername == driver
    return "MySQL, PostgreSQL, and DM8 default ports and URL drivers are unchanged."


def verify_shared_security() -> str:
    validator = ReadOnlyValidator()
    validator.validate("SELECT 1")
    for sql in (
        "DROP TABLE plugin_test_users",
        "UPDATE plugin_test_users SET username='x'",
        "SELECT 1; DELETE FROM plugin_test_users",
        "WITH x AS (DELETE FROM plugin_test_users RETURNING *) SELECT * FROM x",
    ):
        try:
            validator.validate(sql)
        except ReadOnlyViolationError:
            continue
        raise AssertionError(f"unsafe SQL accepted: {sql}")
    return "The unchanged shared validator accepts SELECT and blocks representative unsafe SQL."


def verify_provider_schema() -> str:
    provider = (PLUGIN_ROOT / "provider" / "db_query_extended.yaml").read_text(encoding="utf-8")
    assert "value: kingbasees" in provider
    assert "KingbaseES (Preview)" in provider
    assert "Schema (optional)" in provider
    return "Provider declares KingbaseES as Preview and exposes optional schema without changing Tool inputs."


def run_runtime_gate(entries: list[dict[str, Any]]) -> None:
    started = perf_counter()
    try:
        require_kingbase_runtime()
    except ConnectionFailedError as exc:
        entries.append(entry("real_driver_runtime", "BLOCKED", started, str(exc)))
        return
    except Exception as exc:  # noqa: BLE001
        entries.append(entry("real_driver_runtime", "FAIL", started, f"{type(exc).__name__}: {exc}"))
        return
    entries.append(
        entry(
            "real_driver_runtime",
            "BLOCKED",
            started,
            "Driver imports, but a real KingbaseES connection is still required before runtime PASS.",
        )
    )


def entry(case: str, status: str, started: float, message: str) -> dict[str, Any]:
    return {
        "case": case,
        "status": status,
        "execution_time_ms": int((perf_counter() - started) * 1000),
        "message": message,
    }


if __name__ == "__main__":
    raise SystemExit(main())

