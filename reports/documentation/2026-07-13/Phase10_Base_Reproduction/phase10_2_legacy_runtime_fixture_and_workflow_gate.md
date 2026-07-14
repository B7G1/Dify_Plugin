# Phase 10.2 — Legacy Runtime Three-Database Fixtures and Workflow Gate

- Date: 2026-07-13
- Status: `PHASE_10_2_PARTIAL`
- Scope: installed Dify Legacy Tool runtime for MySQL, PostgreSQL, and MSSQL; raw output fixture capture; Modern regression; real Workflow prerequisite probe
- Start commit: `8ef7306`
- End commit: `7b688be`
- Canonical evidence: `reports/verification/2026-07-13/phase10_2_final_gate.json`
- Security: `INTERNAL / REDACTED / NO_CREDENTIALS_RETAINED`

## Decision

The installed Legacy Tool path is proven for all three in-scope databases and both requested formats. Phase 10.2 is nevertheless `PARTIAL`, not PASS: no genuine original `db_query/sql_query` Workflow DSL exists in the active Dify database, and the Dify `api` and `nginx` containers cannot start because their Docker Desktop WSL bind-mount sources are missing. Synthetic DSL, fake import/publish, and invented six-run Workflow evidence were not used.

## Installed Candidate and Runtime Result

The final candidate was built from a clean detached worktree at `7b688be`, with the existing 44-wheel offline input set copied as an external build input. It was uploaded through Dify `PluginService`, installed, and upgraded through `PluginInstaller`; the active identifier is:

```text
li_zijun/db_query_extended:0.1.1@a528b17bd19f6e3aeed58e8db92f6b25c2ddb372c2bb8d0398bc0447da7293ec
```

| Field | Value |
| --- | --- |
| Candidate filename | `db_query_extended-0.1.1-phase10_2-providerfix.difypkg` |
| Size | 35,053,156 bytes |
| SHA-256 | `244B82EE270001303F6F0C9F4B07D80148BDDD289808203EEEDB005F89271055` |
| Dify checksum | `a528b17bd19f6e3aeed58e8db92f6b25c2ddb372c2bb8d0398bc0447da7293ec` |
| Package content | 44 wheels; manifest, shared core, Modern Tool, and Legacy Tool present |

The final installed-runtime gate passed. It captures actual `ToolManager -> plugin-daemon` messages, not a direct `utils.legacy` call.

| Database | Markdown table read | Legacy JSON table read | NULL/Unicode/table evidence | `SELECT 1` original Markdown |
| --- | --- | --- | --- | --- |
| MySQL | PASS | PASS | PASS | exact PASS |
| PostgreSQL | PASS | PASS | PASS | exact PASS |
| MSSQL | PASS | PASS | PASS; `TOP` and schema-qualified table | exact PASS |

The six raw fixtures are under `reports/verification/2026-07-13/phase10_2_runtime/phase10_2_runtime_fixtures/`. Each records database, query id/SHA-256, format, installed checksum, source commit, UTF-8/LF metadata, checks, and unedited runtime output. The JSON fixtures contain only `{ "records": [...] }`; runtime NULL values are `""` at the legacy presentation boundary.

## Runtime Registration Incident and Fix

### Observed symptom

The first `8ef7306` candidate installed and Legacy Tool dispatch worked, but the Modern Provider became unavailable immediately after upgrade.

### Evidence and root cause

The candidate declared two Providers. Dify/plugin-daemon 0.5.3 logged both Tool installations, but its `tool_installations` state for this plugin retained only `legacy_database_query`; `db_query_extended` returned `PluginNotFoundError`. This is a real installed-runtime limitation of this Dify/daemon combination, not a source-import result.

### Chosen fix

Commit `7b688be` keeps one `db_query_extended` Provider and registers `legacy_database_query` as its second Tool. The migration utility now rewrites only the Tool identity to `db_query_extended/legacy_database_query`. This preserves the frozen nine inline Legacy parameters while keeping Modern credentials and Tool execution alive.

### Rejected path

Keeping two Providers was rejected because it demonstrably overwrote the Modern installation. Duplicating the executor or bypassing Dify installation tables was not used.

