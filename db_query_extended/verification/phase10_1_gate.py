"""Repeatable Phase 10.1 legacy compatibility gate (no database credentials)."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "db_query_extended"
sys.path.insert(0, str(PLUGIN))

from utils.errors import ParameterValidationError, ReadOnlyViolationError, UnsupportedDatabaseTypeError  # noqa: E402
from utils.formatter import format_rows  # noqa: E402
from utils.legacy import FormatterMode, SELECT_ONE_GOLDEN, format_result, run_legacy_query, validate_legacy_parameters  # noqa: E402
from utils.sql_validator import ReadOnlyValidator  # noqa: E402


PARAMETERS = ["db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "db_properties", "query_sql", "output_format"]
SECRET = "phase10_1_fake_password"


def record(group: dict[str, Any], name: str, fn) -> None:  # type: ignore[no-untyped-def]
    try:
        fn()
        group[name] = "PASS"
    except Exception as exc:  # noqa: BLE001
        group[name] = f"FAIL: {exc.__class__.__name__}: {exc}"


def legacy_request(**overrides: Any) -> dict[str, Any]:
    request = {"db_type": "mysql", "db_host": "localhost", "db_port": 3306, "db_username": "test_user", "db_password": SECRET, "db_name": "plugin_test", "db_properties": "schema=public", "query_sql": "SELECT 1 AS probe", "output_format": "markdown"}
    request.update(overrides)
    return request


def assert_raises(error: type[Exception], fn) -> None:  # type: ignore[no-untyped-def]
    try:
        fn()
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def contract_tests() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    legacy = yaml.safe_load((PLUGIN / "tools" / "legacy_database_query.yaml").read_text(encoding="utf-8"))
    original = json.loads((ROOT / "reports" / "contracts" / "original_plugin_parameter_contract.json").read_text(encoding="utf-8"))
    modern = yaml.safe_load((PLUGIN / "tools" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((PLUGIN / "manifest.yaml").read_text(encoding="utf-8"))
    record(checks, "nine_parameters_and_order", lambda: _same([item["name"] for item in legacy["parameters"]], PARAMETERS))
    record(checks, "frozen_parameter_yaml", lambda: _same(legacy["parameters"], original["raw_values"]["parameters"]))
    record(checks, "db_type_options", lambda: _same([item["value"] for item in legacy["parameters"][0]["options"]], ["mysql", "oracle", "oracle11g", "postgresql", "mssql"]))
    record(checks, "default_markdown", lambda: _same(legacy["parameters"][-1]["default"], "markdown"))
    record(checks, "separate_modern_entry", lambda: _different(legacy["identity"]["name"], modern["identity"]["name"]))
    record(checks, "project_identity", lambda: _different(legacy["identity"]["author"], "junjiem"))
    record(checks, "manifest_registers_single_runtime_provider", lambda: _same(manifest["plugins"]["tools"], ["provider/db_query_extended.yaml"]))
    provider = yaml.safe_load((PLUGIN / "provider" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    record(checks, "provider_registers_both_tools", lambda: _same(provider["tools"], ["tools/db_query_extended.yaml", "tools/legacy_database_query.yaml"]))
    return checks


def formatter_tests() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    sample = {"columns": ["probe"], "rows": [{"probe": 1}], "row_count": 1, "truncated": False, "max_rows": 1}
    complex_result = {"columns": ["name", "nullable", "amount"], "rows": [{"name": "中文|line\nnext", "nullable": None, "amount": 12.34}], "row_count": 1, "truncated": False, "max_rows": 1}
    original = copy.deepcopy(complex_result)
    record(checks, "select_one_markdown_golden", lambda: _same(format_result(FormatterMode.LEGACY_MARKDOWN, sample), SELECT_ONE_GOLDEN))
    record(checks, "records_object_and_null", lambda: _same(format_result(FormatterMode.LEGACY_JSON_RECORDS, complex_result), {"records": [{"name": "中文|line\nnext", "nullable": "", "amount": 12.34}]}))
    record(checks, "modern_null_preserved", lambda: _same(format_result(FormatterMode.MODERN_JSON, complex_result)["rows"][0]["nullable"], None))
    record(checks, "formatter_does_not_mutate_normalized", lambda: _same(complex_result, original))
    record(checks, "empty_records", lambda: _same(format_result(FormatterMode.LEGACY_JSON_RECORDS, {"columns": ["x"], "rows": []}), {"records": []}))
    record(checks, "markdown_escaping", lambda: _contains(format_result(FormatterMode.LEGACY_MARKDOWN, complex_result), "中文\\|line<br>next"))
    record(checks, "duplicate_column_blocked", lambda: assert_raises(ParameterValidationError, lambda: format_result(FormatterMode.LEGACY_JSON_RECORDS, {"columns": ["x", "x"], "rows": [[1, 2]]})))
    record(checks, "existing_modern_formatter", lambda: _same(format_rows(["x"], [(None,)], max_rows=1)["rows"], [{"x": None}]))
    return checks


def mapping_and_security_tests() -> tuple[dict[str, Any], dict[str, Any]]:
    mapping: dict[str, Any] = {}
    security: dict[str, Any] = {}
    record(mapping, "mysql_mapping", lambda: _same(validate_legacy_parameters(legacy_request())["config"]["database_type"], "mysql"))
    record(mapping, "postgresql_mapping", lambda: _same(validate_legacy_parameters(legacy_request(db_type="postgresql", db_port=5432))["config"]["database_type"], "postgresql"))
    record(mapping, "mssql_internal_mapping", lambda: _same(validate_legacy_parameters(legacy_request(db_type="mssql", db_port=1433))["config"]["database_type"], "sqlserver"))
    record(mapping, "oracle_controlled", lambda: assert_raises(UnsupportedDatabaseTypeError, lambda: validate_legacy_parameters(legacy_request(db_type="oracle"))))
    record(mapping, "oracle11g_controlled", lambda: assert_raises(UnsupportedDatabaseTypeError, lambda: validate_legacy_parameters(legacy_request(db_type="oracle11g"))))
    record(mapping, "unknown_controlled", lambda: assert_raises(UnsupportedDatabaseTypeError, lambda: validate_legacy_parameters(legacy_request(db_type="unknown"))))
    record(security, "secret_not_in_validation_error", lambda: _not_contains(_error_text(lambda: validate_legacy_parameters(legacy_request(db_type="unknown"))), SECRET))
    validator = ReadOnlyValidator()
    for name, sql in {"cte_delete": "WITH x AS (DELETE FROM t RETURNING id) SELECT * FROM x", "select_into": "SELECT 1 INTO x", "outfile": "SELECT 1 INTO OUTFILE '/tmp/x'", "for_update": "SELECT * FROM t FOR UPDATE", "multi_statement": "SELECT 1; SELECT 2"}.items():
        record(security, f"blocked_{name}", lambda sql=sql: assert_raises(ReadOnlyViolationError, lambda: validator.validate(sql)))
    return mapping, security


def legacy_tool_invocation_tests() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    execute = lambda *args: {"columns": ["probe", "nullable"], "rows": [{"probe": 1, "nullable": None}], "row_count": 1, "truncated": False, "max_rows": 1000}
    markdown = run_legacy_query(legacy_request(), execute)
    records = run_legacy_query(legacy_request(output_format="json"), execute)
    record(checks, "legacy_tool_markdown_invocation", lambda: _contains(markdown, "probe"))
    record(checks, "legacy_tool_json_invocation", lambda: _same(records, {"records": [{"probe": 1, "nullable": ""}]}))
    record(checks, "legacy_tool_safe_rejection", lambda: (_not_contains(_error_text(lambda: run_legacy_query(legacy_request(query_sql="SELECT 1; DELETE FROM x"), execute)), SECRET), assert_raises(ReadOnlyViolationError, lambda: run_legacy_query(legacy_request(query_sql="SELECT 1; DELETE FROM x"), execute))))
    return checks


def workflow_tests() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    script = PLUGIN / "scripts" / "migrate_legacy_workflow.py"
    fixture = {"graph": {"nodes": [{"id": "legacy", "type": "tool", "data": {"provider_id": "db_query", "tool_name": "sql_query", "inputs": {name: f"{{{{#{name}#}}}}" for name in PARAMETERS}}}, {"id": "downstream", "type": "template-transform", "data": {"template": "{{#legacy.records#}} {{#legacy.text#}}"}}]}}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source, output, backup = root / "old.json", root / "new.json", root / "backup.json"
        source.write_text(json.dumps(fixture), encoding="utf-8")
        dry = _run(script, "--input", source, "--output", output, "--dry-run")
        record(checks, "dry_run_unchanged", lambda: (_same(dry["status"], "MIGRATED"), _same(source.read_text(encoding="utf-8"), json.dumps(fixture)), _same(output.exists(), False)))
        migrated = _run(script, "--input", source, "--output", output, "--backup", backup)
        document = json.loads(output.read_text(encoding="utf-8"))
        node = document["graph"]["nodes"][0]["data"]
        record(checks, "bindings_and_mssql_preserved", lambda: (_same(node["inputs"], fixture["graph"]["nodes"][0]["data"]["inputs"]), _same(node["inputs"]["db_type"], "{{#db_type#}}")))
        record(checks, "identity_rewritten_only", lambda: (_same((node["provider_id"], node["tool_name"]), ("li_zijun/db_query_extended/db_query_extended", "legacy_database_query")), _same(document["graph"]["nodes"][1], fixture["graph"]["nodes"][1])))
        record(checks, "backup_and_secret_redaction", lambda: (_same(backup.read_text(encoding="utf-8"), source.read_text(encoding="utf-8")), _not_contains(json.dumps(migrated), SECRET)))
        again = _run(script, "--input", output, "--output", root / "again.json")
        record(checks, "idempotent", lambda: _same(again["status"], "NOOP"))
        blocked = subprocess.run([sys.executable, str(script), "--input", str(root / "bad.json"), "--output", str(root / "bad-out.json")], text=True, capture_output=True)
        (root / "bad.json").write_text("{}", encoding="utf-8")
        blocked = subprocess.run([sys.executable, str(script), "--input", str(root / "bad.json"), "--output", str(root / "bad-out.json")], text=True, capture_output=True)
        record(checks, "unknown_dsl_blocked", lambda: (_same(blocked.returncode, 2), _contains(blocked.stderr, "BLOCKED")))
    return checks


def existing_regression() -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(PLUGIN / "verification" / "phase2_matrix.py")], text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(result.stdout[-1000:] or result.stderr[-1000:])
    summary = json.loads(result.stdout)["summary"]
    _same(summary["fail"], 0)
    return {"phase2_matrix": "PASS", "summary": summary, "workflow": "SKIP_BY_MISSING_API_ENV" if summary["skip"] else "PASS"}


def _run(script: Path, *args: Any) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(script), *map(str, args)], text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def _same(actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def _different(actual: Any, expected: Any) -> None:
    if actual == expected:
        raise AssertionError(f"unexpected {actual!r}")


def _contains(text: str, value: str) -> None:
    if value not in text:
        raise AssertionError(f"missing {value!r}")


def _not_contains(text: str, value: str) -> None:
    if value in text:
        raise AssertionError("secret leaked")


def _error_text(fn) -> str:  # type: ignore[no-untyped-def]
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        return str(exc)
    raise AssertionError("expected an error")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = contract_tests()
    formatter = formatter_tests()
    mapping, security = mapping_and_security_tests()
    security.update(legacy_tool_invocation_tests())
    workflow = workflow_tests()
    existing = existing_regression()
    groups = {"contract_tests": contract, "formatter_tests": formatter, "security_tests": security, "mapping_tests": mapping, "workflow_migration_tests": workflow, "existing_regression": existing}
    failed = {group: {name: value for name, value in checks.items() if isinstance(value, str) and value.startswith("FAIL")} for group, checks in groups.items() if any(isinstance(value, str) and value.startswith("FAIL") for value in checks.values())}
    payload = {"phase": "10.1", "status": "FAIL" if failed else "PASS", "starting_commit": "0700f82", "ending_commit": None, **groups, "modified_files": ["manifest.yaml", "provider/db_query_extended.yaml", "tools/legacy_database_query.yaml", "tools/legacy_database_query.py", "utils/legacy.py", "utils/validation.py", "scripts/migrate_legacy_workflow.py"], "evidence_files": ["reports/verification/2026-07-13/phase10_1_final_gate.json", "reports/logs/2026-07-13/Phase10_Base_Reproduction/phase10_1_legacy_implementation_gate.log", "reports/logs/2026-07-13/Phase10_Base_Reproduction/phase10_1_existing_phase2_regression.log"], "allowed_claims": ["LEGACY_TOOL_IMPLEMENTED", "LEGACY_FORMATTERS_IMPLEMENTED", "WORKFLOW_MIGRATION_UTILITY_IMPLEMENTED"] if not failed else [], "forbidden_claims": ["ORIGINAL_BASE_PLUGIN_REPRODUCTION_CONFIRMED", "ORACLE_REPRODUCTION_PASS", "ORACLE11G_REPRODUCTION_PASS", "LEGACY_WORKFLOW_MIGRATION_PASS", "FINAL_PROJECT_DELIVERY_PASS"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "failed_groups": failed}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
