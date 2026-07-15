"""Verify the existing Legacy Markdown and JSON Workflows without mutating them."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any


API_URL = "http://nginx/v1/workflows/run"
PROVIDER_ID = "li_zijun/db_query_extended/db_query_extended"
EXPECTED_IDENTIFIER = "li_zijun/db_query_extended:0.1.3@975d378099f6f817bda07eb6351bcbc9ec535d6bdb5ec3b33e40ab6b65cd14cf"
URL_WITH_CREDENTIALS = re.compile(r"[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@", re.I)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Gate:
    def __init__(self, args: argparse.Namespace):
        from app_factory import create_app

        self.args = args
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.secrets: list[str] = []
        self.apps: dict[str, Any] = {}
        self.tokens: dict[str, str] = {}
        self.database_inputs: dict[str, dict[str, Any]] = {}
        self.active_identifier = ""

    def close(self) -> None:
        self.context.pop()

    def safe(self, value: Any) -> bool:
        text = json.dumps(value, ensure_ascii=False, default=str)
        return (
            all(secret not in text for secret in self.secrets)
            and "Bearer " not in text
            and not URL_WITH_CREDENTIALS.search(text)
        )

    def prepare(self) -> dict[str, Any]:
        from core.plugin.impl.tool import PluginToolManager
        from extensions.ext_database import db
        from models.model import ApiToken, App

        app_ids = {"markdown": self.args.markdown_app_id, "json": self.args.json_app_id}
        for workflow_format, app_id in app_ids.items():
            app = db.session.get(App, app_id)
            if app is None or str(app.mode) != "workflow" or not app.workflow_id:
                raise RuntimeError(f"Existing {workflow_format} Workflow is missing or unpublished.")
            tokens = list(db.session.query(ApiToken).filter(ApiToken.app_id == app.id).all())
            if len(tokens) != 1 or not tokens[0].token:
                raise RuntimeError(f"Existing {workflow_format} Workflow API key is unavailable.")
            self.apps[workflow_format] = app
            self.tokens[workflow_format] = tokens[0].token
            self.secrets.append(tokens[0].token)

        tenant_ids = {str(app.tenant_id) for app in self.apps.values()}
        if len(tenant_ids) != 1:
            raise RuntimeError("Existing Markdown and JSON Workflows do not share a tenant.")
        entity = PluginToolManager().fetch_tool_provider(tenant_ids.pop(), PROVIDER_ID)
        self.active_identifier = entity.plugin_unique_identifier
        if self.active_identifier != EXPECTED_IDENTIFIER:
            raise AssertionError("Active plugin identifier does not match the Phase 10.5 candidate.")
        self.database_inputs = {database: self.legacy_inputs(database) for database in ("postgresql", "mysql", "mssql")}

        return {
            "active_plugin_identifier": self.active_identifier,
            "workflow_apps": {
                kind: {
                    "app_id": str(app.id),
                    "workflow_id": str(app.workflow_id),
                    "name": app.name,
                    "api_key": {"source": "existing Dify app token", "present": True, "length": len(self.tokens[kind])},
                }
                for kind, app in self.apps.items()
            },
            "workflow_mutated": False,
            "workflow_imported": False,
            "workflow_published": False,
            "api_key_changed": False,
        }

    def modern_credential(self, database_type: str) -> dict[str, Any]:
        from core.tools.tool_manager import ToolManager
        from extensions.ext_database import db
        from models.tools import BuiltinToolProvider
        from services.tools.builtin_tools_manage_service import BuiltinToolManageService

        tenant_id = str(next(iter(self.apps.values())).tenant_id)
        controller = ToolManager.get_builtin_provider(PROVIDER_ID, tenant_id)
        rows = db.session.query(BuiltinToolProvider).filter(BuiltinToolProvider.provider == PROVIDER_ID).all()
        for row in rows:
            encrypter, _ = BuiltinToolManageService.create_tool_encrypter(tenant_id, row, PROVIDER_ID, controller)
            credential = dict(encrypter.decrypt(row.credentials))
            if credential.get("database_type") == database_type:
                self.secrets.extend(str(value) for key, value in credential.items() if key in {"password", "token", "api_key"} and value)
                return credential
        raise RuntimeError(f"Existing Modern credential is missing for {database_type}.")

    def legacy_inputs(self, database: str) -> dict[str, Any]:
        if database == "mysql":
            password = os.environ.get("PHASE10_6_MYSQL_PASSWORD")
            if not password:
                raise RuntimeError("PHASE10_6_MYSQL_PASSWORD is required from the existing local fixture only.")
            self.secrets.append(password)
            return {
                "db_type": "mysql", "db_host": "host.docker.internal", "db_port": 3306,
                "db_username": "plugin_test_user", "db_password": password, "db_name": "plugin_test",
                "db_properties": "charset=utf8mb4",
            }
        source = self.modern_credential({"postgresql": "postgresql", "mssql": "sqlserver"}[database])
        properties = "ssl_mode=disable" if database == "postgresql" else "&".join(
            f"{key}={source[key]}" for key in ("schema", "charset", "ssl_mode") if source.get(key)
        )
        return {
            "db_type": database,
            "db_host": source["host"],
            "db_port": source.get("port"),
            "db_username": source["username"],
            "db_password": source["password"],
            "db_name": source.get("database", ""),
            "db_properties": properties,
        }

    def request(self, workflow_format: str, database: str, case_name: str, sql: str) -> tuple[int, dict[str, Any], float]:
        payload = {
            "inputs": {**self.database_inputs[database], "query_sql": sql},
            "response_mode": "blocking",
            "user": f"phase10_6_{workflow_format}_{case_name}",
        }
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.tokens[workflow_format]}", "Content-Type": "application/json"},
            method="POST",
        )
        started = perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                status, body = response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            status, body = exc.code, json.loads(exc.read().decode("utf-8", errors="replace"))
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        if not self.safe(body):
            raise AssertionError("Workflow response contains a sensitive value.")
        return status, body, elapsed_ms

    def trace(self, run_id: str) -> dict[str, Any]:
        from extensions.ext_database import db
        from models.workflow import WorkflowNodeExecutionModel, WorkflowRun
        from sqlalchemy import select

        run = db.session.get(WorkflowRun, run_id)
        if run is None:
            raise AssertionError("Workflow API response did not persist a WorkflowRun.")
        nodes = db.session.scalars(
            select(WorkflowNodeExecutionModel)
            .where(WorkflowNodeExecutionModel.workflow_run_id == run_id)
            .order_by(WorkflowNodeExecutionModel.index)
        ).all()
        summary = []
        tool_identifier = None
        for node in nodes:
            metadata = node.execution_metadata_dict or {}
            if node.node_type == "tool":
                tool_identifier = metadata.get("tool_info", {}).get("plugin_unique_identifier")
            summary.append({"node_type": node.node_type, "status": str(node.status)})
        return {
            "workflow_status": str(run.status),
            "nodes": summary,
            "tool_identity": tool_identifier,
            "tool_called": any(node["node_type"] == "tool" for node in summary),
            "template_called": any(node["node_type"] == "template-transform" for node in summary),
            "output_called": any(node["node_type"] == "end" for node in summary),
        }

    @staticmethod
    def output(body: dict[str, Any]) -> Any:
        return body.get("data", {}).get("outputs", {}).get("result")

    def success_case(self, workflow_format: str, database_type: str) -> dict[str, Any]:
        http_status, body, elapsed_ms = self.request(workflow_format, database_type, database_type, "SELECT 1 AS probe;")
        trace = self.trace(str(body.get("workflow_run_id")))
        result = self.output(body)
        if workflow_format == "markdown":
            shape = "github_markdown_table" if isinstance(result, str) and re.search(r"\|\s*probe\s*\|", result) and re.search(r"\|\s*1\s*\|", result) else "unexpected"
            contract = isinstance(result, str) and shape == "github_markdown_table"
            probe = 1 if contract else None
        else:
            parsed = json.loads(result) if isinstance(result, str) else None
            shape = "records_only_json_string" if isinstance(parsed, dict) and set(parsed) == {"records"} else "unexpected"
            contract = isinstance(parsed, dict) and parsed.get("records") == [{"probe": 1}]
            probe = 1 if contract else None
        checks = {
            "http_success": 200 <= http_status < 300,
            "workflow_succeeded": trace["workflow_status"] == "succeeded",
            "tool_called": trace["tool_called"],
            "active_legacy_tool": trace["tool_identity"] == self.active_identifier,
            "template_called": trace["template_called"],
            "output_called": trace["output_called"],
            "result_string": isinstance(result, str) and bool(result),
            "legacy_contract": contract,
            "modern_envelope_absent": not isinstance(result, dict) or not {"columns", "rows", "row_count", "truncated", "max_rows"}.intersection(result),
        }
        return {
            "database_type": database_type,
            "workflow_format": workflow_format,
            "http_status": http_status,
            "workflow_status": trace["workflow_status"],
            "tool_identity": trace["tool_identity"],
            "result_type": type(result).__name__,
            "result_shape": shape,
            "probe_value": probe,
            "legacy_contract_pass": contract,
            "modern_envelope_absent": checks["modern_envelope_absent"],
            "template_output_mapping": trace["template_called"] and trace["output_called"],
            "elapsed_ms": elapsed_ms,
            "checks": checks,
            "status": "PASS" if all(checks.values()) else "FAIL",
        }

    def negative_case(self, case_name: str, sql: str) -> dict[str, Any]:
        http_status, body, elapsed_ms = self.request("markdown", "postgresql", case_name, sql)
        run_id = body.get("workflow_run_id")
        trace = self.trace(str(run_id)) if run_id else {"workflow_status": "not_created", "nodes": [], "tool_identity": None, "tool_called": False}
        result = self.output(body)
        text = json.dumps(body, ensure_ascii=False, default=str)
        checks = {
            "workflow_failed": trace["workflow_status"] != "succeeded",
            "tool_exception_chain": trace["tool_called"],
            "success_payload_absent": not (isinstance(result, str) and ("| probe" in result or '"records"' in result)),
            "modern_error_envelope_absent": "columns" not in text and "row_count" not in text,
            "sensitive_scan_pass": self.safe(body),
        }
        return {
            "case_name": case_name,
            "workflow_format": "markdown",
            "database_type": "postgresql",
            "http_status": http_status,
            "expected_failure": True,
            "observed_failure": trace["workflow_status"] != "succeeded",
            "failure_stage": "PluginInvokeError / Workflow exception chain" if trace["tool_called"] else "before_tool",
            "workflow_status": trace["workflow_status"],
            "tool_identity": trace["tool_identity"],
            "sanitized": checks["sensitive_scan_pass"],
            "success_payload_absent": checks["success_payload_absent"],
            "sensitive_scan_pass": checks["sensitive_scan_pass"],
            "elapsed_ms": elapsed_ms,
            "checks": checks,
            "status": "PASS" if all(checks.values()) else "FAIL",
        }

    def run(self) -> int:
        preflight = self.prepare()
        successes = [self.success_case(kind, database) for kind in ("markdown", "json") for database in ("postgresql", "mysql", "mssql")]
        negatives = [
            self.negative_case("multi_statement_rejected", "SELECT 1; SELECT 2;"),
            self.negative_case("missing_table_rejected", "SELECT * FROM phase10_6_missing_table;"),
        ]
        failures = [case for case in successes + negatives if case["status"] != "PASS"]
        evidence = {
            "phase": "Phase 10.6 — Legacy Workflow End-to-End Non-Regression Gate",
            "status": "PASS" if not failures else "PARTIAL",
            "date": utcnow(),
            "source_commit": self.args.source_commit,
            "phase10_5_evidence_commit": self.args.phase10_5_evidence_commit,
            "candidate_package_sha256": self.args.candidate_package_sha256,
            "active_plugin_checksum": self.active_identifier.rsplit("@", 1)[-1],
            "active_plugin_identifier": self.active_identifier,
            "workflow_scope": "existing published Phase 10.2.1 Markdown and JSON Workflows only",
            "database_scope": ["postgresql", "mysql", "mssql"],
            "successful_case_count": sum(case["status"] == "PASS" for case in successes),
            "workflow_api_succeeded_case_count": sum(
                200 <= case["http_status"] < 300 and case["workflow_status"] == "succeeded" for case in successes
            ),
            "failed_case_count": len(failures),
            "markdown_cases": [case for case in successes if case["workflow_format"] == "markdown"],
            "json_cases": [case for case in successes if case["workflow_format"] == "json"],
            "negative_cases": negatives,
            "workflow_mutated": preflight["workflow_mutated"],
            "workflow_published": preflight["workflow_published"],
            "api_key_changed": preflight["api_key_changed"],
            "sensitive_values_retained": False,
            "checks": preflight,
            "failures": [case.get("case_name", f"{case['workflow_format']}_{case['database_type']}") for case in failures],
            "not_proven": ["ORACLE_RUNTIME_PASS", "ORACLE11G_RUNTIME_PASS", "DM8_NEW_RUNTIME_PASS", "KINGBASEES_NEW_RUNTIME_PASS", "FINAL_PROJECT_DELIVERY_PASS"],
        }
        dump(self.args.output, evidence)
        print(json.dumps({"status": evidence["status"], "successful_case_count": evidence["successful_case_count"], "failed_case_count": evidence["failed_case_count"]}))
        return 0 if evidence["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown-app-id", required=True)
    parser.add_argument("--json-app-id", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--phase10-5-evidence-commit", required=True)
    parser.add_argument("--candidate-package-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    gate = Gate(parser.parse_args())
    try:
        return gate.run()
    finally:
        gate.close()


if __name__ == "__main__":
    raise SystemExit(main())