The rerun proved both Tool identities from the installed candidate. Modern PostgreSQL `SELECT 1` passed, its structured response remained non-legacy, and Legacy DML rejection produced `ReadOnlyViolationError` without a credential leak.

## Workflow Gate

The real prerequisite probe found three active Dify Workflow records. None contains both the original provider identity `db_query` and original Tool identity `sql_query`; they cannot be presented as a migrated original Workflow. The Console and Workflow endpoints are unreachable because `dify-api-1` and `dify-nginx-1` exited before startup with Docker bind-mount type errors. Therefore the following remain unrun and blocked:

- real legacy DSL dry-run/output/backup/idempotence migration;
- Dify Workflow import and publish;
- downstream Markdown and records consumer validation;
- the required six Workflow API runs.

This blocker is captured in `phase10_2_workflow_blocker.json` and the exact container error is retained in `phase10_2_workflow_baseline_blocker.log`.

## Commands and Reproduction

Run from `E:\Dify_Plugin` with the Dify worker, daemon, and three local test databases available:

```powershell
git worktree add --detach E:\Dify_Plugin_phase10_2_rebuild 7b688be
.\dify-plugin.exe plugin package E:\Dify_Plugin_phase10_2_rebuild\db_query_extended -o <candidate.difypkg> --max-size 100
.\dify-plugin.exe plugin checksum <candidate.difypkg>

docker exec --workdir /app/api -e PYTHONPATH=/app/api dify-worker-1 `
  /app/api/.venv/bin/python /tmp/phase10_2_installed_legacy_runtime.py ...

docker exec --workdir /app/api -e PYTHONPATH=/app/api dify-worker-1 `
  /app/api/.venv/bin/python /tmp/phase10_2_workflow_probe.py ...

.\db_query_extended\.venv\Scripts\python.exe db_query_extended\verification\phase10_2_gate.py `
  --runtime reports\verification\2026-07-13\phase10_2_runtime\phase10_2_installed_runtime_final.json `
  --workflow reports\verification\2026-07-13\phase10_2_runtime\phase10_2_workflow_blocker.json `
  --output reports\verification\2026-07-13\phase10_2_final_gate.json
```

Expected result in the current baseline is installed-runtime `PASS`, Workflow `BLOCKED`, and final `PARTIAL`. If API/nginx is repaired and a genuine original DSL is supplied or exported, rerun the migration and Workflow/API portions; only then may the final status be reconsidered.

## File Change Trace

- `manifest.yaml`: one registered Dify Tool Provider instead of two, because the installed daemon retains one Provider per plugin installation.
- `provider/db_query_extended.yaml`: registers both Modern and Legacy Tool declarations.
- `scripts/migrate_legacy_workflow.py`: maps original `db_query/sql_query` to `db_query_extended/legacy_database_query`.
- `verification/phase10_1_gate.py`: verifies the revised one-Provider/two-Tool design.
- `verification/phase10_2_*.py`: repeatable installed runtime, Workflow prerequisite, and final aggregation gates.

## Tutorial Relevance

- `TUTORIAL_REQUIRED`: clean-source package build, checksum activation, Dify upgrade, installed Tool runtime fixture validation, one-Provider/two-Tool constraint.
- `DEVELOPMENT_HISTORY_ONLY`: two-Provider overwrite incident and Docker Desktop bind-mount failure.
- `EVIDENCE_ONLY`: raw runtime fixture JSON, candidate hash, installation identifier, and blocker logs.
- `TEMPORARY`: detached worktrees, `/tmp` harness copies, and candidate package binary.

## Final Boundary

```text
ALLOWED_CONCLUSIONS:
LEGACY_INSTALLED_TOOL_RUNTIME_THREE_DATABASE_PASS
PHASE_10_2_PARTIAL

NOT_PROVEN:
LEGACY_WORKFLOW_MIGRATION_PASS
ORACLE_REPRODUCTION_PASS
ORACLE11G_REPRODUCTION_PASS
DM8_FINAL_DELIVERY_PASS
KINGBASEES_FINAL_DELIVERY_PASS
FINAL_PROJECT_DELIVERY_PASS
```
