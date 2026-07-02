# Roadmap after v1.0.0 Public Release

## Current transition

- v1.0.0 Technical Baseline: **FROZEN**
- Screenshot Review: **PASS**
- Public Release: **READY**
- Next active phase: **Phase 10 — KingbaseES Adapter**

## Phase 10 — KingbaseES Adapter

| Priority | Workstream | Estimate | Main risks | Dependencies | Acceptance standard |
| --- | --- | --- | --- | --- | --- |
| P0 | KingbaseES environment and driver baseline | 1–2 days | version/driver mismatch, redistribution terms | real KingbaseES instance, Linux amd64 driver | documented version, connectivity probe, license review |
| P0 | KingbaseES Adapter implementation | 3–5 days | assuming full PostgreSQL compatibility | approved Adapter contract and template | no change to existing Provider/Tool contract; controlled errors and JSON types |
| P0 | Real Provider / Workflow / API verification | 2–3 days | timeout/type/Unicode differences | published test Workflow and ephemeral API key | Provider, Workflow, API, Unicode, truncation, timeout, and dangerous SQL PASS |
| P0 | Full regression | 1 day | regression in MySQL/PostgreSQL/DM8 | v1.0 45-case baseline | all existing 45 checks plus KingbaseES checks; zero FAIL/SKIP |

## Later phases

| Priority | Workstream | Estimate | Dependency | Acceptance direction |
| --- | --- | --- | --- | --- |
| P1 | CI/CD implementation | 5–8 days | runner and secret ownership | lint, unit, package, secret scan, gated vendor integration |
| P2 | Oracle Adapter | 7–10 days | Phase 10 lessons and Oracle test environment | DATE/TIMESTAMP/NUMBER/CLOB plus full shared regression |
| P2 | SQL Server Adapter | 5–8 days | Linux ODBC environment | NVARCHAR/datetime, timeout, API, security regression |
| P3 | SQLite Adapter | 3–5 days | approved file-access policy | read-only file scope, traversal and locking tests |
| P2 | Performance optimization | 5–10 days | representative benchmarks | documented latency/memory improvement with no regression |
| P2 | Automated release | 3–5 days | stable CI and signing/checksum policy | reproducible artifact and human approval gate |
| P3 | Official Dify Marketplace submission | 3–7 days | license, contacts, official schema review | clean install, metadata approval, public support route |

Phase 10 may add only KingbaseES. Oracle, SQL Server, and SQLite remain out of scope until KingbaseES acceptance is complete.
