# Phase 10.5 — Installed Legacy Tool Runtime Gate

- Date: 2026-07-15
- Phase: Phase 10.5 — Installed Legacy Tool Runtime Gate
- Status: PASS
- Database: MySQL, PostgreSQL, Microsoft SQL Server through Legacy `mssql`
- Scope: candidate-package installation and installed `legacy_database_query` ToolManager calls; no Workflow, API key, or Modern Tool mutation
- Source commit: `bb72f1c` (`fix(phase10.4): implement legacy compatibility boundaries`)
- Runtime: Dify API worker -> PluginService/PluginInstaller -> ToolManager -> installed plugin-daemon Tool
- Canonical path: `reports/documentation/2026-07-15/Phase10_Base_Reproduction/phase10_5_installed_legacy_tool_runtime_gate.md`
- Machine evidence: `reports/verification/2026-07-15/phase10_5_installed_legacy_tool_runtime_gate.json`
- Logs: NOT_RETAINED — runtime request transcript was observed during this focused gate; no credential-bearing raw transcript was persisted
- Supersedes: None
- Security classification: INTERNAL / REDACTED / NO_CREDENTIALS_RETAINED

## Executive Summary

The Phase 10.4 Legacy boundaries are now proven in the installed Dify Tool runtime. A package built from `bb72f1c` was active as `li_zijun/db_query_extended:0.1.3@975d378…d14cf`. The installed `legacy_database_query` Tool succeeded for MySQL, PostgreSQL, and Legacy `mssql` in both preserved formats: Markdown GitHub table and JSON whose top level is only `records`.

The same installed path accepted a terminal-semicolon `SELECT` and a comment-prefixed `SELECT`; it rejected multi-statements, `WITH`, `SELECT INTO`, and `DELETE` as Dify `PluginInvokeError` failures with the Legacy policy message. It also accepted `schema=public`, rejected the required malformed/unknown/override `db_properties` cases before a database call, and wrapped a controlled SQL failure as a sanitized `PluginInvokeError`, rather than returning a Legacy JSON error object.

## Goal and Acceptance Boundary

This gate closes only the runtime proof required for the Phase 10.4 implementation:

1. candidate package installation and active checksum are observed;
2. the Legacy single-`SELECT` policy is enforced by the installed plugin;
3. strict `db_properties` parsing is enforced by the installed plugin; and
4. Legacy failures leave the formatter path and reach Dify as a sanitized Tool exception.

No Workflow was imported, changed, published, or invoked. No API key was created or changed. Oracle, Oracle11g, DM8, and KingbaseES were not newly tested or claimed by this gate.

## Candidate and Environment

| Item | Recorded value |
| --- | --- |
| Candidate package | `db_query_extended-0.1.3-phase10_5-legacy-boundaries.difypkg` (`LOCAL_ONLY / NOT_TRACKED_BY_GIT`) |
| Package size | 41,239,400 bytes |
| Package SHA-256 | `a6a91d8974252853109d72e61295f3955869fe72f730f207081b7d0cdac11eda` |
| Dify plugin checksum | `975d378099f6f817bda07eb6351bcbc9ec535d6bdb5ec3b33e40ab6b65cd14cf` |
| Active identifier | `li_zijun/db_query_extended:0.1.3@975d378099f6f817bda07eb6351bcbc9ec535d6bdb5ec3b33e40ab6b65cd14cf` |
| Installation result | PASS; candidate already active on the confirmation run |

The MySQL fixture password was read only from the existing local test-database container and supplied to the runner as a process environment variable. It was not printed, written to evidence, added to a Dify credential record, or committed. PostgreSQL and SQL Server used already installed Modern credential records only to populate the Legacy inline request for this focused compatibility test.

## Verification Results

| Gate | Result | Evidence |
| --- | --- | --- |
| Candidate installation / checksum activation | PASS | candidate and active identifier in machine evidence |
| MySQL Markdown + JSON `SELECT 1;` | PASS | Markdown exact GitHub table; JSON only `records` |
| PostgreSQL Markdown + JSON `SELECT 1;` | PASS | same Legacy contracts |
| `mssql` Markdown + JSON `SELECT 1;` | PASS | Legacy name dispatches to internal SQL Server adapter |
| Terminal semicolon and leading comment | PASS | both return Markdown table through installed Tool |
| Multi-statement, `WITH`, `SELECT INTO`, `DELETE` | PASS | each throws `PluginInvokeError` carrying the Legacy policy message |
| `schema=public` | PASS | accepted and returns Legacy JSON |
| duplicate, unknown, `host`, `password`, malformed properties | PASS | each fails before execution as `PluginInvokeError`; property values are absent |
| Controlled missing-table SQL error | PASS | `PluginInvokeError` contains safe `SqlExecutionError` diagnostic and no Legacy JSON error result |

