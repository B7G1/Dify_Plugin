# Phase 7.3 Regression Verification Matrix

| # | Gate | Evidence type | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Provider contract | REAL_EXECUTION_PASS | PASS | `phase7_3_provider_result.json`: 6 PASS / 0 FAIL / 0 SKIP |
| 2 | Tool contract | REAL_EXECUTION_PASS | PASS | `phase7_3_tool_result.json`: 27 PASS / 0 FAIL / 0 SKIP |
| 3 | SQL read-only safety | REAL_EXECUTION_PASS | PASS | `drop`, `update`, `delete`, `alter`, `create` blocked |
| 4 | MySQL adapter | REAL_EXECUTION_PASS | PASS | Provider credential, adapter contract, six tool cases, multilingual exact equality |
| 5 | PostgreSQL adapter | REAL_EXECUTION_PASS | PASS | Provider credential, adapter contract, six tool cases, multilingual exact equality |
| 6 | DM8 adapter | REAL_EXECUTION_PASS | PASS | Provider credential, adapter contract, six tool cases, unicode bind, 14 data capability cases, multilingual exact equality |
| 7 | Result formatting / JSON normalization | REAL_EXECUTION_PASS | PASS | decimal, datetime, row shape, JSON response contract |
| 8 | Row truncation / max_rows | REAL_EXECUTION_PASS | PASS | adapter `max_rows` cases and formatter `truncated` case |
| 9 | Unicode / multilingual retrieval | REAL_EXECUTION_PASS | PASS | `phase7_3_multilingual_regression_result.json`: 3 PASS / 0 FAIL / 0 SKIP |
| 10 | Workflow API | REAL_EXECUTION_PASS | PASS | `phase7_3b_workflow_result.json`: 12 PASS / 0 FAIL / 0 SKIP |
| 11 | Packaging / import / runtime dependency readiness | STATIC_INSPECTION_PASS for v1.0 | CONDITIONAL | v1 canonical artifact and dependency wheels PASS; Kingbase v1.1 dependencies blocked out of scope |
| 12 | Cross-adapter regression | REAL_EXECUTION_PASS | PASS | MySQL / PostgreSQL / DM8 all passed common Provider, Tool, truncation, safety, multilingual gates |
| 13 | Full verification rerun | REAL_EXECUTION_PASS | PASS | `phase7_3b_verify_all/summary.json`: 45 PASS / 0 FAIL / 0 SKIP |

## Summary

Core regression status: **PASS**  
Release-readiness status: **PASS**  
Reason: Phase 7.3b reran Workflow API and `verify_all.ps1` successfully; the earlier Workflow failure was a verifier parsing false negative.
