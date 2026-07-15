#!/usr/bin/env python3
"""Static gate for the frozen Legacy/Modern architecture boundary."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "db_query_extended"
LEGACY_PARAMETERS = [
    "db_type", "db_host", "db_port", "db_username", "db_password",
    "db_name", "db_properties", "query_sql", "output_format",
]
LEGACY_DATABASES = ["mysql", "oracle", "oracle11g", "postgresql", "mssql"]
MODERN_PARAMETERS = ["sql", "max_rows", "timeout_seconds", "readonly", "output_format"]


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(name: str, condition: bool, detail: str) -> dict[str, str]:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    legacy_yaml = load_yaml(PLUGIN / "tools" / "legacy_database_query.yaml")
    modern_yaml = load_yaml(PLUGIN / "tools" / "db_query_extended.yaml")
    provider_yaml = load_yaml(PLUGIN / "provider" / "db_query_extended.yaml")
    dsl = load_yaml(ROOT / "reports" / "assets" / "2026-07-15" / "Phase10_Base_Reproduction" / "migrated_legacy_json_v0_1_3.yml")
    legacy_source = (PLUGIN / "utils" / "legacy.py").read_text(encoding="utf-8")
    legacy_tool_source = (PLUGIN / "tools" / "legacy_database_query.py").read_text(encoding="utf-8")
    modern_tool_source = (PLUGIN / "tools" / "db_query_extended.py").read_text(encoding="utf-8")
    graph_nodes = dsl["workflow"]["graph"]["nodes"]
    json_tool = next(node["data"] for node in graph_nodes if node["data"]["type"] == "tool")

    checks = [
        check("two_distinct_tool_entries", provider_yaml["tools"] == ["tools/db_query_extended.yaml", "tools/legacy_database_query.yaml"], "one provider exposes two named Tool contracts"),
        check("legacy_identity", legacy_yaml["identity"]["name"] == "legacy_database_query", "Legacy technical Tool name is frozen"),
        check("modern_identity", modern_yaml["identity"]["name"] == "db_query_extended", "Modern technical Tool name is frozen"),
        check("legacy_nine_parameter_order", [item["name"] for item in legacy_yaml["parameters"]] == LEGACY_PARAMETERS, "Legacy UI remains the original nine-field order"),
        check("legacy_five_database_values", [item["value"] for item in legacy_yaml["parameters"][0]["options"]] == LEGACY_DATABASES, "Legacy declarations preserve five original database values"),
        check("modern_parameter_contract", [item["name"] for item in modern_yaml["parameters"]] == MODERN_PARAMETERS, "Modern Tool remains credential-backed and separate"),
        check("mssql_to_sqlserver", '"mssql": "sqlserver"' in legacy_source, "Legacy mssql maps to the internal sqlserver adapter key"),
        check("oracle_controlled_unsupported", 'database_type in {"oracle", "oracle11g"}' in legacy_source and "UnsupportedDatabaseTypeError" in legacy_source, "Oracle declarations are explicit controlled unsupported paths"),
        check("shared_execution_core", "run_legacy_query(tool_parameters, execute_read_only_query)" in legacy_tool_source and "execute_read_only_query(" in modern_tool_source, "both paths call the same execution core after their own mapping"),
        check("output_contract_isolation", 'return {"records": records}' in legacy_source and "success_response(database_type, result)" in modern_tool_source, "Legacy records and modern structured envelopes are independent"),
        check("legacy_properties_boundary", "parse_qsl" in legacy_source and 'properties.get("schema")' in legacy_source and 'properties.get("charset")' in legacy_source and 'properties.get("ssl_mode")' in legacy_source, "Legacy properties are parsed before only mapped fields enter internal config"),
        check("json_dsl_execution_persistence", json_tool["tool_parameters"].get("output_format", {}).get("value") == "json", "passed JSON DSL persists json under tool_parameters"),
    ]
    failures = [item for item in checks if item["status"] == "FAIL"]
    payload = {
        "suite": "phase10_3_legacy_architecture_gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "scope": "static architecture freeze only; no database, installed plugin, or Workflow was invoked",
        "checks": checks,
        "frozen_routes": {
            "legacy": "legacy_database_query -> legacy mapper -> legacy SQL policy -> shared execution core -> legacy formatter",
            "modern": "db_query_extended -> provider credential mapper -> modern read-only policy -> shared execution core -> modern structured formatter",
            "shared_core": "utils.database.execute_read_only_query -> adapter registry -> normalized result",
        },
        "legacy_database_mapping": {
            "mysql": {"internal_key": "mysql", "status": "IMPLEMENTED"},
            "postgresql": {"internal_key": "postgresql", "status": "IMPLEMENTED"},
            "mssql": {"internal_key": "sqlserver", "status": "IMPLEMENTED"},
            "oracle": {"internal_key": None, "status": "UNSUPPORTED_DECLARED_LEGACY"},
            "oracle11g": {"internal_key": None, "status": "UNSUPPORTED_DECLARED_LEGACY"},
        },
        "phase10_4_required_changes": [
            "Preserve original Legacy SQL acceptance as exactly one SELECT statement; do not silently inherit broader modern policy.",
            "Preserve the Legacy runtime exception path with sanitized text instead of returning a new structured Legacy error envelope.",
            "Reject unsupported or duplicate db_properties explicitly; do not silently discard them. Only schema, charset, and ssl_mode map to internal config.",
        ],
        "phase10_4_verification_matrix": [
            "nine_parameter_order", "legacy_to_internal_mapping", "mssql_to_sqlserver", "oracle_and_oracle11g_controlled_unsupported",
            "legacy_markdown_github_table", "legacy_json_records_only", "modern_structured_envelope_unchanged",
            "json_tool_parameters_persistence", "legacy_and_modern_isolation", "sanitized_legacy_exception_path",
        ],
        "not_proven": [
            "ORACLE_RUNTIME_PASS", "ORACLE11G_RUNTIME_PASS", "DM8_NEW_RUNTIME_PASS", "KINGBASEES_NEW_RUNTIME_PASS",
            "PHASE_10_4_IMPLEMENTATION_PASS", "FINAL_PROJECT_DELIVERY_PASS",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "failures": len(failures)}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
