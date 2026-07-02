# Changelog

All notable changes to this project are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows Semantic Versioning for product releases.

Product version `v1.0.0` contains plugin package version `0.1.1`.

## [Unreleased]

### Added

- No changes. New functionality begins after the frozen v1.0.0 baseline.

## [v1.0.0] - 2026-07-02

### Added

- Read-only database query support for MySQL 8.4, PostgreSQL 16, and DM8.
- Dify Provider credential validation and a stable read-only Tool contract.
- Shared Adapter framework with MySQL, PostgreSQL, and DM8 implementations.
- Stable JSON result fields, row limits, truncation metadata, timeout handling, and Unicode-safe values.
- Published three-node DM8 Workflow and Workflow API acceptance path.
- Fixed `dify` Compose startup with persistent PostgreSQL, Weaviate, and application-storage named volumes.
- `start_dify.ps1`, `dify_preflight.ps1`, and safe `bootstrap.ps1` recovery entry points.
- Provider, Tool, Workflow, and aggregate verification scripts with machine-readable evidence.
- Architecture SVG/PNG assets, Dashboard, Demo, Developer Guide, release documents, paper outlines, and presentation material.
- Contribution, security, privacy, issue, pull-request, and Marketplace metadata documents.

### Changed

- Moved database-specific behavior behind the Adapter Registry while preserving one Provider/Tool/Workflow contract.
- Replaced unstable temporary middleware/PostgreSQL mounts with fixed named volumes managed by the `dify` Compose project.
- Standardized release evidence around dated JSON results and a zero-FAIL/zero-SKIP gate.
- Declared `v1.0.0` the immutable technical baseline for all later adapter work.

### Fixed

- Prevented administrator, tenant, plugin, Provider, and Workflow loss after controlled restart by stabilizing PostgreSQL persistence.
- Corrected plugin-daemon startup dependencies and storage/database readiness so restart loops no longer occur.
- Corrected Workflow variable binding and API acceptance configuration discovered during real DM8 verification.
- Established process-only Workflow API key handling so release scripts and reports do not persist credentials.

### Security

- Enforced one read-only `SELECT` or `WITH ... SELECT` statement.
- Rejected DML, DDL, multi-statement input, transaction and permission commands, and dangerous SQL before execution.
- Kept passwords, tokens, API keys, and connection secrets out of reports, scripts, and Git.
- Added private vulnerability-reporting guidance and release secret checks.

### Verification

- Provider: 6 PASS / 0 FAIL / 0 SKIP.
- Tool: 27 PASS / 0 FAIL / 0 SKIP.
- Workflow: 12 PASS / 0 FAIL / 0 SKIP.
- Total: **45 PASS / 0 FAIL / 0 SKIP**.
- Cold boot: PASS; PostgreSQL system identifier remained `7657369583221227555`.
- Screenshot Review: PASS.
- Environment Ready: YES.
- Public Release: READY.

## [0.1.0] - 2026-06-29

### Added

- Initial MySQL and PostgreSQL read-only query support.
- First Provider, Tool, Adapter abstraction, stable JSON format, and Workflow API automation.
- Initial 35 PASS / 0 FAIL / 0 SKIP release freeze before DM8 acceptance.

### Changed

- Moved MySQL/PostgreSQL differences from the shared database helper into independent adapters.
- Froze the first common read-only SQL and JSON behavior.

### Fixed

- Stabilized early Dify platform integration and local database verification paths.

### Security

- Rejected core write and schema-changing statements before database execution.

[Unreleased]: https://github.com/B7G1/Dify_Plugin/compare/v1.0.0...HEAD
[v1.0.0]: https://github.com/B7G1/Dify_Plugin/releases/tag/v1.0.0
[0.1.0]: https://github.com/B7G1/Dify_Plugin/releases/tag/v0.1.0
