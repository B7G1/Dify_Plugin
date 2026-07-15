# Phase 10.6 — Legacy Workflow End-to-End Non-Regression Gate

- Date: 2026-07-15
- Phase: Phase 10.6 — Legacy Workflow End-to-End Non-Regression Gate
- Status: PARTIAL
- Database: PostgreSQL, MySQL, Microsoft SQL Server through Legacy `mssql`
- Scope: existing published Phase 10.2.1 Markdown and JSON Workflows only; real Workflow API calls and read-only execution tracing
- Source commit: `bb72f1c` (`fix(phase10.4): implement legacy compatibility boundaries`)
- Runtime: Dify API worker -> Workflow API -> published Workflow snapshot -> Tool -> Template -> End output
- Canonical path: `reports/documentation/2026-07-15/Phase10_Base_Reproduction/phase10_6_legacy_workflow_end_to_end_non_regression_gate.md`
- Machine evidence: `reports/verification/2026-07-15/phase10_6_legacy_workflow_end_to_end_non_regression_gate.json`
- Logs: NOT_RETAINED — no raw credential-bearing HTTP transcript was persisted
- Supersedes: None
- Security classification: INTERNAL / REDACTED / NO_CREDENTIALS_RETAINED

## Executive Summary

Phase 10.6 made the required real calls to the two existing Legacy Workflows without changing, importing, or publishing either Workflow and without creating or rotating an API key. All six positive calls returned HTTP 200 and Workflow `succeeded`; all three Markdown calls returned a GitHub-style table containing `probe=1`. Both PostgreSQL negative calls entered the Legacy `PluginInvokeError` / Workflow exception chain, returned no success payload, and passed the sensitive-value scan.

The gate is nevertheless `PARTIAL`. The active tenant plugin is the verified Phase 10.5 candidate, `li_zijun/db_query_extended:0.1.3@975d378099f6f817bda07eb6351bcbc9ec535d6bdb5ec3b33e40ab6b65cd14cf`, but both existing published Workflow snapshots resolve their Tool node to `li_zijun/db_query_extended:0.1.1@a528b17bd19f6e3aeed58e8db92f6b25c2ddb372c2bb8d0398bc0447da7293ec`. The JSON Workflow also returns its old list result rather than the required Template-produced `result` String containing `{"records":[{"probe":1}]}`. Changing that immutable snapshot would require an import/publish or Workflow edit, which this phase forbids.

## Acceptance Boundary and Baseline

Phase 10.5 was committed separately as `2a2e1aac418e15f5375abc77061d3e30a5499c09` (`test(phase10.5): verify installed legacy tool runtime`). Its candidate package SHA-256 is `a6a91d8974252853109d72e61295f3955869fe72f730f207081b7d0cdac11eda`; its active checksum and identifier still match the expected candidate before the Workflow calls.

`dify-api-1`, `dify-worker-1`, `dify-plugin_daemon-1`, `dify-nginx-1`, and the PostgreSQL, MySQL, and SQL Server fixtures were running. The originally expected local `api.env` was not present in the accessible Dify project location or current process. The gate therefore used the already existing app-scoped Dify API tokens for the two named published Workflows inside the API worker. Token values were read only for request authorization, never emitted, persisted, created, or changed.

## Workflow and Key State

| Item | Result |
| --- | --- |
| Existing Markdown Workflow | `502b5f09-93ef-40a7-bff6-d25c99a21de1`; published Workflow ID `96146b12-6532-4ae3-bc9e-8c15fe186a48` |
| Existing JSON Workflow | `905f1d4a-44ba-4bcd-90f2-e5a43742dd5a`; published Workflow ID `88ce31f7-715b-4853-bd25-8983416e9770` |
| Workflow modified / reimported / published | No / No / No |
| API Key created, rotated, or changed | No |
| Active candidate at invocation | Expected Phase 10.5 identifier confirmed |
| Tool identifier resolved by both published Workflow snapshots | Old `0.1.1@a528…`, not the active Phase 10.5 `0.1.3@975d…` candidate |

