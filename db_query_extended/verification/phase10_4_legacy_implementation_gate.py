#!/usr/bin/env python3
"""Credential-free implementation gate for Phase 10.4 Legacy behavior."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "db_query_extended"
sys.path.insert(0, str(PLUGIN))

from utils.errors import ParameterValidationError, ReadOnlyViolationError, UnsupportedDatabaseTypeError  # noqa: E402
from utils.legacy import FormatterMode, format_result, parse_legacy_properties, run_legacy_query, validate_legacy_parameters  # noqa: E402
from utils.result_formatter import success_response  # noqa: E402
from utils.sql_validator import LegacySingleSelectValidator  # noqa: E402


LEGACY_PARAMETERS = ["db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "db_properties", "query_sql", "output_format"]
MODERN_PARAMETERS = ["sql", "max_rows", "timeout_seconds", "readonly", "output_format"]


def expect_error(error: type[Exception], fn: Callable[[], Any]) -> None:
    try:
        fn()
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def check(name: str, fn: Callable[[], Any]) -> dict[str, str]:
    try:
        fn()
        return {"name": name, "status": "PASS"}
    except Exception as exc:  # noqa: BLE001
        return {"name": name, "status": "FAIL", "detail": f"{exc.__class__.__name__}: {exc}"}


def legacy_request(**overrides: Any) -> dict[str, Any]:
    request = {
        "db_type": "mysql", "db_host": "localhost", "db_port": 3306,
        "db_username": "test_user", "db_password": "<redacted>",
        "db_name": "plugin_test", "db_properties": "", "query_sql": "SELECT 1 AS probe",
        "output_format": "json",
    }
    request.update(overrides)
    return request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validator = LegacySingleSelectValidator()
    execute = lambda *_: {"columns": ["probe"], "rows": [{"probe": 1}], "row_count": 1, "truncated": False, "max_rows": 1000}

    legacy_yaml = yaml.safe_load((PLUGIN / "tools" / "legacy_database_query.yaml").read_text(encoding="utf-8"))
    modern_yaml = yaml.safe_load((PLUGIN / "tools" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    provider_yaml = yaml.safe_load((PLUGIN / "provider" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    dsl = yaml.safe_load((ROOT / "reports" / "assets" / "2026-07-15" / "Phase10_Base_Reproduction" / "migrated_legacy_json_v0_1_3.yml").read_text(encoding="utf-8"))
    legacy_tool_source = (PLUGIN / "tools" / "legacy_database_query.py").read_text(encoding="utf-8")

    checks = [
        check("legacy_select", lambda: validator.validate("SELECT 1")),
        check("legacy_leading_comment_select", lambda: validator.validate("-- comment\nSELECT 1")),
        check("legacy_terminal_semicolon", lambda: validator.validate("SELECT 1;")),
        check("legacy_two_selects_blocked", lambda: expect_error(ReadOnlyViolationError, lambda: validator.validate("SELECT 1; SELECT 2"))),
        check("legacy_select_delete_blocked", lambda: expect_error(ReadOnlyViolationError, lambda: validator.validate("SELECT 1; DELETE FROM t"))),
        check("legacy_select_into_blocked", lambda: expect_error(ReadOnlyViolationError, lambda: validator.validate("SELECT 1 INTO t"))),
        check("legacy_with_blocked", lambda: expect_error(ReadOnlyViolationError, lambda: validator.validate("WITH x AS (SELECT 1) SELECT * FROM x"))),
        check("legacy_non_select_blocked", lambda: expect_error(ReadOnlyViolationError, lambda: validator.validate("DELETE FROM t"))),
        check("properties_empty", lambda: _equal(parse_legacy_properties(""), {})),
        check("properties_allowed", lambda: _equal(parse_legacy_properties("schema=public&charset=utf8&ssl_mode=disable"), {"schema": "public", "charset": "utf8", "ssl_mode": "disable"})),
        check("properties_unknown_blocked", lambda: expect_error(ParameterValidationError, lambda: parse_legacy_properties("connect_args=x"))),
        check("properties_duplicate_blocked", lambda: expect_error(ParameterValidationError, lambda: parse_legacy_properties("schema=a&schema=b"))),
        check("properties_malformed_blocked", lambda: expect_error(ParameterValidationError, lambda: parse_legacy_properties("schema"))),
        check("properties_connection_overrides_blocked", _connection_override_check),
        check("mssql_to_sqlserver", lambda: _equal(validate_legacy_parameters(legacy_request(db_type="mssql", db_port=1433))["config"]["database_type"], "sqlserver")),
        check("oracle_controlled_unsupported", lambda: expect_error(UnsupportedDatabaseTypeError, lambda: validate_legacy_parameters(legacy_request(db_type="oracle")))),
        check("oracle11g_controlled_unsupported", lambda: expect_error(UnsupportedDatabaseTypeError, lambda: validate_legacy_parameters(legacy_request(db_type="oracle11g")))),
        check("legacy_markdown", lambda: _contains(run_legacy_query(legacy_request(output_format="markdown"), execute), "|   probe |")),
        check("legacy_json_records_only", lambda: _equal(run_legacy_query(legacy_request(), execute), {"records": [{"probe": 1}]})),
        check("legacy_json_empty", lambda: _equal(format_result(FormatterMode.LEGACY_JSON_RECORDS, {"columns": ["probe"], "rows": []}), {"records": []})),
        check("legacy_error_uses_exception_path", lambda: _legacy_error_source_check(legacy_tool_source)),
        check("modern_tool_schema_unchanged", lambda: _equal([item["name"] for item in modern_yaml["parameters"]], MODERN_PARAMETERS)),
        check("modern_provider_schema_unchanged", lambda: _equal([item for item in provider_yaml["credentials_for_provider"]], ["database_type", "host", "port", "username", "password", "database", "schema", "connection_timeout", "ssl_mode"])),
        check("modern_envelope_unchanged", _modern_envelope_check),
        check("legacy_schema_unchanged", lambda: _equal([item["name"] for item in legacy_yaml["parameters"]], LEGACY_PARAMETERS)),
        check("json_dsl_persistence_unchanged", lambda: _json_dsl_check(dsl)),
    ]
    failures = [item for item in checks if item["status"] == "FAIL"]
    payload = {
        "suite": "phase10_4_legacy_implementation_gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "scope": "credential-free unit/static verification; no database, Dify installation, Workflow, or API key was invoked",
        "checks": checks,
        "allowed_conclusions": ["PHASE_10_4_LEGACY_POLICY_IMPLEMENTED", "PHASE_10_4_PROPERTIES_POLICY_IMPLEMENTED", "PHASE_10_4_LEGACY_SANITIZED_EXCEPTION_CODE_PATH_IMPLEMENTED"] if not failures else [],
        "not_proven": ["DIFY_PLUGIN_INVOKE_ERROR_RUNTIME_PASS", "ORACLE_RUNTIME_PASS", "ORACLE11G_RUNTIME_PASS", "DM8_NEW_RUNTIME_PASS", "KINGBASEES_NEW_RUNTIME_PASS", "FINAL_PROJECT_DELIVERY_PASS"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "failures": len(failures)}, ensure_ascii=False))
    return 1 if failures else 0


def _equal(actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def _contains(value: Any, expected: str) -> None:
    if not isinstance(value, str) or expected not in value:
        raise AssertionError(f"missing {expected!r}")


def _legacy_error_source_check(source: str) -> None:
    if 'create_json_message({"error"' in source:
        raise AssertionError("Legacy Tool still creates a structured error message")
    if "raise DatabaseQueryError(\"The query request could not be completed.\") from exc" not in source:
        raise AssertionError("Legacy Tool does not sanitize unexpected exceptions")
    if "except DatabaseQueryError as exc:" not in source or "            raise\n" not in source:
        raise AssertionError("Legacy Tool does not preserve the known exception path")


def _connection_override_check() -> None:
    for key in ("host", "port", "username", "password", "database", "driver"):
        expect_error(ParameterValidationError, lambda key=key: parse_legacy_properties(f"{key}=x"))


def _modern_envelope_check() -> None:
    response = success_response("mysql", {"columns": ["probe"], "rows": [{"probe": 1}], "row_count": 1, "truncated": False, "max_rows": 100})
    required = {"success", "database_type", "execution_time_ms", "columns", "rows", "row_count", "truncated", "max_rows", "generated_at", "warning", "error"}
    _equal(set(response), required)
    _equal(response["rows"], [{"probe": 1}])


def _json_dsl_check(dsl: dict[str, Any]) -> None:
    tool = next(node["data"] for node in dsl["workflow"]["graph"]["nodes"] if node["data"]["type"] == "tool")
    _equal(tool["tool_parameters"]["output_format"], {"type": "constant", "value": "json"})


if __name__ == "__main__":
    raise SystemExit(main())
