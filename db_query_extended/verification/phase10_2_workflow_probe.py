"""Record why real Legacy Workflow migration cannot run in the current Dify baseline."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def endpoint_status(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return {"reachable": True, "http_status": response.status}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"reachable": False, "error_type": type(exc).__name__}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from app_factory import create_app
    from extensions.ext_database import db
    from models.model import App
    from models.workflow import Workflow

    app = create_app()
    context = app.app_context()
    context.push()
    try:
        workflows: list[dict[str, Any]] = []
        for workflow_app in db.session.query(App).filter(App.mode == "workflow").order_by(App.created_at.desc()).all():
            workflow = db.session.get(Workflow, workflow_app.workflow_id) if workflow_app.workflow_id else None
            graph = str(workflow.graph) if workflow else ""
            workflows.append({
                "name": workflow_app.name,
                "workflow_present": workflow is not None,
                "graph_length": len(graph),
                "contains_original_provider_db_query": '"provider_id": "db_query"' in graph,
                "contains_original_tool_sql_query": '"tool_name": "sql_query"' in graph,
                "contains_current_provider_marker": "db_query" in graph,
            })
        console = endpoint_status("http://nginx/console/api/ping")
        workflow_api = endpoint_status("http://nginx/v1/workflows/run")
        legacy_dsl_present = any(item["contains_original_provider_db_query"] and item["contains_original_tool_sql_query"] for item in workflows)
        report: dict[str, Any] = {
            "suite": "phase10_2_real_workflow_prerequisite_probe",
            "generated_at": utcnow(),
            "status": "PASS" if legacy_dsl_present and console["reachable"] and workflow_api["reachable"] else "BLOCKED",
            "workflows": workflows,
            "legacy_dsl_present": legacy_dsl_present,
            "console": console,
            "workflow_api": workflow_api,
            "not_run": ["real_legacy_dsl_migration", "workflow_import", "workflow_publish", "six_database_format_workflow_runs"],
            "blockers": [],
        }
        if not legacy_dsl_present:
            report["blockers"].append("No historical Dify Workflow with original provider_id=db_query and tool_name=sql_query is available; synthetic DSL is prohibited.")
        if not console["reachable"] or not workflow_api["reachable"]:
            report["blockers"].append("Dify api/nginx containers are unavailable because Docker Desktop WSL bind-mount sources are missing.")
        dump(args.output, report)
        print(json.dumps({"status": report["status"], "workflow_count": len(workflows), "legacy_dsl_present": legacy_dsl_present}))
        return 0 if report["status"] == "PASS" else 2
    finally:
        context.pop()


if __name__ == "__main__":
    raise SystemExit(main())
