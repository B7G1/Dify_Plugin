"""Fail-closed Phase 10.2 evidence aggregator."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime, workflow = load(args.runtime), load(args.workflow)
    runtime_pass = runtime.get("status") == "PASS"
    workflow_pass = workflow.get("status") == "PASS"
    status = "PASS" if runtime_pass and workflow_pass else "PARTIAL" if runtime_pass and workflow.get("status") == "BLOCKED" else "FAIL"
    report: dict[str, Any] = {
        "suite": "phase10_2_final_gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "phase_status": f"PHASE_10_2_{status}",
        "source_starting_commit": runtime.get("source_starting_commit"),
        "source_ending_commit": runtime.get("source_commit"),
        "candidate": runtime.get("candidate"),
        "installed_identifier": runtime.get("active_identifier"),
        "gates": {"installed_legacy_runtime": runtime.get("status"), "real_workflow_migration_and_api": workflow.get("status")},
        "workflow_blockers": workflow.get("blockers", []),
        "allowed_conclusions": ["LEGACY_INSTALLED_TOOL_RUNTIME_THREE_DATABASE_PASS", "PHASE_10_2_PARTIAL"] if status == "PARTIAL" else (["PHASE_10_2_PASS"] if status == "PASS" else []),
        "not_proven": ["LEGACY_WORKFLOW_MIGRATION_PASS", "ORACLE_REPRODUCTION_PASS", "ORACLE11G_REPRODUCTION_PASS", "DM8_FINAL_DELIVERY_PASS", "KINGBASEES_FINAL_DELIVERY_PASS", "FINAL_PROJECT_DELIVERY_PASS"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "gates": report["gates"]}))
    return 0 if status in {"PASS", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
