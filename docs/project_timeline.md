# db_query_extended Project Timeline

## 2026-06-16 — Research

The project began because Dify workflows needed database access without granting arbitrary SQL execution. Research mapped the Dify plugin model, Provider/Tool boundary, packaging model, and local runtime constraints. This mattered because the project needed a security and extension direction before code existed. The result defined a read-only query tool rather than a general database administration plugin.

## Phase 1 — Environment direction

The first phase converted research into an executable project plan. It identified Docker Desktop, WSL, Python, the Plugin CLI, Dify, and local databases as the required environment. This exposed that reproducibility would be as important as plugin code and prepared the later recovery baseline.

## Phase 2 — Plugin Skeleton and Reverse Engineering

The plugin skeleton established manifest, Provider, Tool, entry point, packaging, and local verification structure. Reverse engineering of an existing SQL plugin clarified useful behavior and unsafe shortcuts. The phase solved “how a Dify Tool is assembled” and provided a controlled foundation for original implementation.

## Phase 3 — Workflow integration

Local code alone could not prove compatibility with the real platform. The plugin was installed into Dify, Providers were configured, Workflows were created, and UI/API paths were exercised. This phase solved platform-integration failures and demonstrated that Provider → Tool → Workflow execution worked outside unit tests.

## Phase 4 — Shared core freeze

As query behavior grew, connection creation, result conversion, error handling, and SQL policy risked becoming duplicated. Phase 4 centralized those responsibilities and froze the public read-only contract. This was important because later database work needed a stable core rather than repeated rewrites.

## Phase 5 — Adapter architecture

MySQL and PostgreSQL differences revealed that a single conditional-heavy helper would not scale. Database-specific behavior moved into independent adapters behind a shared contract. This solved maintainability and made future databases additive rather than invasive.

## Phase 5.5 — Workflow automation

Manual screenshots could show success but could not guarantee repeatability. Provider, Tool, Workflow API, JSON, and dangerous-SQL cases became automated suites. This phase established machine evidence and the zero-FAIL/zero-SKIP release rule used by all later phases.

## Phase 6 — Release freeze

The project introduced package identity, release notes, checksums, immutable evidence, and release checklists. This solved ambiguity between development builds and release candidates. It also created the discipline needed to accept a new database without losing earlier behavior.

## Phase 7 — Domestic database direction

DM8 and KingbaseES were evaluated as extensions of the Adapter framework. The phase separated target-specific requirements from shared Tool behavior. This protected the frozen core and established that domestic databases must satisfy the same Provider, Workflow, API, Unicode, and security criteria.

## Phase 7.1 — DM8 real acceptance

DM8 support was implemented and installed as plugin 0.1.1. Provider credentials were validated against a real target, a three-node Workflow was published, Workflow API calls returned real DM8 data, Unicode passed, and dangerous SQL was rejected. The final suite reached Provider 6, Tool 27, Workflow 12 — **45 PASS / 0 FAIL / 0 SKIP**. This proved the Adapter framework with a materially different database.

## Persistence recovery and cold boot

After a restart exposed missing Console state, the investigation found an unstable temporary mount/Compose chain. PostgreSQL and Weaviate moved to fixed named volumes under the `dify` project, with one startup entry and preflight. Stop/start, Docker Desktop, WSL, and full cold-boot evidence kept PostgreSQL system identifier `7657369583221227555` unchanged. This solved the difference between “works now” and “survives tomorrow.”

## Phase 8 — Baseline Freeze

The accepted environment, versions, recovery procedure, architecture, release materials, and verification evidence were frozen as v1.0. This phase made the DM8 result a reusable development baseline rather than a one-off success.

## Phase 9 — Product Ready

The repository was reorganized for a new contributor: README, bootstrap, Developer Guide, CI design, report generator, Marketplace checklist, test matrix, and Adapter template were added. This solved discoverability and team handoff while leaving business logic unchanged.

## Phase 9.5 — Public Release

Architecture SVG/PNG assets, Cold Boot explanation, Demo scripts, OBS/PowerPoint order, paper/thesis outlines, presentation material, governance files, and public screenshots were completed. Final manual screenshot review passed. This made the baseline suitable for public demonstration, defense, and release.

## 2026-07-02 — v1.0.0 Completed

The lifecycle closed with `Technical Baseline = FROZEN`, `Environment = READY`, `Public Release = READY`, and `45 PASS / 0 FAIL / 0 SKIP`. v1.0.0 is no longer a development target. All feature development now begins from the frozen tag candidate and belongs to `v1.1.x`, starting with Phase 10 KingbaseES Adapter expansion.
