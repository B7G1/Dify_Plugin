# Phase 7.4 Release Staging Hygiene — Staging Allowlist Plan

Status: ANALYSIS ONLY  
Date: 2026-07-07  
Branch: `feature/kingbasees-adapter`

This plan intentionally does not stage, commit, delete, restore, or move files. It classifies the current working tree into safe staging groups and risk buckets.

## Current risk summary

The working tree contains a mixture of:

1. Phase 7.2 multilingual evidence closure.
2. Phase 7.3 / 7.3b regression closure.
3. DM8 / KingbaseES / SQL Server expansion artifacts.
4. Interactive map and generated UI assets.
5. Historical report deletions and archive moves.
6. Build/package artifacts and untracked binaries.

Do not run `git add .`.

## Commit 1 allowlist — Phase 7 regression closure

Purpose: preserve the completed Phase 7.2 / Phase 7.3 evidence and the narrow verifier harness fix.

Recommended commit message:

```text
fix: normalize workflow output and close Phase 7 regression
```

Allowlist:

```text
db_query_extended/verification/verification_runner.py
reports/README.md
reports/REPORT_MAP.md
reports/documentation/README.md
reports/FINAL_ACCEPTANCE_INDEX_2026-07-01.md
reports/documentation/Phase7_2_Multilingual_Compatibility/
reports/documentation/Phase7_3_Full_Adapter_Regression/
reports/verification/2026-07-07/
```

Evidence to mention in commit/body:

```text
Phase 7.2: PASS / fully closed
Phase 7.3: PASS
Provider: 6 PASS / 0 FAIL / 0 SKIP
Tool: 27 PASS / 0 FAIL / 0 SKIP
Workflow: 12 PASS / 0 FAIL / 0 SKIP
verify_all: 45 PASS / 0 FAIL / 0 SKIP
```

Notes:

- `verification_runner.py` is verifier harness code, not production Provider / Tool / Adapter behavior.
- The Workflow false negative was caused by output shape normalization mismatch.
- The actual Dify Workflow now returns `outputs["json"]` as a one-element list containing the result object.
- The verifier now accepts dict or one-element list-of-dict and continues to reject arbitrary arrays.

Pre-stage checks:

- Confirm no secret values are present in `reports/verification/2026-07-07/`.
- Confirm only credential field names, such as `DIFY_WORKFLOW_API_KEY`, are recorded.
- Confirm screenshots do not expose secrets before committing them.

## Commit 2 candidate — adapter expansion and database gates

Purpose: separate DM8 data capability, KingbaseES feasibility/mock work, SQL Server environment expansion, and local database fixtures from the Phase 7 regression closure.

Candidate paths:

```text
db_query_extended/verification/dm8_data_capability_runner.py
db_query_extended/verification/import_dm8_multilingual_fixture.ps1
db_query_extended/verification/import_dm8_multilingual_fixture.py
db_query_extended/verification/kingbase_mock_runner.py
db_query_extended/verification/multilingual_gate_runner.py
db_query_extended/verification/packaging_readiness_runner.py
db_query_extended/verification/verify_dm_data_capability.ps1
db_query_extended/verification/verify_kingbase_mock.ps1
db_query_extended/verification/verify_kingbase_phase10.ps1
db_query_extended/verification/verify_phase10_packaging.ps1
db_query_extended/workflow_specs/
reports/documentation/Phase10_KingbaseES_Adapter/
reports/documentation/Phase11_Database_Expansion/
reports/documentation/Phase11_SQLServer_Adapter/
reports/documentation/Phase7_1_DM8_Adapter/data_capability_evidence_closure_2026-07-06.md
reports/documentation/Phase7_1_DM8_Adapter/data_retrieval_validation.md
reports/documentation/Phase7_1_DM8_Adapter/frontend_data_retrieval_status_2026-07-07.md
reports/verification/2026-07-06/
reports/verification/2026-07-02/
local_test_db/
```

Do not stage until reviewed for:

- license files
- passwords
- API keys
- database dumps with sensitive content
- large binary artifacts
- environment-specific absolute paths that should remain local

Potential commit message:

```text
docs: archive domestic database expansion evidence
```

## Commit 3 candidate — interactive map and generated UI artifacts

Purpose: keep interactive documentation/report UI separate from verification logic.

Candidate paths:

```text
db_query_extended_interactive_map/
reports/README.html
LICENSE_COMPARISON.html
ROADMAP.html
当前状态.html
当前状态.md
最新报告/
过往报告/
```

Review before staging:

- generated assets volume
- whether HTML/libs should be committed or regenerated
- broken links after any report moves
- whether Chinese-named generated files belong in repo history

Potential commit message:

```text
docs: update interactive report map and generated views
```

## Commit 4 candidate — archive and deletion hygiene

Purpose: handle historical deletion/migration separately after human confirmation.

High-risk deletions currently shown by git status include:

```text
Dify本地化插件制作流程_最新整理版.html
Dify本地化插件制作流程_最新整理版.qmd
Dify本地化插件制作流程_最新整理版_files/...
reports/documentation/Phase2_Plugin_Development/day3_plugin_manifest_main_report.md
reports/documentation/Phase5_DM_Adapter/*
reports/documentation/Phase6_KingbaseES_Adapter/*
```

Do not stage deletions until confirming whether each deleted path has a replacement in:

```text
过往报告/
reports/archive/
reports/documentation/Phase7_Domestic_Database_Adapters/
```

Potential commit message:

```text
docs: reorganize historical report archive
```

## Explicitly do not stage yet

```text
db_query_extended.difypkg
db_query_extended/db_query_extended.difypkg
junjiem-db_query_0.0.11-offline.difypkg
test_tool_schema.difypkg
db_query_extended/utils/adapters/kingbasees.py
db_query_extended/utils/drivers/
db_query_extended/provider/db_query_extended.yaml
db_query_extended/requirements.txt
db_query_extended/utils/validation.py
test_tool_schema/
env_check/
release/db_query_extended/
staged.txt
start_dify.bat
```

Reason:

- Package artifacts and generated binaries should be reviewed separately.
- KingbaseES product code and provider changes are not part of Phase 7.3b regression closure.
- Provider/requirements/validation modifications may be production-impacting and require a separate code review.

## Recommended immediate next action

Perform a scoped diff review for Commit 1 only:

```text
db_query_extended/verification/verification_runner.py
reports/README.md
reports/REPORT_MAP.md
reports/documentation/README.md
reports/FINAL_ACCEPTANCE_INDEX_2026-07-01.md
reports/documentation/Phase7_2_Multilingual_Compatibility/
reports/documentation/Phase7_3_Full_Adapter_Regression/
reports/verification/2026-07-07/
```

If clean, stage only those paths and commit with:

```text
fix: normalize workflow output and close Phase 7 regression
```

## Remaining open items

- Rotate exposed `DIFY_WORKFLOW_API_KEY` outside the repository.
- Rotate exposed DM administrator password outside the repository.
- Review screenshots for secret exposure before committing them.
- Decide whether release package artifacts are tracked or excluded.
- Decide whether KingbaseES code changes belong to a separate feature commit.
