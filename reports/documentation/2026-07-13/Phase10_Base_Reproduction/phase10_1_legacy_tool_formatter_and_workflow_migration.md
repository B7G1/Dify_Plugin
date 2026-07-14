# Phase 10.1 — Legacy-Compatible Tool, Formatter and Workflow Migration

- Date: 2026-07-13
- Phase: Phase 10.1 — Base Plugin Reproduction
- Status: PASS
- Database: MySQL, PostgreSQL, MSSQL legacy path; Oracle/Oracle11g controlled not-yet-implemented status
- Scope: legacy Tool contract implementation, formatter modes, shared-core integration, DSL migration utility, and regression checks
- Source commit: `0700f82`
- Runtime: `db_query_extended/.venv` Python 3.11; local MySQL/PostgreSQL fixtures; Dify SDK source import
- Canonical path: `reports/documentation/2026-07-13/Phase10_Base_Reproduction/phase10_1_legacy_tool_formatter_and_workflow_migration.md`
- Machine evidence: `reports/verification/2026-07-13/phase10_1_final_gate.json`
- Logs: `reports/logs/2026-07-13/Phase10_Base_Reproduction/phase10_1_*.log`
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / REDACTED / NO_REAL_CREDENTIALS_RETAINED

## Executive Summary

Added a separate `legacy_database_query` Provider/Tool without altering the Modern Tool contract. It accepts the original frozen nine external parameters, reuses the existing read-only execution core, preserves `mssql` externally, renders legacy Markdown or `{ "records": [...] }`, and keeps legacy NULL as `""` only at the presentation boundary.

## Goal and Acceptance Boundary

This implements the Phase 10.0 design. It does not prove installed-plugin runtime, Oracle, Oracle11g, a real legacy Workflow, full Markdown fixture parity, five-database reproduction, or final delivery.

## Baseline and Code Audit

At `0700f82`, Modern Tool execution was `Tool → validate_tool_parameters → Provider credentials → execute_read_only_query → normalized result → structured JSON`. Reused shared components are `ReadOnlyValidator`, `validate_connection_config`, `execute_read_only_query`, the Adapter registry, engine lifecycle, and normalized result rows. Modern coupling remains limited to Provider credentials and `success_response`; it was not changed.

## Work Performed

- Registered a second provider in `manifest.yaml`.
- Added `legacy_database_query` YAML and Python entrypoints under project-owned identity `li_zijun`.
- Added `utils/legacy.py`: frozen-name validation, `mssql → sqlserver` internal mapping, formatter dispatch, and shared-core execution.
- Allowed `validate_connection_config(..., require_database=False)` only for the legacy path because original `db_name` is optional; Modern behavior remains the default.
- Added a dry-run, output-only, idempotent Workflow DSL migration utility.
- Added a repeatable Phase 10.1 gate; no production database execution stack was copied.

## Legacy Tool Contract and Mapping

The exact frozen parameter order is `db_type`, `db_host`, `db_port`, `db_username`, `db_password`, `db_name`, `db_properties`, `query_sql`, `output_format`; YAML was compared structurally against the Phase 10.0 raw contract.

| Legacy value | Internal value | Status |
| --- | --- | --- |
| `mysql` | `mysql` | implemented |
| `postgresql` | `postgresql` | implemented |
| `mssql` | `sqlserver` | implemented; external value retained |
| `oracle` | — | controlled `UnsupportedDatabaseTypeError` |
| `oracle11g` | — | controlled `UnsupportedDatabaseTypeError` |

## Formatter and NULL Behavior

`FormatterMode` dispatches `modern_json`, `legacy_json_records`, and `legacy_markdown` without mutating the normalized result. Legacy JSON contains only `records`; NULL becomes `""`. Modern rows retain `null`. The archived `SELECT 1` Markdown golden passes exactly. Generic Markdown escapes pipes and newlines; additional real-runtime Markdown fixtures remain pending rather than guessed. Duplicate legacy column names are rejected because an object cannot preserve them safely.

## Workflow Migration

`scripts/migrate_legacy_workflow.py` supports JSON/YAML, `--dry-run`, separate `--output`, optional `--backup`, idempotent reruns, and a concise redacted summary. It only rewrites recognized `db_query/sql_query` nodes after all nine inputs are present, retaining bindings and downstream nodes. Unsupported DSL shapes or incomplete legacy inputs return `BLOCKED`. The fixture is created in a temporary directory and proves logic only, not Dify Workflow runtime.

## Security and Redaction

Inline credentials are never logged by the mapper or migration summary. The legacy Tool uses the existing conservative validator; CTE DELETE, SELECT INTO, INTO OUTFILE, FOR UPDATE, and multi-statements remain blocked. Oracle states are controlled errors, not fake successes. No real password, URL, token, or database error traceback is persisted.

## Verification Results

- Phase 10.1 gate: PASS — contract 7/7, formatter 8/8, security 9/9, mapping 6/6, migration 6/6.
- Legacy Dify Provider/Tool import: PASS.
- Existing `phase2_matrix.py`: 76 PASS, 0 FAIL, 1 SKIP. The SKIP is only a missing `DIFY_WORKFLOW_API_URL`/key; it is not counted as Workflow PASS.

## Commands Executed

```powershell
E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe db_query_extended\verification\phase10_1_gate.py --output reports\verification\2026-07-13\phase10_1_final_gate.json
E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe db_query_extended\verification\phase2_matrix.py
```

Expected results: Phase 10.1 gate PASS; existing regression has zero failures. A Workflow API skip means only that the configured API environment was absent.

## Files Changed

`manifest.yaml`; `provider/legacy_database_query.{yaml,py}`; `tools/legacy_database_query.{yaml,py}`; `utils/legacy.py`; `utils/validation.py`; `scripts/migrate_legacy_workflow.py`; `verification/phase10_1_gate.py`; Phase 10.1 report/evidence/log files; `REPORT_MAP.md`.

## Known Limits and Abandoned Paths

No dependency was added merely to copy the reference package's `tabulate` renderer; the exact known golden is preserved and unobserved formats remain pending fixtures. No full duplicate executor was created. Legacy `db_properties` maps the safe core's `schema`, `charset`, and `ssl_mode`; database-specific arbitrary URL-property parity remains a later database-contract gate.

## Git State

Only Phase 10.1 source, verification, log, and report paths are eligible for staging. The pre-existing interactive-map, `analysis/`, `archive/`, environment/probe, and other user worktree changes are untouched.

## Final Decision

```text
PHASE_STATUS: PHASE_10_1_PASS
ALLOWED_CONCLUSIONS:
LEGACY_TOOL_IMPLEMENTED
LEGACY_FORMATTERS_IMPLEMENTED
WORKFLOW_MIGRATION_UTILITY_IMPLEMENTED
MODERN_TOOL_REGRESSION_ZERO_FAIL
NOT_YET_PROVEN:
ORIGINAL_BASE_PLUGIN_REPRODUCTION_CONFIRMED
ORACLE_REPRODUCTION_PASS
ORACLE11G_REPRODUCTION_PASS
LEGACY_WORKFLOW_MIGRATION_PASS
FINAL_PROJECT_DELIVERY_PASS
```

## Next Step

Phase 10.2 should execute MySQL, PostgreSQL, and MSSQL through the installed legacy path, compare real legacy output fixtures, and validate a real migrated Workflow without widening the frozen contract.