## Real Workflow API Results

| Workflow | Database | HTTP | Workflow status | Result | `probe` | Candidate contract |
| --- | --- | ---: | --- | --- | ---: | --- |
| Markdown | PostgreSQL | 200 | `succeeded` | GitHub Markdown table | 1 | FAIL — Tool snapshot is old `0.1.1` |
| Markdown | MySQL | 200 | `succeeded` | GitHub Markdown table | 1 | FAIL — Tool snapshot is old `0.1.1` |
| Markdown | SQL Server / `mssql` | 200 | `succeeded` | GitHub Markdown table | 1 | FAIL — Tool snapshot is old `0.1.1` |
| JSON | PostgreSQL | 200 | `succeeded` | list, not final JSON `result` String | N/A | FAIL — old Tool snapshot and output contract |
| JSON | MySQL | 200 | `succeeded` | list, not final JSON `result` String | N/A | FAIL — old Tool snapshot and output contract |
| JSON | SQL Server / `mssql` | 200 | `succeeded` | list, not final JSON `result` String | N/A | FAIL — old Tool snapshot and output contract |

The API worker trace confirmed `tool`, `template-transform`, and `end` nodes for every positive call. It also confirms that the current active candidate was not the Tool version invoked by the frozen Workflow snapshots. No Modern structured envelope was returned by the successful Markdown cases.

## Negative Paths

| Case | Workflow | Database | Outcome | Failure stage | Success payload | Sensitive scan |
| --- | --- | --- | --- | --- | --- | --- |
| `SELECT 1; SELECT 2;` | Markdown | PostgreSQL | expected failure | Legacy `PluginInvokeError` / Workflow exception chain | absent | PASS |
| `SELECT * FROM phase10_6_missing_table;` | Markdown | PostgreSQL | expected failure | Legacy `PluginInvokeError` / Workflow exception chain | absent | PASS |

## Security and Redaction

PostgreSQL and SQL Server request inputs were derived transiently from existing encrypted Modern credential records; the MySQL fixture password was read transiently from its existing local container environment. API tokens and database passwords were neither printed nor retained in the machine evidence. The evidence stores only safe statuses, identifiers, types, shapes, and assertion results.

## Files Changed

- `db_query_extended/verification/phase10_6_legacy_workflow_api_gate.py`: reproducible API-worker gate; it only reads the existing Workflows, existing credentials, existing app tokens, current plugin identity, and persisted execution traces.
- This canonical report and its machine evidence: record the real call boundary and the immutable published-snapshot mismatch.

## Final Decision

```text
PHASE_STATUS: PARTIAL

ALLOWED_CONCLUSIONS:
The existing Workflow API transport, fixture reachability, Markdown output path,
and both negative Legacy exception paths are live.
The current Phase 10.5 candidate is active for the tenant.

NOT_YET_PROVEN:
PHASE10_6_CURRENT_CANDIDATE_WORKFLOW_PASS
ORACLE_RUNTIME_PASS
ORACLE11G_RUNTIME_PASS
DM8_NEW_RUNTIME_PASS
KINGBASEES_NEW_RUNTIME_PASS
FINAL_PROJECT_DELIVERY_PASS

FINAL_DELIVERY_IMPACT:
No final delivery claim is permitted. This run proves that the old published
Workflow snapshots work, not that they execute the current candidate.

NEXT_PHASE:
None automatically. A new authorized Workflow migration/import/publish decision
is required before retrying this gate against the Phase 10.5 candidate.
```

## Tutorial Relevance

- `TUTORIAL_REQUIRED`: verify the active plugin identifier separately from the published Workflow Tool snapshot before claiming end-to-end compatibility.
- `DEVELOPMENT_HISTORY_ONLY`: published Workflows can retain a historical plugin checksum after a tenant plugin upgrade.
- `EVIDENCE_ONLY`: request authorization and database credentials were process-only inputs.
- `TEMPORARY`: `/tmp/phase10_6_legacy_workflow_api_gate.py` and the process environment used for the run.
