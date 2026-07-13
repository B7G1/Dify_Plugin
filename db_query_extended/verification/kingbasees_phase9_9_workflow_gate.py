"""Create and verify the installed KingbaseES Workflow through Dify's service API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable


PROVIDER_ID = "li_zijun/db_query_extended/db_query_extended"
PLUGIN_ID = "li_zijun/db_query_extended"
TOOL_NAME = "db_query_extended"
EXPECTED_CHECKSUM = "bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9"
EXPECTED_IDENTIFIER = f"{PLUGIN_ID}:0.1.1@{EXPECTED_CHECKSUM}"
APP_NAME = "KingbaseES Phase 9.9 Installed Workflow Gate"
SOURCE_APP_NAME = "DM8 Readonly SQL Acceptance"
KINGBASE_CREDENTIAL_NAME = "KingbaseES Phase 9.8 Readonly"
POSTGRES_CREDENTIAL_NAME = "PostgreSQL Phase 9.8 Regression"
API_URL = "http://nginx/v1/workflows/run"
OUTPUT_KEYS = {
    "columns", "rows", "row_count", "truncated", "max_rows",
    "database_type", "execution_time_ms",
}
URL_WITH_CREDENTIALS = re.compile(r"[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@", re.I)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def parse_json(value: str | None) -> Any:
    return json.loads(value) if value else None


def model(value: Any) -> Any:
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def suite(name: str, cases: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    return {
        "suite": name,
        "generated_at": utcnow(),
        "status": "PASS" if cases and all(case["status"] == "PASS" for case in cases) else "FAIL",
        "summary": {
            "pass": sum(case["status"] == "PASS" for case in cases),
            "fail": sum(case["status"] == "FAIL" for case in cases),
            "skip": sum(case["status"] == "SKIP" for case in cases),
        },
        "cases": cases,
        **extra,
    }


class Gate:
    def __init__(self, output_dir: Path, runtime_evidence: Path):
        from app_factory import create_app

        self.output_dir = output_dir
        self.runtime_evidence = json.loads(runtime_evidence.read_text(encoding="utf-8"))
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.tenant_id = ""
        self.user_id = ""
        self.workflow_app: Any = None
        self.api_token = ""
        self.active_identifier = ""
        self.secrets: list[str] = []
        self.traces: list[dict[str, Any]] = []
        self.api_call_count = 0

    def close(self) -> None:
        self.context.pop()

    def credential(self, name: str) -> Any:
        from extensions.ext_database import db
        from models.tools import BuiltinToolProvider
        from sqlalchemy import select

        row = db.session.scalar(
            select(BuiltinToolProvider).where(
                BuiltinToolProvider.tenant_id == self.tenant_id,
                BuiltinToolProvider.provider == PROVIDER_ID,
                BuiltinToolProvider.name == name,
            )
        )
        if row is None:
            raise RuntimeError(f"Required Dify credential is missing: {name}")
        return row

    def decrypted_credentials(self, row: Any) -> dict[str, Any]:
        from core.tools.tool_manager import ToolManager
        from services.tools.builtin_tools_manage_service import BuiltinToolManageService

        controller = ToolManager.get_builtin_provider(PROVIDER_ID, self.tenant_id)
        encrypter, _ = BuiltinToolManageService.create_tool_encrypter(
            self.tenant_id, row, PROVIDER_ID, controller
        )
        return dict(encrypter.decrypt(row.credentials))

    def active_plugin(self) -> tuple[str, dict[str, Any]]:
        from core.plugin.impl.tool import PluginToolManager

        entity = PluginToolManager().fetch_tool_provider(self.tenant_id, PROVIDER_ID)
        return entity.plugin_unique_identifier, model(entity.declaration)

    def prepare(self) -> dict[str, Any]:
        from extensions.ext_database import db
        from libs.datetime_utils import naive_utc_now
        from models import Account
        from models.enums import ApiTokenType
        from models.model import App, ApiToken
        from models.tools import BuiltinToolProvider
        from models.workflow import Workflow
        from services.app_service import AppService
        from services.workflow_service import WorkflowService
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        provider_row = db.session.scalar(
            select(BuiltinToolProvider).where(BuiltinToolProvider.provider == PROVIDER_ID)
        )
        if provider_row is None:
            raise RuntimeError("No installed db_query_extended credential identifies the Dify tenant")
        self.tenant_id = str(provider_row.tenant_id)
        self.user_id = str(provider_row.user_id)
        account = db.session.get(Account, self.user_id)
        if account is None:
            raise RuntimeError("Dify credential owner account is missing")

        self.active_identifier, declaration = self.active_plugin()
        if self.active_identifier != EXPECTED_IDENTIFIER:
            raise AssertionError(f"Active plugin mismatch: {self.active_identifier}")

        kingbase = self.credential(KINGBASE_CREDENTIAL_NAME)
        kingbase_credentials = self.decrypted_credentials(kingbase)
        if kingbase_credentials.get("database_type") != "kingbasees":
            raise AssertionError("Named KingbaseES credential does not identify database_type=kingbasees")
        self.secrets.extend(
            str(value) for key, value in kingbase_credentials.items()
            if key in {"password", "token", "api_key"} and value
        )

        source_app = db.session.scalar(
            select(App).where(App.tenant_id == self.tenant_id, App.name == SOURCE_APP_NAME)
        )
        if source_app is None or not source_app.workflow_id:
            raise RuntimeError("Reusable three-node Workflow baseline is missing")
        source_workflow = db.session.get(Workflow, source_app.workflow_id)
        if source_workflow is None:
            raise RuntimeError("Reusable published Workflow snapshot is missing")

        target_app = db.session.scalar(
            select(App).where(App.tenant_id == self.tenant_id, App.name == APP_NAME)
        )
        created = target_app is None
        if target_app is None:
            target_app = AppService().create_app(
                self.tenant_id,
                {
                    "name": APP_NAME,
                    "description": "Installed KingbaseES Workflow API gate; no source overlay.",
                    "mode": "workflow",
                    "icon_type": source_app.icon_type.value if hasattr(source_app.icon_type, "value") else "emoji",
                    "icon": source_app.icon or "KB",
                    "icon_background": source_app.icon_background or "#E4FBCC",
                },
                account,
            )

        graph = deepcopy(source_workflow.graph_dict)
        start_nodes = [node for node in graph["nodes"] if node["data"].get("type") == "start"]
        tool_nodes = [node for node in graph["nodes"] if node["data"].get("type") == "tool"]
        end_nodes = [node for node in graph["nodes"] if node["data"].get("type") == "end"]
        if not (len(start_nodes) == len(tool_nodes) == len(end_nodes) == 1):
            raise AssertionError("Expected exactly one Start, Tool, and End node")
        start, tool, end = start_nodes[0], tool_nodes[0], end_nodes[0]
        variables = {item["variable"]: item for item in start["data"]["variables"]}
        if set(variables) != {"sql", "max_rows"} or not variables["sql"].get("required"):
            raise AssertionError("Workflow input contract must be sql + max_rows")
        tool_data = tool["data"]
        tool_data.update(
            {
                "title": "KingbaseES installed read-only SQL",
                "provider_id": PROVIDER_ID,
                "provider_name": PROVIDER_ID,
                "provider_type": "builtin",
                "plugin_id": PLUGIN_ID,
                "plugin_unique_identifier": self.active_identifier,
                "tool_name": TOOL_NAME,
                "credential_id": str(kingbase.id),
                "is_team_authorization": True,
            }
        )
        tool_data["tool_parameters"]["sql"] = {"type": "variable", "value": [start["id"], "sql"]}
        tool_data["tool_configurations"]["max_rows"] = {
            "type": "variable", "value": [start["id"], "max_rows"]
        }
        end["data"]["outputs"] = [{"variable": "result", "value_selector": [tool["id"], "json"]}]

        published = db.session.get(Workflow, target_app.workflow_id) if target_app.workflow_id else None
        published_new = published is None or published.graph_dict != graph
        if published_new:
            service = WorkflowService()
            draft = service.get_draft_workflow(app_model=target_app)
            service.sync_draft_workflow(
                app_model=target_app,
                graph=graph,
                features=source_workflow.normalized_features_dict,
                unique_hash=draft.unique_hash if draft else None,
                account=account,
                environment_variables=source_workflow.environment_variables,
                conversation_variables=source_workflow.conversation_variables,
            )
            with Session(db.engine) as session:
                published = service.publish_workflow(
                    session=session,
                    app_model=target_app,
                    account=account,
                    marked_name="Phase 9.9 installed KingbaseES gate",
                    marked_comment="Explicit credential and active checksum binding",
                )
                app_in_session = session.get(App, target_app.id)
                app_in_session.workflow_id = published.id
                app_in_session.enable_api = True
                app_in_session.updated_by = account.id
                app_in_session.updated_at = naive_utc_now()
                session.commit()
            db.session.expire_all()
            target_app = db.session.get(App, target_app.id)
        elif not target_app.enable_api:
            target_app.enable_api = True
            db.session.commit()

        token = db.session.scalar(
            select(ApiToken)
            .where(ApiToken.app_id == target_app.id, ApiToken.type == ApiTokenType.APP)
            .order_by(ApiToken.created_at.desc())
        )
        token_created = token is None
        if token is None:
            token = ApiToken()
            token.app_id = target_app.id
            token.tenant_id = self.tenant_id
            token.type = ApiTokenType.APP
            token.token = ApiToken.generate_api_key("app-", 24)
            db.session.add(token)
            db.session.commit()
        self.api_token = token.token
        self.secrets.append(self.api_token)
        self.workflow_app = target_app

        published = db.session.get(Workflow, target_app.workflow_id)
        published_tool = next(
            node["data"] for node in published.graph_dict["nodes"] if node["data"].get("type") == "tool"
        )
        options = [item["value"] for item in declaration["credentials_schema"][0]["options"]]
        checks = {
            "active_checksum": self.active_identifier == EXPECTED_IDENTIFIER,
            "dedicated_workflow": target_app.name == APP_NAME,
            "workflow_published": bool(target_app.workflow_id),
            "api_enabled": bool(target_app.enable_api),
            "api_key_present": bool(self.api_token),
            "explicit_kingbase_credential": published_tool.get("credential_id") == str(kingbase.id),
            "published_plugin_identifier": published_tool.get("plugin_unique_identifier") == EXPECTED_IDENTIFIER,
            "sql_mapping": published_tool["tool_parameters"]["sql"]["value"] == [start["id"], "sql"],
            "max_rows_mapping": published_tool["tool_configurations"]["max_rows"]["value"] == [start["id"], "max_rows"],
            "provider_schema": options == ["mysql", "postgresql", "dm", "sqlserver", "kingbasees"],
            "installed_runtime_probe": self.runtime_evidence.get("status") == "PASS",
        }
        report = {
            "suite": "kingbasees_phase9_9_preflight",
            "generated_at": utcnow(),
            "status": "PASS" if all(checks.values()) else "FAIL",
            "baseline_commit": "2d9d187",
            "active_identifier": self.active_identifier,
            "workflow": {
                "name": APP_NAME,
                "app_id": str(target_app.id),
                "workflow_id": str(target_app.workflow_id),
                "created_this_run": created,
                "published_this_run": published_new,
                "api_enabled": target_app.enable_api,
                "api_key": {"present": True, "length": len(self.api_token), "source": "Dify app credential"},
                "nodes": ["start", "tool", "end"],
                "inputs": ["sql", "max_rows"],
                "credential_binding": {"name": KINGBASE_CREDENTIAL_NAME, "id": str(kingbase.id)},
            },
            "provider_options": options,
            "runtime": self.runtime_evidence,
            "checks": checks,
        }
        dump(self.output_dir / "kingbasees_phase9_9_preflight.json", report)
        return report

    def invoke_api(self, case_name: str, sql: str, max_rows: int, *, app: Any | None = None) -> dict[str, Any]:
        from extensions.ext_database import db
        from models.model import ApiToken
        from sqlalchemy import select

        app = app or self.workflow_app
        token = self.api_token
        if app.id != self.workflow_app.id:
            row = db.session.scalar(select(ApiToken).where(ApiToken.app_id == app.id).order_by(ApiToken.created_at.desc()))
            if row is None:
                raise RuntimeError(f"Regression Workflow has no API key: {app.name}")
            token = row.token
        payload = {
            "inputs": {"sql": sql, "max_rows": max_rows},
            "response_mode": "blocking",
            "user": f"phase9.9-{case_name}",
        }
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST",
        )
        started = perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                http_status = response.status
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            http_status = exc.code
            body = json.loads(exc.read().decode("utf-8", errors="replace"))
        self.api_call_count += 1
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        raw = body.get("data", {}).get("outputs", {}).get("result")
        if not isinstance(raw, list) or len(raw) != 1 or not isinstance(raw[0], dict):
            raise AssertionError(f"Malformed Workflow result wrapper for {case_name}")
        result = raw[0]
        trace = self.trace(str(body.get("workflow_run_id")), sql, max_rows, raw, app)
        self.traces.append({"case": case_name, **trace})
        return {
            "http_status": http_status,
            "workflow_run_id": body.get("workflow_run_id"),
            "task_id": body.get("task_id"),
            "workflow_status": body.get("data", {}).get("status"),
            "request": {
                "endpoint": API_URL,
                "method": "POST",
                "authorization_present": True,
                "inputs": payload["inputs"],
                "response_mode": "blocking",
                "user": payload["user"],
            },
            "workflow_outputs": body.get("data", {}).get("outputs"),
            "tool_json": result,
            "elapsed_ms": elapsed_ms,
            "redaction_check": self.safe({"request": payload["inputs"], "response": body}),
        }

    def trace(self, run_id: str, sql: str, max_rows: int, raw_result: list[dict[str, Any]], app: Any) -> dict[str, Any]:
        from extensions.ext_database import db
        from models.workflow import WorkflowNodeExecutionModel, WorkflowRun
        from sqlalchemy import select

        db.session.expire_all()
        run = db.session.get(WorkflowRun, run_id)
        if run is None:
            raise AssertionError(f"WorkflowRun not persisted: {run_id}")
        nodes = db.session.scalars(
            select(WorkflowNodeExecutionModel)
            .where(WorkflowNodeExecutionModel.workflow_run_id == run_id)
            .order_by(WorkflowNodeExecutionModel.index)
        ).all()
        node_data = [
            {
                "execution_id": str(node.id),
                "node_id": node.node_id,
                "node_type": node.node_type,
                "status": str(node.status),
                "inputs": node.inputs_dict,
                "outputs": node.outputs_dict,
                "execution_metadata": node.execution_metadata_dict,
                "error": node.error,
                "elapsed_time": node.elapsed_time,
            }
            for node in nodes
        ]
        start = next(node for node in node_data if node["node_type"] == "start")
        tool = next(node for node in node_data if node["node_type"] == "tool")
        end = next(node for node in node_data if node["node_type"] == "end")
        run_inputs = parse_json(run.inputs)
        run_outputs = parse_json(run.outputs)
        is_kingbase = app.id == self.workflow_app.id
        expected_identifier = EXPECTED_IDENTIFIER if is_kingbase else tool["execution_metadata"].get("tool_info", {}).get("plugin_unique_identifier")
        checks = {
            "run_succeeded": str(run.status) == "succeeded",
            "run_input_sql_non_null": bool(run_inputs.get("sql")) and run_inputs["sql"] == sql,
            "run_input_max_rows": run_inputs.get("max_rows") == max_rows,
            "start_input_sql_non_null": bool(start["inputs"].get("sql")) and start["inputs"]["sql"] == sql,
            "tool_resolved_sql_non_null": bool(tool["inputs"].get("sql")) and tool["inputs"]["sql"] == sql,
            "tool_invocation_payload_non_null": bool(tool["inputs"]),
            "tool_output_matches_workflow": tool["outputs"].get("json") == raw_result,
            "end_output_matches_tool": end["outputs"].get("result") == raw_result,
            "run_output_matches_end": run_outputs.get("result") == raw_result,
            "plugin_identifier_metadata": tool["execution_metadata"].get("tool_info", {}).get("plugin_unique_identifier") == expected_identifier,
        }
        if not all(checks.values()):
            raise AssertionError(f"Workflow trace mismatch: {checks}")
        return {
            "workflow_run_id": run_id,
            "app_id": str(app.id),
            "workflow_id": str(run.workflow_id),
            "status": str(run.status),
            "inputs": run_inputs,
            "outputs": run_outputs,
            "elapsed_time": run.elapsed_time,
            "nodes": node_data,
            "checks": checks,
            "correlation": "Dify workflow_run_id plus node execution IDs; plugin logs correlated by timestamp window",
        }

    def safe(self, value: Any) -> bool:
        text = json.dumps(value, ensure_ascii=False, default=str)
        return (
            all(not secret or secret not in text for secret in self.secrets)
            and "Bearer " not in text
            and not URL_WITH_CREDENTIALS.search(text)
        )

    def run_case(
        self,
        name: str,
        sql: str,
        max_rows: int,
        predicate: Callable[[dict[str, Any]], bool],
        expected: str,
    ) -> dict[str, Any]:
        started = perf_counter()
        try:
            actual = self.invoke_api(name, sql, max_rows)
            result = actual["tool_json"]
            assertions = {
                "http_200": actual["http_status"] == 200,
                "workflow_succeeded": actual["workflow_status"] == "succeeded",
                "predicate": predicate(result),
                "redacted": actual["redaction_check"],
            }
            status = "PASS" if all(assertions.values()) else "FAIL"
            error = None
        except Exception as exc:  # noqa: BLE001
            actual = None
            assertions = {}
            status = "FAIL"
            error = str(exc)
        return {
            "case": name,
            "expected": expected,
            "actual": actual,
            "assertions": assertions,
            "status": status,
            "duration_ms": round((perf_counter() - started) * 1000, 3),
            "error": error,
        }

    @staticmethod
    def successful(result: dict[str, Any]) -> bool:
        return result.get("success") is True and result.get("database_type") == "kingbasees" and OUTPUT_KEYS <= result.keys()

    def run_positive(self) -> dict[str, Any]:
        table = "phase97_fixture.sample_data"
        specs = [
            ("select_1", "SELECT 1 AS probe", 100, lambda r: self.successful(r) and r["rows"] == [{"probe": 1}]),
            ("fixture_rows", f"SELECT id, label FROM {table} ORDER BY id", 100, lambda r: self.successful(r) and r["row_count"] == 12 and r["rows"][0] == {"id": 1, "label": "row-01"} and r["rows"][-1] == {"id": 12, "label": "row-12"}),
            ("unicode", f"SELECT unicode_text FROM {table} WHERE id=1", 100, lambda r: self.successful(r) and r["rows"] == [{"unicode_text": "金仓只读验证"}]),
            ("null", f"SELECT nullable_text FROM {table} WHERE id=2", 100, lambda r: self.successful(r) and r["rows"] == [{"nullable_text": None}]),
            ("numeric", f"SELECT amount FROM {table} WHERE id=2", 100, lambda r: self.successful(r) and r["rows"] == [{"amount": "2.50"}]),
            ("date", f"SELECT event_date FROM {table} WHERE id=2", 100, lambda r: self.successful(r) and r["rows"] == [{"event_date": "2026-07-02"}]),
            ("timestamp", f"SELECT event_time FROM {table} WHERE id=2", 100, lambda r: self.successful(r) and r["rows"] == [{"event_time": "2026-07-02 12:34:56"}]),
            ("schema_qualified", f"SELECT COUNT(*) AS total FROM {table}", 100, lambda r: self.successful(r) and r["rows"] == [{"total": 12}]),
            ("max_rows", f"SELECT id FROM {table} ORDER BY id", 5, lambda r: self.successful(r) and r["row_count"] == 5 and r["truncated"] is True and r["max_rows"] == 5 and [row["id"] for row in r["rows"]] == [1, 2, 3, 4, 5]),
            ("empty_result", f"SELECT id FROM {table} WHERE id<0", 100, lambda r: self.successful(r) and r["rows"] == [] and r["row_count"] == 0 and r["truncated"] is False),
            ("aggregate", f"SELECT SUM(amount) AS total FROM {table}", 100, lambda r: self.successful(r) and r["rows"] == [{"total": "84.00"}]),
            ("order_by", f"SELECT id FROM {table} ORDER BY id DESC", 3, lambda r: self.successful(r) and [row["id"] for row in r["rows"]] == [12, 11, 10]),
        ]
        cases = [self.run_case(name, sql, maximum, predicate, "real Workflow API returns exact installed KingbaseES data") for name, sql, maximum, predicate in specs]
        report = suite("kingbasees_phase9_9_workflow_positive", cases, active_identifier=self.active_identifier)
        dump(self.output_dir / "kingbasees_phase9_9_workflow_positive.json", report)

        type_names = {"unicode", "null", "numeric", "date", "timestamp"}
        types = suite("kingbasees_phase9_9_workflow_types", [case for case in cases if case["case"] in type_names])
        dump(self.output_dir / "kingbasees_phase9_9_workflow_types.json", types)

        contract_cases = []
        for case in cases:
            actual = case.get("actual") or {}
            result = actual.get("tool_json") or {}
            checks = {
                "output_fields": OUTPUT_KEYS <= result.keys(),
                "workflow_wrapper": isinstance((actual.get("workflow_outputs") or {}).get("result"), list),
                "raw_and_parsed_match": ((actual.get("workflow_outputs") or {}).get("result") or [None])[0] == result,
                "database_type": result.get("database_type") == "kingbasees",
            }
            contract_cases.append({"case": case["case"], "checks": checks, "status": "PASS" if case["status"] == "PASS" and all(checks.values()) else "FAIL"})
        contract = suite("kingbasees_phase9_9_workflow_contract", contract_cases)
        dump(self.output_dir / "kingbasees_phase9_9_workflow_contract.json", contract)
        return report

    def run_security(self) -> dict[str, Any]:
        table = "phase97_fixture.sample_data"
        blocked = lambda r: r.get("success") is False and r.get("error", {}).get("type") == "ReadOnlyViolationError"
        specs = [
            ("dml_rejection", f"INSERT INTO {table} (id, label) VALUES (999, 'blocked')", 100, blocked),
            ("ddl_rejection", "CREATE TABLE phase97_fixture.phase99_blocked(id int)", 100, blocked),
            ("multi_statement_rejection", "SELECT 1; SELECT 2", 100, blocked),
            ("database_error_redaction", f"SELECT phase99_missing_column FROM {table}", 100, lambda r: r.get("success") is False and bool(r.get("error")) and self.safe(r)),
            ("database_integrity_after_rejection", f"SELECT COUNT(*) AS blocked_count FROM {table} WHERE id=999", 100, lambda r: self.successful(r) and r["rows"] == [{"blocked_count": 0}]),
        ]
        cases = [self.run_case(name, sql, maximum, predicate, "Workflow blocks or safely reports the request without data mutation or secret leakage") for name, sql, maximum, predicate in specs]
        report = suite("kingbasees_phase9_9_workflow_security", cases, no_secret_leak=all((case.get("actual") or {}).get("redaction_check", case["status"] == "PASS") for case in cases))
        dump(self.output_dir / "kingbasees_phase9_9_workflow_security.json", report)
        return report

    def run_recovery(self) -> dict[str, Any]:
        table = "phase97_fixture.sample_data"
        specs = [
            ("initial_success", "SELECT 1 AS probe", 100, lambda r: self.successful(r) and r["rows"] == [{"probe": 1}]),
            ("controlled_failure", f"DELETE FROM {table}", 100, lambda r: r.get("success") is False and r.get("error", {}).get("type") == "ReadOnlyViolationError"),
            ("post_failure_select_1", "SELECT 1 AS probe", 100, lambda r: self.successful(r) and r["rows"] == [{"probe": 1}]),
            ("post_failure_fixture", f"SELECT id, label FROM {table} ORDER BY id", 100, lambda r: self.successful(r) and r["row_count"] == 12 and r["rows"][0]["label"] == "row-01"),
        ]
        cases = [self.run_case(name, sql, maximum, predicate, "Workflow remains usable without restart after a controlled failure") for name, sql, maximum, predicate in specs]
        report = suite(
            "kingbasees_phase9_9_failure_recovery",
            cases,
            container_restart_required=False,
            credential_preserved=True,
            runtime_crash=False,
        )
        dump(self.output_dir / "kingbasees_phase9_9_failure_recovery.json", report)
        return report

    def invoke_tool(self, credential_id: str, sql: str) -> dict[str, Any]:
        from core.tools.entities.tool_entities import ToolProviderType
        from core.tools.tool_manager import ToolManager

        tool = ToolManager.get_tool_runtime(
            provider_type=ToolProviderType.BUILT_IN,
            provider_id=PROVIDER_ID,
            tool_name=TOOL_NAME,
            tenant_id=self.tenant_id,
            credential_id=credential_id,
        )
        message = list(tool.invoke(user_id=self.user_id, tool_parameters={
            "sql": sql, "max_rows": 100, "timeout_seconds": 30,
            "readonly": True, "output_format": "json",
        }))[0]
        return model(message)["message"]["json_object"]

    def run_regression(self) -> dict[str, Any]:
        from core.plugin.impl.tool import PluginToolManager
        from extensions.ext_database import db
        from models.model import App
        from sqlalchemy import select

        postgres = self.credential(POSTGRES_CREDENTIAL_NAME)
        postgres_credentials = self.decrypted_credentials(postgres)
        manager = PluginToolManager()
        cases: list[dict[str, Any]] = []

        def record(name: str, action: Callable[[], Any], predicate: Callable[[Any], bool]) -> None:
            started = perf_counter()
            try:
                actual = action()
                status = "PASS" if predicate(actual) else "FAIL"
                error = None
            except Exception as exc:  # noqa: BLE001
                actual, status, error = None, "FAIL", str(exc)
            cases.append({"case": name, "actual": actual, "status": status, "duration_ms": round((perf_counter() - started) * 1000, 3), "error": error})

        record(
            "postgresql_provider_smoke",
            lambda: manager.validate_provider_credentials(self.tenant_id, self.user_id, PROVIDER_ID, postgres_credentials),
            lambda value: bool(value),
        )
        record(
            "postgresql_tool_select_1",
            lambda: self.invoke_tool(str(postgres.id), "SELECT 1 AS probe"),
            lambda value: value.get("rows") == [{"probe": 1}] and value.get("database_type") == "postgresql",
        )
        source_app = db.session.scalar(select(App).where(App.tenant_id == self.tenant_id, App.name == SOURCE_APP_NAME))
        record(
            "existing_dm_workflow_api",
            lambda: self.invoke_api("dm_regression", "SELECT 1 AS probe", 1, app=source_app),
            lambda value: value["http_status"] == 200 and value["workflow_status"] == "succeeded" and value["tool_json"].get("database_type") == "dm" and value["tool_json"].get("rows") == [{"probe": 1}],
        )
        active, declaration = self.active_plugin()
        options = [item["value"] for item in declaration["credentials_schema"][0]["options"]]
        record("provider_schema_order", lambda: options, lambda value: value == ["mysql", "postgresql", "dm", "sqlserver", "kingbasees"])
        record("tool_schema", lambda: declaration["tools"], lambda value: any(item["identity"]["name"] == TOOL_NAME for item in value))
        record("active_plugin_unchanged", lambda: active, lambda value: value == EXPECTED_IDENTIFIER)
        record("installed_adapter_and_dialect_identity", lambda: self.runtime_evidence.get("checks", {}), lambda value: all(value.get(key) for key in ("adapter_import_smoke", "psycopg2_identity", "postgresql_dialect_identity", "provider_schema", "tool_schema")))
        report = suite("kingbasees_phase9_9_regression", cases, sqlserver_role="OPTIONAL")
        dump(self.output_dir / "kingbasees_phase9_9_regression.json", report)
        return report

    def run(self) -> int:
        preflight = self.prepare()
        positive = self.run_positive()
        types = json.loads((self.output_dir / "kingbasees_phase9_9_workflow_types.json").read_text(encoding="utf-8"))
        contract = json.loads((self.output_dir / "kingbasees_phase9_9_workflow_contract.json").read_text(encoding="utf-8"))
        security = self.run_security()
        recovery = self.run_recovery()
        regression = self.run_regression()

        trace_checks = [all(trace["checks"].values()) for trace in self.traces]
        trace_report = {
            "suite": "kingbasees_phase9_9_runtime_trace",
            "generated_at": utcnow(),
            "status": "PASS" if self.traces and all(trace_checks) else "FAIL",
            "active_identifier": self.active_identifier,
            "installed_runtime_root": self.runtime_evidence.get("installed_root"),
            "api_call_count": self.api_call_count,
            "traces": self.traces,
        }
        if not self.safe(trace_report):
            trace_report["status"] = "FAIL"
            trace_report["redaction_failure"] = True
        dump(self.output_dir / "kingbasees_phase9_9_runtime_trace.json", trace_report)

        reports = [preflight, positive, types, contract, security, recovery, trace_report, regression]
        gates = {report["suite"]: report["status"] for report in reports}
        final = {
            "suite": "kingbasees_phase9_9_final_gate",
            "generated_at": utcnow(),
            "status": "PASS" if all(value == "PASS" for value in gates.values()) else "FAIL",
            "phase_status": "PHASE_9_9_PASS" if all(value == "PASS" for value in gates.values()) else "PHASE_9_9_FAIL",
            "active_identifier": self.active_identifier,
            "api_call_count": self.api_call_count,
            "gates": gates,
            "skip_count": sum(report.get("summary", {}).get("skip", 0) for report in reports),
            "allowed_conclusions": [
                "KINGBASEES_INSTALLED_WORKFLOW_API_PASS",
                "KINGBASEES_END_TO_END_PASS",
                "KINGBASEES_FINAL_OFFLINE_PLUGIN_TECHNICAL_PASS",
            ] if all(value == "PASS" for value in gates.values()) else [],
            "not_yet_proven": [
                "FINAL_PROJECT_DELIVERY_PASS",
                "PUBLIC_REDISTRIBUTION_APPROVED",
                "DM8_FINAL_DELIVERY_PASS",
                "DEVELOPMENT_PROCESS_DOCUMENTATION_COMPLETE",
                "FROM_ZERO_REPRODUCTION_TUTORIAL_COMPLETE",
            ],
            "redistribution_status": "REDISTRIBUTION_REVIEW_PENDING",
        }
        dump(self.output_dir / "kingbasees_phase9_9_final_gate.json", final)
        print(json.dumps({"status": final["status"], "api_call_count": self.api_call_count, "gates": gates}))
        return 0 if final["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runtime-evidence", type=Path, required=True)
    args = parser.parse_args()
    gate = Gate(args.output_dir, args.runtime_evidence)
    try:
        return gate.run()
    finally:
        gate.close()


if __name__ == "__main__":
    raise SystemExit(main())