The JSON success checks confirm the runtime message type, the exact one-key top level, the `records` value, and the exposed `result` variable. This protects the Legacy contract from the Modern structured envelope.

## Commands Executed

Run from `E:\Dify_Plugin` after Dify worker, plugin-daemon, and the three local fixture databases are available:

```powershell
.\dify-plugin.exe plugin package .\db_query_extended --output_path <candidate.difypkg> --max-size 100
.\dify-plugin.exe plugin checksum <candidate.difypkg>

docker cp db_query_extended\verification\phase10_2_installed_legacy_runtime.py dify-worker-1:/tmp/phase10_5/
docker cp db_query_extended\verification\phase10_5_installed_legacy_runtime_gate.py dify-worker-1:/tmp/phase10_5/
docker exec --workdir /app/api -e PYTHONPATH=/app/api dify-worker-1 `
  /app/api/.venv/bin/python /tmp/phase10_5/phase10_5_installed_legacy_runtime_gate.py `
  --package /tmp/phase10_5/candidate.difypkg `
  --expected-version 0.1.3 `
  --expected-checksum <checksum> `
  --package-sha256 <sha256> `
  --source-commit bb72f1c `
  --output-dir /tmp/phase10_5/output
```

The runner uses the established public Dify `PluginService`/`PluginInstaller` path and `ToolManager`; it never imports the host source tree as the running plugin. The MySQL password is an execution-only environment input and must not be put into a command transcript or report.

## Files Changed

- `db_query_extended/verification/phase10_5_installed_legacy_runtime_gate.py`: reusable installed-runtime gate; reuses the proven Phase 10.2 installer helper but replaces obsolete Legacy error-JSON and property-name assertions.
- this report and its JSON evidence: records the candidate identity, contract results, and scope boundary.

No product behavior changed in Phase 10.5. The candidate contains the already committed Phase 10.4 code.

## Decisions and Security

- `mssql` remains the Legacy parameter value; it is exercised through the existing internal `sqlserver` adapter mapping.
- Dify `PluginInvokeError` is now observed for policy, parameter, and SQL execution failures. Legacy success formatting is not used for failures.
- The runner deliberately does not inject an artificial unknown Python exception into a production plugin solely to test its fallback string. The Phase 10.4 static gate covers that fixed fallback branch; this gate proves the real known-error Dify wrapper and redaction behavior.
- Evidence stores query hashes and safe Dify messages only. It contains no password, connection URL, Authorization value, or raw fixture credential.

## Reproduction Trace

Prerequisites: candidate source at `bb72f1c`; running Dify API worker/plugin-daemon; reachable MySQL, PostgreSQL, and SQL Server local fixtures; an existing Dify tenant with PostgreSQL and SQL Server credentials; an execution-only MySQL fixture password.

Expected result: the runner prints five PASS gates and writes `phase10_5_installed_legacy_tool_runtime_gate.json`. A failure means either candidate activation, installed dispatch, contract preservation, or sanitized exception handling is incomplete. It does not authorize a Workflow change or an expansion of database support.

## Final Decision

```text
PHASE_STATUS: PASS

ALLOWED_CONCLUSIONS:
PHASE_10_5_INSTALLED_LEGACY_TOOL_RUNTIME_PASS

NOT_YET_PROVEN:
LEGACY_WORKFLOW_REIMPORT_OR_PUBLISH_PASS
ORACLE_RUNTIME_PASS
ORACLE11G_RUNTIME_PASS
DM8_NEW_RUNTIME_PASS
KINGBASEES_NEW_RUNTIME_PASS
FINAL_PROJECT_DELIVERY_PASS

FINAL_DELIVERY_IMPACT:
This is an installed Tool runtime gate only. It does not complete the project,
the original-plugin reproduction prerequisite, or any database final delivery.

NEXT_PHASE:
Decide and implement the remaining Legacy-compatible architecture work without
changing the frozen Workflow/API boundary in this gate.
```

## Tutorial Relevance

- `TUTORIAL_REQUIRED`: package command, checksum activation, public installer path, and installed ToolManager verification.
- `DEVELOPMENT_HISTORY_ONLY`: reuse of a local fixture password because a Modern MySQL credential was not present.
- `EVIDENCE_ONLY`: candidate SHA-256, plugin checksum, active identifier, and per-case runtime output.
- `TEMPORARY`: `/tmp/phase10_5`, candidate package binary, and process-only environment variables.
