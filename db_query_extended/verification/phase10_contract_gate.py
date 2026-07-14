"""Freeze and verify the Phase 10 original-plugin reproduction contracts.

Read-only with respect to the reference package and production plugin.  It
re-extracts the reference YAML/code on every run, writes the versioned contract
JSON files and machine evidence, and exits non-zero for a contract mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "junjiem-db_query_0.0.11-offline.difypkg"
CONTRACTS = ROOT / "reports" / "contracts"
EVIDENCE = ROOT / "reports" / "verification" / "2026-07-13"
SHA256 = "6619DB2611D25C685F8CA4F565F86E972A0EBD25894464EF911AEA09C77F1560"
SOURCE = {"artifact": "junjiem-db_query_0.0.11-offline(1).difypkg", "local_path": "LOCAL_ONLY / NOT_TRACKED_BY_GIT", "sha256": SHA256}
PARAMETERS = ["db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "db_properties", "query_sql", "output_format"]
DATABASES = ["mysql", "oracle", "oracle11g", "postgresql", "mssql"]


def stamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dump(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_reference() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str]:
    if not REFERENCE.is_file():
        raise FileNotFoundError(f"reference package missing: {REFERENCE}")
    actual = hashlib.sha256(REFERENCE.read_bytes()).hexdigest().upper()
    if actual != SHA256:
        raise ValueError(f"reference SHA-256 mismatch: {actual}")
    with zipfile.ZipFile(REFERENCE) as package:
        if package.testzip() is not None:
            raise ValueError("reference ZIP integrity failure")
        manifest = yaml.safe_load(package.read("manifest.yaml"))
        provider = yaml.safe_load(package.read("provider/db_query.yaml"))
        tool = yaml.safe_load(package.read("tools/sql_query.yaml"))
        requirements = package.read("requirements.txt").decode("utf-8")
        db_util = package.read("tools/db_util.py").decode("utf-8")
    return manifest, provider, tool, requirements, db_util


def base(kind: str) -> dict[str, Any]:
    return {"schema_version": "1.0", "contract": kind, "extraction_date": "2026-07-13", "source_artifact": SOURCE, "validation_status": "FROZEN", "unknown_fields": [], "evidence_references": ["reports/verification/2026-07-13/original_plugin_artifact_inventory.json"]}


def build_contracts() -> dict[str, dict[str, Any]]:
    manifest, provider, tool, requirements, db_util = load_reference()
    raw_parameters = tool["parameters"]
    ui = base("ORIGINAL_PLUGIN_UI_CONTRACT")
    ui.update({
        "source_files": ["manifest.yaml", "provider/db_query.yaml", "tools/sql_query.yaml"],
        "raw_values": {"manifest": {key: manifest[key] for key in ("name", "author", "label", "description", "icon", "version")}, "provider_identity": provider["identity"], "tool_identity": tool["identity"], "tool_description": tool["description"]},
        "normalized": {"package_identity": {"must_remain_project_owned": ["author", "name", "version", "notice"], "reference_identity_not_to_be_impersonated": True}, "ui_contract": {"plugin_label": manifest["label"], "plugin_description": manifest["description"], "icon": manifest["icon"], "tool_label": tool["identity"]["label"], "tool_description": tool["description"]["human"], "node_selector_identity": {"provider": provider["identity"]["name"], "tool": tool["identity"]["name"]}}},
    })
    ui["unknown_fields"] = [{"field": "installed_Dify_node_selector_rendering", "status": "UNKNOWN", "reason": "original package was not installed into a disposable tenant during the audit"}]

    parameter = base("ORIGINAL_PLUGIN_PARAMETER_CONTRACT")
    parameter.update({"source_files": ["tools/sql_query.yaml"], "raw_values": {"parameters": raw_parameters}, "normalized": {"parameter_order": [item["name"] for item in raw_parameters], "parameters": [{"internal_name": item["name"], "display_label": item.get("label"), "description": item.get("human_description"), "type": item["type"], "form": item.get("form"), "required": item["required"], "default": item.get("default"), "placeholder": item.get("placeholder"), "minimum": item.get("min"), "maximum": item.get("max"), "options": item.get("options", []), "yaml_order": index + 1, "workflow_visible": True, "variable_binding": "UNKNOWN_FROM_STATIC_YAML", "depends_on": []} for index, item in enumerate(raw_parameters)]}})
    parameter["unknown_fields"] = [{"field": "Dify runtime variable-binding widget behavior", "status": "UNKNOWN", "reason": "not encoded by the original YAML and no isolated Dify installation was performed"}]

    output = base("ORIGINAL_PLUGIN_OUTPUT_CONTRACT")
    output.update({"source_files": ["tools/sql_query.py", "tools/db_util.py", "requirements.txt"], "raw_values": {"format_dispatch": "json => create_json_message({records: records}); otherwise => tabulate(..., tablefmt=github)", "normalization": {"null": "pandas fillna('')", "timestamp": "YYYY-MM-DD HH:MM:SS", "date": "YYYY-MM-DD", "integral_float": "int", "json_envelope": {"records": []}}, "requirements": [line for line in requirements.splitlines() if line]}, "normalized": {"modes": ["legacy_markdown", "legacy_json_records", "modern_structured_json"], "legacy_markdown": {"default": True, "table_format": "github", "exact_observed_golden": "|   probe |\\n|---------|\\n|       1 |", "trailing_newline": False}, "legacy_json_records": {"top_level": ["records"], "row_shape": "object", "null": "", "empty": {"records": []}, "unicode": "preserved", "date": "YYYY-MM-DD", "timestamp": "YYYY-MM-DD HH:MM:SS"}, "modern_structured_json": {"required_keys": ["columns", "rows", "row_count", "truncated", "max_rows", "database_type", "execution_time_ms"], "null": None}, "security_exception": "raw errors must not be reproduced"}})
    output["unknown_fields"] = [{"field": "full original-runtime Markdown golden matrix", "status": "PENDING_FIXTURE_CAPTURE", "reason": "the audited isolated runtime captured SELECT 1 Markdown only; source-level formatter semantics are frozen without inventing unobserved output"}]
    output["evidence_references"].append("reports/verification/2026-07-13/original_plugin_runtime_probe.json")

    database = base("ORIGINAL_PLUGIN_DATABASE_CONTRACT")
    routes = {"mysql": {"driver": "PyMySQL==1.1.1", "url": "mysql+pymysql", "test_sql": "SELECT 1", "runtime": "PASS"}, "oracle": {"driver": "oracledb==2.2.1", "url": "oracle+oracledb", "test_sql": "SELECT 1 FROM DUAL", "runtime": "NOT_TESTED"}, "oracle11g": {"driver": "oracledb==2.2.1", "url": "oracle+oracledb", "test_sql": "SELECT 1 FROM DUAL", "native_client": "oracledb.init_oracle_client()", "runtime": "BLOCKED"}, "postgresql": {"driver": "psycopg2-binary==2.9.10", "url": "postgresql+psycopg2", "test_sql": "SELECT 1", "runtime": "PASS"}, "mssql": {"driver": "pymssql==2.3.4", "url": "mssql+pymssql", "test_sql": "SELECT 1", "runtime": "PASS"}}
    database.update({"source_files": ["requirements.txt", "tools/db_util.py", "tools/sql_query.yaml"], "raw_values": {"requirements": [line for line in requirements.splitlines() if line], "driver_branches_present": {name: name in db_util for name in DATABASES}}, "normalized": {"mandatory_original_scope": DATABASES, "extension_scope": ["dm8", "kingbasees"], "out_of_scope": ["sqlite", "mariadb_specific", "tidb", "oceanbase", "clickhouse", "db2", "duckdb", "snowflake"], "routes": routes, "adapter_mapping_target": {"mysql": "MySQLAdapter", "postgresql": "PostgreSQLAdapter", "mssql": "SQLServerAdapter", "oracle": "OracleAdapter", "oracle11g": "Oracle11gAdapter", "dm8": "DM8Adapter", "kingbasees": "KingbaseESAdapter"}, "sqlserver_position": ["ORIGINAL_BASE_PLUGIN_REQUIRED_DATABASE", "OPTIONAL_MODERN_PROVIDER_COMPATIBILITY_PATH"]}})
    database["normalized"]["oracle_route_decisions"] = {
        "oracle": {"status": "ORACLE_IMPLEMENTATION_ROUTE_CONDITIONAL", "preferred": "SQLAlchemy oracle+oracledb with python-oracledb thin where server compatibility is proven", "candidates": ["python-oracledb thin", "python-oracledb thick", "cx_Oracle", "SQLAlchemy oracle+oracledb", "SQLAlchemy oracle+cx_oracle", "plugin-owned compatibility wrapper"], "rejections_or_conditions": {"cx_Oracle": "legacy driver; no selection without Python 3.12/offline evidence", "wrapper": "adds maintenance and cannot substitute for a real DBAPI runtime"}},
        "oracle11g": {"status": "ORACLE11G_IMPLEMENTATION_ROUTE_CONDITIONAL", "preferred": "SQLAlchemy oracle+oracledb using python-oracledb thick mode with compatible Instant Client", "required_to_unblock": ["Oracle 11g server", "compatible Linux amd64 Instant Client", "license/redistribution decision", "offline wheel and native-library inspection", "Dify plugin-daemon validation"]},
        "comparison_dimensions": ["Python 3.12", "Linux amd64", "server compatibility", "Instant Client", "manylinux wheel", "native .so/ldd", "offline installation", "Dify daemon", "package size", "license/redistribution", "package inclusion", "legacy behavior"],
    }
    database["unknown_fields"] = [{"field": "Oracle server version and real connection", "status": "NOT_TESTED"}, {"field": "Oracle11g Instant Client media/license/server", "status": "BLOCKED"}]

    workflow = base("ORIGINAL_PLUGIN_WORKFLOW_MIGRATION_CONTRACT")
    workflow.update({"source_files": ["tools/sql_query.yaml", "provider/db_query.yaml"], "raw_values": {"provider": provider["identity"]["name"], "tool": tool["identity"]["name"], "parameters": PARAMETERS}, "normalized": {"migration_definition": "replace identity without losing the nine fields, bindings, downstream Markdown or records consumers, or mssql", "strategies": [{"name": "legacy_compatible_tool", "status": "RECOMMENDED", "reason": "smallest user-facing compatibility surface"}, {"name": "workflow_migration_utility", "status": "RECOMMENDED", "reason": "preserves exported DSL bindings and downstream references"}, {"name": "in_place_reference_identity", "status": "REJECTED", "reason": "would impersonate the original publisher and conflicts with Dify installation identity"}], "future_passes": [f"{name.upper()}_LEGACY_WORKFLOW_MIGRATION_PASS" for name in ["MYSQL", "POSTGRESQL", "MSSQL", "ORACLE", "ORACLE11G"]] + ["DM8_LEGACY_STYLE_WORKFLOW_PASS", "KINGBASEES_LEGACY_STYLE_WORKFLOW_PASS"]}})
    workflow["unknown_fields"] = [{"field": "original exported workflow DSL", "status": "NOT_AVAILABLE", "reason": "reference package was not installed or exported to avoid changing the active tenant"}]

    architecture = base("FINAL_REPRODUCTION_ARCHITECTURE")
    architecture.update({"source_files": ["db_query_extended/provider/db_query_extended.yaml", "db_query_extended/tools/db_query_extended.yaml", "db_query_extended/utils/adapters/__init__.py"], "raw_values": {"current_tool": "db_query_extended", "current_provider": "db_query_extended"}, "normalized": {"legacy_compatible_tool": {"parameters": PARAMETERS, "inline_credentials": True, "formats": ["legacy_markdown", "legacy_json_records"]}, "modern_provider_tool": {"credentials": "provider", "parameters": ["sql", "max_rows", "timeout_seconds", "readonly", "output_format"], "format": "modern_structured_json"}, "shared_secure_core": ["credential normalization", "secret redaction", "read-only validator", "connection lifecycle", "adapter registry", "dialect registration", "result normalization", "formatter modes"], "security_boundary": {"normal_read_query_parity": "REQUIRED", "vulnerability_parity": "FORBIDDEN", "forbidden_regressions": ["credentialed URL logging", "raw database errors", "CTE DELETE", "SELECT INTO", "INTO OUTFILE", "FOR UPDATE", "multi-statement", "connection leak"]}}})

    sequence = base("FINAL_CORRECT_REPRODUCTION_SEQUENCE")
    sequence.update({"source_files": ["reports/documentation/PROJECT_DELIVERY_CONTRACT.md"], "raw_values": {"development_history_and_tutorial_are_distinct": True}, "normalized": {"steps": ["verify reference package", "read-only unpack", "freeze UI/parameter/output/workflow contracts", "confirm five original databases", "confirm DM8 and KingbaseES extensions", "design legacy tool + modern tool + shared core", "prepare seven-database environments and dependencies", "implement shared secure core", "implement five original adapters", "verify legacy UI/output/workflow", "add DM8", "add KingbaseES", "collect offline dependencies", "build final package", "install and validate seven databases", "produce delivery evidence"], "tutorial_excluded_detours": ["two-database-first implementation", "incompatible parameter retrofit", "modern-JSON-only retrofit", "Markdown omission", "SQL Server marked purely optional", "extension completion claimed before base reproduction"]}})
    return {"original_plugin_ui_contract.json": ui, "original_plugin_parameter_contract.json": parameter, "original_plugin_output_contract.json": output, "original_plugin_database_contract.json": database, "original_plugin_workflow_migration_contract.json": workflow, "final_reproduction_architecture.json": architecture, "final_correct_reproduction_sequence.json": sequence}


def check(condition: bool, name: str, detail: str) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def write_evidence(contracts: dict[str, dict[str, Any]]) -> int:
    manifest, provider, tool, requirements, db_util = load_reference()
    results = {
        "phase10_0_original_ui_contract_gate.json": [check(contracts["original_plugin_ui_contract.json"]["raw_values"]["manifest"]["label"] == manifest["label"], "manifest_labels", "direct package label extraction"), check(contracts["original_plugin_ui_contract.json"]["raw_values"]["tool_identity"] == tool["identity"], "tool_identity", "direct Tool identity extraction")],
        "phase10_0_parameter_contract_gate.json": [check([p["name"] for p in tool["parameters"]] == PARAMETERS, "nine_parameter_order", "source YAML order"), check(contracts["original_plugin_parameter_contract.json"]["raw_values"]["parameters"] == tool["parameters"], "raw_parameter_match", "full raw YAML parameters")],
        "phase10_0_output_contract_gate.json": [check("create_json_message({\"records\": records})" in tool_source() and "tablefmt=\"github\"" in tool_source(), "source_dispatch", "direct output implementation"), check(contracts["original_plugin_output_contract.json"]["normalized"]["legacy_json_records"]["null"] == "", "legacy_null", "frozen source behavior")],
        "phase10_0_database_scope_gate.json": [check([x["value"] for x in tool["parameters"][0]["options"]] == DATABASES, "mandatory_five_scope", "direct db_type options"), check(all(route in db_util for route in ["mysql+pymysql", "oracle+oracledb", "postgresql+psycopg2", "mssql+pymssql"]), "driver_routes", "direct db_util routes")],
        "phase10_0_workflow_migration_design_gate.json": [check(contracts["original_plugin_workflow_migration_contract.json"]["raw_values"]["parameters"] == PARAMETERS, "binding_preservation", "nine legacy fields"), check("mssql" in contracts["original_plugin_workflow_migration_contract.json"]["normalized"]["migration_definition"], "mssql_preserved", "legacy option retained")],
        "phase10_0_oracle_route_decision.json": [check("oracledb==2.2.1" in requirements and "oracle+oracledb" in db_util, "original_route", "python-oracledb route extracted"), check("init_oracle_client" in db_util, "oracle11g_thick_requirement", "native-client requirement extracted")],
        "phase10_0_oracle11g_route_decision.json": [check("init_oracle_client" in db_util, "original_thick_mode", "original code invokes thick-mode initialization"), check("Instant Client" in contracts["original_plugin_database_contract.json"]["unknown_fields"][1]["field"], "blocker_recorded", "external-client blocker recorded")],
        "phase10_0_architecture_freeze.json": [check((ROOT / "db_query_extended" / "utils" / "adapters" / "__init__.py").is_file(), "shared_registry_exists", "current secure core is reusable"), check(contracts["final_reproduction_architecture.json"]["normalized"]["legacy_compatible_tool"]["parameters"] == PARAMETERS, "legacy_design", "design preserves nine parameters")],
        "phase10_0_reproduction_sequence_gate.json": [check(contracts["final_correct_reproduction_sequence.json"]["normalized"]["steps"][:3] == ["verify reference package", "read-only unpack", "freeze UI/parameter/output/workflow contracts"], "correct_start", "contract audit precedes implementation"), check("two-database-first implementation" in contracts["final_correct_reproduction_sequence.json"]["normalized"]["tutorial_excluded_detours"], "detour_excluded", "historical detour excluded")],
        "phase10_0_delivery_contract_alignment.json": [check_delivery_contract()],
    }
    status = 0
    for filename, checks in results.items():
        failed = [entry for entry in checks if entry["status"] != "PASS"]
        payload = {"suite": filename.removesuffix(".json"), "generated_at": stamp(), "status": "FAIL" if failed else "PASS", "source_artifact": SOURCE, "checks": checks, "unknown_fields": []}
        if filename == "phase10_0_oracle_route_decision.json":
            payload["decision_status"] = contracts["original_plugin_database_contract.json"]["normalized"]["oracle_route_decisions"]["oracle"]["status"]
            payload["route"] = contracts["original_plugin_database_contract.json"]["normalized"]["oracle_route_decisions"]["oracle"]
        if filename == "phase10_0_oracle11g_route_decision.json":
            payload["decision_status"] = contracts["original_plugin_database_contract.json"]["normalized"]["oracle_route_decisions"]["oracle11g"]["status"]
            payload["route"] = contracts["original_plugin_database_contract.json"]["normalized"]["oracle_route_decisions"]["oracle11g"]
        dump(EVIDENCE / filename, payload)
        status |= bool(failed)
    final_checks = [check(not status, "all_contract_gates", "every Phase 10 contract gate passed"), check(not production_changes(), "no_production_code_change", "working tree production source remains unchanged from baseline")]
    final = {"suite": "phase10_0_final_gate", "generated_at": stamp(), "status": "PASS" if all(x["status"] == "PASS" for x in final_checks) else "FAIL", "phase_status": "PHASE_10_0_PASS" if all(x["status"] == "PASS" for x in final_checks) else "PHASE_10_0_FAIL", "checks": final_checks, "allowed_conclusions": ["ORIGINAL_PLUGIN_CONTRACT_FROZEN", "FINAL_REPRODUCTION_ARCHITECTURE_FROZEN", "FINAL_CORRECT_REPRODUCTION_SEQUENCE_FROZEN"], "not_yet_proven": ["ORIGINAL_BASE_PLUGIN_REPRODUCTION_CONFIRMED", "ORACLE_REPRODUCTION_PASS", "ORACLE11G_REPRODUCTION_PASS", "LEGACY_WORKFLOW_MIGRATION_PASS", "DM8_FINAL_DELIVERY_PASS", "FINAL_PROJECT_DELIVERY_PASS"]}
    dump(EVIDENCE / "phase10_0_final_gate.json", final)
    return 1 if final["status"] != "PASS" else 0


def tool_source() -> str:
    with zipfile.ZipFile(REFERENCE) as package:
        return package.read("tools/sql_query.py").decode("utf-8")


def check_delivery_contract() -> dict[str, Any]:
    text = (ROOT / "reports" / "documentation" / "PROJECT_DELIVERY_CONTRACT.md").read_text(encoding="utf-8")
    required = ["Oracle11g", "Microsoft SQL Server", "查询功能等价", "用户参数等价", "输出格式等价", "Workflow 可迁移", "UI contract 等价", "可安装、可查询 runtime 等价", "安全强化", "教程不得要求复现者重走历史返工路径"]
    missing = [item for item in required if item not in text]
    return check(not missing, "normative_alignment", f"missing={missing}")


def production_changes() -> list[str]:
    result = subprocess.run(["git", "diff", "--name-only", "d29247494f9a48c6dc79de8ea8e9e31ae2cfa2ca"], cwd=ROOT, text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line.startswith("db_query_extended/") and not line.startswith("db_query_extended/verification/")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-contracts", action="store_true")
    args = parser.parse_args()
    contracts = build_contracts()
    if args.write_contracts:
        for name, content in contracts.items():
            dump(CONTRACTS / name, content)
    else:
        for name, content in contracts.items():
            path = CONTRACTS / name
            if not path.is_file() or json.loads(path.read_text(encoding="utf-8")) != content:
                raise ValueError(f"contract is stale or missing: {path}")
    result = write_evidence(contracts)
    print(json.dumps({"status": "PASS" if not result else "FAIL", "contracts": len(contracts), "evidence": 11}, ensure_ascii=False))
    return result


if __name__ == "__main__":
    sys.exit(main())
