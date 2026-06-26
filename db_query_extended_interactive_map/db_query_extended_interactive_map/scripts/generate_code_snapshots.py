"""Refresh offline-readable cumulative code snapshots for the interactive map.

The original 2026-06-23 map contains historical Step 1-12 snapshots.  When this
script extends the map, it preserves those existing cumulative states and only
adds Step 13+ snapshots from the current real workspace and archived reports.
Large/binary/runtime artifacts are represented by summaries.
"""
from __future__ import annotations

import json
from pathlib import Path

MAP_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = MAP_ROOT.parents[1]
PLUGIN_ROOT = WORKSPACE_ROOT / "db_query_extended"
GENERATED = MAP_ROOT / "assets" / "code-snapshots.generated.js"
SNAPSHOT_ROOT = MAP_ROOT / "assets" / "code-snapshots"


NEW_STEPS: dict[str, list[str]] = {
    "step-13-platform-restore": [
        "reports/verification/2026-06-25/plugin_daemon_logs.txt",
        "reports/verification/2026-06-25/final_verification_matrix.md",
    ],
    "step-14-workflow-app": [
        "reports/verification/2026-06-25/workflow_mysql_result.json",
        "reports/verification/2026-06-25/workflow_postgresql_result.json",
    ],
    "step-15-mysql-workflow-pass": [
        "reports/verification/2026-06-25/workflow_mysql_result.json",
        "reports/verification/2026-06-25/api_logs.txt",
    ],
    "step-16-postgresql-workflow-pass": [
        "reports/verification/2026-06-25/workflow_postgresql_result.json",
        "utils/database.py",
    ],
    "step-17-error-path-pass": [
        "tools/db_query_extended.py",
        "reports/verification/2026-06-25/final_verification_matrix.md",
    ],
    "step-18-phase3-evidence-archive": [
        "reports/verification/2026-06-25/README.md",
        "reports/verification/2026-06-25/verify_plugin_output.txt",
        "reports/verification/2026-06-25/final_verification_matrix.md",
    ],
    "step-19-database-core-freeze": [
        "utils/database.py",
    ],
    "step-20-formatter-core": [
        "utils/formatter.py",
        "utils/database.py",
    ],
    "step-21-sql-readonly-validator": [
        "utils/sql_validator.py",
        "utils/validation.py",
    ],
    "step-22-tool-and-matrix": [
        "tools/db_query_extended.py",
        "verification/phase2_matrix.py",
        "reports/verification/2026-06-26/phase2_verification_report.json",
    ],
    "step-23-doc-verification-split": [
        "reports/README.md",
        "reports/documentation/README.md",
        "reports/verification/README.md",
        "reports/documentation/Phase4_Core_Freeze/2026-06-26/README.md",
    ],
    "step-24-cockpit-and-map": [
        "reports/html_reports/2026-06-24/project_dashboard.html",
        "README.md",
        "INDEX.md",
        "assets/timeline-data.js",
        "assets/file-metadata.js",
        "assets/code-snapshots.generated.js",
    ],
}


SUMMARIES: dict[str, str] = {
    "step-13-platform-restore/platform-restore-summary.txt": (
        "2026-06-25: Dify Console recovered. plugin-daemon recovered and loaded "
        "li_zijun/db_query_extended:0.0.1. Evidence is archived under "
        "reports/verification/2026-06-25.\n"
    ),
    "step-14-workflow-app/workflow-app-summary.txt": (
        "Workflow App Plu_Test was created and published. It became the fixed "
        "UI/API verification target for MySQL and PostgreSQL.\n"
    ),
    "step-18-phase3-evidence-archive/phase3-verification-summary.txt": (
        "Phase 3 final baseline: verify_plugin.ps1 reported 57 PASS / 0 FAIL / "
        "0 SKIP. MySQL Workflow UI, PostgreSQL Workflow UI, Workflow API, and "
        "wrong-password path passed.\n"
    ),
    "step-24-cockpit-and-map/git-sync-summary.txt": (
        "Local commits exist for Cockpit localization and this interactive map "
        "continuation. Remote push is intentionally not marked complete unless "
        "explicitly approved and executed.\n"
    ),
}


def load_existing_cumulative() -> dict[str, dict[str, str]]:
    if not GENERATED.exists():
        return {}
    text = GENERATED.read_text(encoding="utf-8", errors="replace").strip()
    prefix = "window.CODE_SNAPSHOTS = "
    if not text.startswith(prefix):
        return {}
    payload = text[len(prefix):].rstrip(";")
    return json.loads(payload)


def read_workspace_file(relative: str) -> str:
    if relative.startswith("assets/"):
        source = MAP_ROOT / relative
    elif relative.startswith("reports/") or relative in {"README.md", "INDEX.md"}:
        source = WORKSPACE_ROOT / relative
    else:
        source = PLUGIN_ROOT / relative
    if not source.exists():
        return f"待确认：当前工作区中找不到 {relative}，未伪造旧代码。\n"
    if source.is_dir():
        return f"{relative} is a directory. Full directory contents are not copied.\n"
    return source.read_text(encoding="utf-8", errors="replace")


def write_incremental_snapshot(step: str, relative: str, content: str) -> None:
    target = SNAPSHOT_ROOT / step / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> None:
    cumulative = load_existing_cumulative()
    if cumulative:
        state = dict(cumulative.get("step-12-workflow-sql", next(reversed(cumulative.values()))))
    else:
        state = {}

    for step, paths in NEW_STEPS.items():
        for relative in paths:
            content = read_workspace_file(relative)
            write_incremental_snapshot(step, relative, content)
            state[relative] = content
        for key, content in SUMMARIES.items():
            summary_step, relative = key.split("/", 1)
            if summary_step == step:
                write_incremental_snapshot(step, relative, content)
                state[relative] = content
        cumulative[step] = dict(state)

    GENERATED.write_text(
        "window.CODE_SNAPSHOTS = " + json.dumps(cumulative, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    for step in NEW_STEPS:
        print(f"{step}: {len(cumulative[step])} cumulative files")


if __name__ == "__main__":
    main()
