# Phase 10 Preparation — Adapter Expansion (KingbaseES)

## Status

Planning document only. No KingbaseES code, Provider field, Adapter registration, Workflow, dependency, or verification behavior is added here.

## Overall goal

Extend the released v1.0.0 Adapter Framework with a real KingbaseES target while preserving every frozen contract and all accepted database behavior. Phase 10 will evolve as `v1.1.x`.

## Technical goals

1. Select and document the exact KingbaseES server version, Linux `amd64` driver, SQLAlchemy compatibility, and redistribution terms.
2. Implement KingbaseES only at the designed Adapter/credential extension boundaries.
3. Preserve one stable Tool input/output and JSON Contract.
4. Support connection validation, bounded read-only execution, timeout behavior, Unicode, dates/numerics/binary/nulls, cleanup, and controlled errors.
5. Add real Provider, Workflow, Workflow API, and dangerous-SQL evidence for KingbaseES.
6. Package and install the plugin in the accepted Dify baseline without changing existing runtime persistence.

## Risk analysis

| Risk | Impact | Required mitigation |
| --- | --- | --- |
| Assuming full PostgreSQL compatibility | incorrect timeout, metadata, type, or SQL behavior | verify against a real KingbaseES version and driver |
| Driver packaging/licensing | plugin cannot be distributed or loaded in Linux runtime | legal/license review and clean-runtime packaging test |
| Vendor-specific dangerous SQL | shared validator may miss a write/admin construct | add KingbaseES security cases without weakening existing policy |
| Type normalization | unstable JSON or Unicode corruption | real Workflow/API cases for vendor types and Chinese text |
| Regression in existing adapters | breaks released users | run the complete inherited suite before acceptance |
| Environment contamination | invalidates v1.0.0 evidence | isolate Phase 10 feature branch and dated verification evidence |

## Acceptance standard

- Real KingbaseES Provider credential validation succeeds and invalid credentials fail safely.
- Scalar, multi-row, truncation, Unicode, timestamp/numeric/null, timeout, and controlled error cases pass.
- Published Workflow and Workflow API return the existing JSON Contract.
- DML, DDL, multi-statement, permission/transaction, obfuscated, and KingbaseES-specific dangerous SQL are rejected.
- Package installs and runs in the accepted Linux `amd64` plugin daemon.
- No unexplained FAIL or SKIP exists in the Phase 10 release candidate.

## Regression requirements

- Provider, Tool, Workflow, SQL Security, JSON Contract, and verification orchestration from v1.0.0 remain compatible.
- The inherited **45 PASS / 0 FAIL / 0 SKIP** suite must remain fully green.
- KingbaseES checks are additive; they never replace, disable, or skip MySQL, PostgreSQL, or DM8 checks.
- Evidence must be written to a new dated directory and linked from the next-version release report.

## First principle

All new databases must be built on the v1.0.0 baseline of **45 PASS / 0 FAIL / 0 SKIP**. No extension may break or rewrite the frozen Provider, Tool, Workflow, SQL Security, JSON Contract, or automated acceptance system.
