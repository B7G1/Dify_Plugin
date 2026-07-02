# Thesis Outline

## Chapter 1 — Introduction

Research background, low-code AI workflows, database integration risks, research questions, scope, and contributions.

## Chapter 2 — Related Technology and Prior Work

Dify plugin model, workflow execution, database abstraction approaches, SQL safety validation, container persistence, and verification strategies. Separate literature claims from project evidence and add formal citations during writing.

## Chapter 3 — Requirements and Problem Analysis

Stakeholders, functional/non-functional requirements, threat model, read-only definition, compatibility targets, persistence failure history, and acceptance criteria.

## Chapter 4 — System Architecture

Overall architecture; Provider, Tool, Adapter Registry, formatter, Workflow/API, Docker/WSL environment, PostgreSQL and Weaviate persistence. Use the unified SVG/PNG diagrams.

## Chapter 5 — Detailed Implementation

Credential validation, shared SQL policy, adapter lifecycle, timeout/error handling, JSON-safe normalization, packaging, fixed startup, preflight, and secret discipline.

## Chapter 6 — Verification Design

Layered Provider/Tool/Workflow suites, dangerous SQL cases, Unicode, real DM8 target, API contract, evidence JSON, and zero-skip release gate.

## Chapter 7 — Experiments and Analysis

- Experiment A: functional query path (`SELECT 1`, Chinese text, timestamp).
- Experiment B: security rejection paths.
- Experiment C: row limit/truncation and JSON consistency.
- Experiment D: cold boot and persistent identity.
- Experiment E: full automated acceptance, 45/0/0.
- Analyze what each result proves and what it does not prove.

## Chapter 8 — Productization and Reproducibility

Baseline freeze, bootstrap limitations, report automation, Dashboard, release package, screenshot provenance, Marketplace gap analysis, and open-source governance.

## Chapter 9 — Limitations and Future Work

Portability, CI infrastructure, performance measurement, license/privacy decisions, and Phase 10 KingbaseES. Keep Oracle, SQL Server, and SQLite as future phases.

## Chapter 10 — Conclusion

Answer the research questions: how one stable Tool contract can support heterogeneous databases, how safety is preserved, and how persistence plus real acceptance supports long-term maintainability.

## Appendices

Test matrix, 45-case summary, cold-boot facts, recovery procedure, package/dependency matrix, selected sanitized screenshots, and report/evidence index.
