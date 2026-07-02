# Paper Outline

## Title

A Recoverable Adapter Architecture for Read-Only Database Queries in Dify Workflows

## Abstract

Describe the problem of exposing heterogeneous databases to low-code AI workflows while preserving read-only safety, normalized output, reproducibility, and deployability. Summarize the Provider–Tool–Adapter architecture, persistent Dify baseline, and real 45-case acceptance.

## 1. Introduction

- Workflow systems need controlled access to operational databases.
- Driver, dialect, timeout, type, and credential differences make one-off integrations fragile.
- Contribution: a reusable read-only plugin architecture plus a recovery and verification discipline.

## 2. Problem Definition

- Functional requirement: execute one bounded read-only query from Dify.
- Security requirement: reject DML, DDL, multi-statement, and dangerous constructs.
- Compatibility requirement: MySQL, PostgreSQL, and DM8 under one result contract.
- Operational requirement: survive container and desktop restarts without losing administrator, plugin, or Workflow state.

## 3. Architecture

- Provider owns credential schema and validation.
- Tool owns stable Dify input/output and shared policy.
- Adapter Registry isolates drivers and database semantics.
- Formatter normalizes Unicode, dates, decimals, binary values, and metadata into JSON.
- Workflow and API expose the same three-node execution path.
- Reference `architecture/overall_architecture.svg` and four component diagrams.

## 4. Implementation

- Python 3.12 plugin runtime and Dify Plugin SDK 0.6.2.
- SQLAlchemy-based adapter boundary with PyMySQL, psycopg2, dmPython, and dmSQLAlchemy.
- Fixed Compose project, PostgreSQL/Weaviate named volumes, and startup preflight.
- Secret handling through Dify Provider credentials and process-only Workflow API key injection.

## 5. Verification Method

- Provider suite: 6 checks.
- Tool suite: 27 checks covering success, truncation, types, timeout/error mapping, and dangerous SQL.
- Workflow suite: 12 checks including DM8, Unicode, API, and security paths.
- Aggregate criterion: zero FAIL and zero SKIP.
- Cold boot: full stop, single-entry restart, unchanged PostgreSQL identity, object persistence, then functional regression.

## 6. Experiment and Results

| Experiment | Result | Meaning |
| --- | --- | --- |
| Provider | 6 PASS / 0 FAIL / 0 SKIP | credentials and Provider contract operate correctly |
| Tool | 27 / 0 / 0 | core read-only and result behavior is stable |
| Workflow | 12 / 0 / 0 | published DM8/UI/API chain succeeds |
| Full acceptance | 45 / 0 / 0 | no hidden skip in release gate |
| Cold boot | system identifier `7657369583221227555` unchanged | same PostgreSQL cluster persisted |
| Plugin daemon | restart count 0 after recovery | runtime remained stable |
| Unicode | Chinese query/result passed | driver-to-JSON path preserves text |

Use machine evidence from `reports/verification/2026-07-01/final_cold_boot/`; do not derive new numerical claims from screenshots.

## 7. Discussion

- Adapter isolation lowers the cost of future databases but does not eliminate vendor-specific testing.
- Automated acceptance is necessary but UI evidence and license/governance remain separate release gates.
- The fixed-path baseline improves reproducibility on the accepted machine while limiting portability.

## 8. Threats to Validity

- One accepted Dify version and `amd64` runtime.
- Vendor environment availability and DM8 licensing/driver constraints.
- Cold boot verifies one machine, not arbitrary disaster recovery.
- MySQL/PostgreSQL evidence spans earlier phases; DM8 received the final real Workflow focus.

## 9. Future Work

- Phase 10 KingbaseES with the same acceptance matrix.
- Oracle, SQL Server, SQLite only after KingbaseES.
- CI runners, reproducible packaging, performance benchmarks, signed releases, Marketplace review.

## 10. Conclusion

The project demonstrates that safe database access in Dify requires both a clean adapter contract and an operational evidence chain. The v1.0 baseline is technically accepted and ready for public-release cleanup, not yet an official Marketplace release.
