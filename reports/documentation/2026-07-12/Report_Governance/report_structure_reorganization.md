# Documentation Hygiene Gate — Canonical Report Structure

- Date: 2026-07-12
- Phase: Report Governance
- Status: PARTIAL
- Database: NOT_APPLICABLE
- Scope: Repository-wide report inventory, safe canonical migration, duplicate removal, permanent policy, and validation
- Source commit: `736902d` baseline; governance commit pending
- Runtime: Windows PowerShell; Git; in-app browser local-map validation
- Canonical path: `reports/documentation/2026-07-12/Report_Governance/report_structure_reorganization.md`
- Machine evidence: `reports/verification/2026-07-12/report_reorganization_manifest.json`, `reports/verification/2026-07-12/report_structure_validation.json`
- Logs: NOT_APPLICABLE
- Supersedes: NOT_APPLICABLE
- Security classification: Internal engineering; secrets and local media excluded

## Executive Summary

The repository now has one active reporting policy, a dated canonical path for current KingbaseES reporting, a dated home for the root-level acceptance/planning reports moved in this pass, and no active canonical exact duplicate. The byte-identical root Day 3 report was removed after its canonical Phase 2 copy was verified.

The gate is `PARTIAL`, not PASS. A repository-wide physical migration would require rewriting or regenerating an interactive-map tree that already contains protected user modifications, and the reports root contains protected untracked generated HTML. Those files were inspected but not overwritten. Legacy phase-first reports are therefore explicitly `HISTORICAL_ONLY` migration inputs; new reports may not use those paths.

From this change onward, all report-related tasks are governed by `reports/REPORTING_STANDARD.md`.

## Goal and Acceptance Boundary

The requested end state is dated canonical human reports, preserved machine evidence and logs, no competing report copies, a unique `REPORT_MAP`, valid links, intact interactive-map behavior, and a permanent enforceable standard.

Safety boundaries took precedence: no product code, database container, database volume, external media, credentials, or existing user edits could be overwritten or staged. Therefore a global physical move could not honestly be declared complete.

## Baseline

- Branch: `feature/kingbasees-adapter`
- Baseline commit: `736902d docs: verify KingbaseES official runtime gate`
- Existing dirty worktree recorded before changes.
- KingbaseES container and data volume were not stopped, changed, or deleted.

## Environment and inventory

Scanned recursively across the repository root, `reports`, `analysis`, `archive`, `env_check`, `local_test_db`, `db_query_extended`, `db_query_extended_interactive_map`, verification/documentation/log/HTML trees, generated data, and code snapshots. Excluded dependency environments and Git internals from report classification.

Initial inventory:

- 511 report/evidence/log/image candidates
- 266 human-readable candidates
- 220 tracked human-readable candidates
- 99 machine-evidence candidates under the broad scan definition
- 28 raw-log candidates under the broad scan definition
- 96 historical snapshot/generated-history candidates
- 5 exact human-readable duplicate groups

Four exact groups were interactive-map/generated or historical copies, not competing canonical reports. One active exact duplicate was the root Day 3 report and its Phase 2 copy. No separate high-overlap pair required content merging; reports that cover a shared subject but different runs/statuses were kept as separate evidence boundaries.

## Canonical structure adopted

```text
reports/documentation/YYYY-MM-DD/PhaseXX_Subject/report.md
reports/verification/YYYY-MM-DD/evidence.json
reports/logs/YYYY-MM-DD/PhaseXX_Subject/raw.log
reports/assets/YYYY-MM-DD/PhaseXX_Subject/image.png
reports/generated/html/YYYY-MM-DD/PhaseXX_Subject/report.html
```

`reports/README.md`, `reports/REPORT_MAP.md`, and `reports/REPORTING_STANDARD.md` are the root entry points. The only template added is the reusable phase report template; optional speculative templates were skipped.

## Work performed

Moved and normalized metadata:

- Phase 9.4 KingbaseES runtime PASS report to `reports/documentation/2026-07-10/Phase09_KingbaseES/phase9_4_official_media_image_runtime_gate.md`.
- Phase 9 pre-media BLOCKED report to `reports/documentation/2026-07-09/Phase09_KingbaseES/phase9_official_media_runtime_feasibility.md`, marked `SUPERSEDED` without rewriting its historical conclusion.
- v1.0 final release check and acceptance evidence index to `reports/documentation/2026-07-02/Final_Delivery/`.
- Phase 10 planning-only root report to `reports/documentation/2026-07-02/Phase10_KingbaseES/phase10_preparation.md`.

Removed:

- `reports/day3_plugin_manifest_main_report.md`, because its SHA-256 exactly matched `reports/documentation/Phase2_Plugin_Development/day3_plugin_manifest_main_report.md`.

Updated links and indexes in `REPORT_MAP`, report README, release documentation, historical hygiene notes, and one machine-specific SQL Server evidence link.

## Permanent policy and templates

- Added `reports/REPORTING_STANDARD.md`, version 1.0, ACTIVE.
- Added `reports/templates/PHASE_REPORT_TEMPLATE.md`.
- Updated `AGENTS.md` so every report creation, cleanup, reorganization, archive, consolidation, validation-documentation, and evidence-index task must first read the standard.

Default future behavior is now fixed: inspect Git state, choose one dated canonical report, separate evidence/logs/assets/generated output, compare duplicates, update links and `REPORT_MAP`, redact secrets, validate, and stage exact paths only.

## Historical snapshots and HTML

Code snapshots and interactive-map copies were retained because they preserve historical reconstruction and the current map depends on them. They are classified `HISTORICAL_SNAPSHOT / NON_AUTHORITATIVE` and are excluded from canonical duplicate counts.

Existing HTML was not promoted as an authoring source. The dirty untracked `reports/README.html` and `reports/REPORT_MAP.html`, plus the legacy `reports/html_reports` tree, were not deleted or regenerated because doing so would overwrite protected user/generated state. Future clean migration must place generated HTML under `reports/generated/html/YYYY-MM-DD/PhaseXX_Subject/`.

## Verification results

- Current canonical moved-path existence: PASS
- Exact duplicate canonical reports after migration: 0
- Root-level phase report count: 0
- Tracked Markdown link check after new artifacts: 0 broken links
- `REPORT_MAP` target existence: PASS for indexed targets
- Interactive map load: PASS (`http://127.0.0.1:8765/index.html`, visible body, expected title/H1, 13 links, 4 scripts, zero console errors)
- Product code changed: NO
- KingbaseES/Dify/DM8/SQL Server/MySQL/PostgreSQL runtime touched: NO
- Final live Docker inventory recheck: UNAVAILABLE because the Docker daemon was not reachable on 2026-07-12; no stop/delete/prune command was issued by this gate
- External assets still ignored and sensitive assets staged: NO
- Reports-root strict cleanliness: BLOCKED by protected untracked `.Rhistory`, `README.html`, and `REPORT_MAP.html`
- Full legacy phase-first physical migration: DEFERRED to avoid overwriting dirty interactive-map/user report work

## Evidence

- Migration actions: `reports/verification/2026-07-12/report_reorganization_manifest.json`
- Validation metrics: `reports/verification/2026-07-12/report_structure_validation.json`

No machine evidence, raw logs, screenshots, database backups, or distinct execution batches were deleted.

## Decisions

Chosen: migrate only clean, unambiguous current/root reports; remove one proven exact duplicate; establish the permanent rule; mark the remaining legacy boundary explicitly.

Rejected: bulk regeneration of the interactive map, because it would overwrite user modifications; mass date inference and movement of all historical reports, because it would create unaudited links and potentially merge distinct runs; archive copies, because Git already preserves deleted versions.

## Blockers

Observed symptoms: legacy phase-first and generated HTML paths remain; the final Docker inventory recheck could not reach the daemon.

Expected behavior: every active human report uses the dated canonical structure and generated HTML has one generated location.

Evidence: dirty interactive-map files, dirty/untracked generated HTML, and protected untracked Phase 11/recovery report work existed before this gate.

Root cause: the requested global migration conflicts with the explicit requirement not to overwrite or stage user changes. Docker reachability is a separate environment-state blocker, not caused or modified by report governance.

Fix in this gate: establish the standard, migrate the clean current subset, and record every deferred class.

Recovery condition: first commit or otherwise isolate the protected user changes; then migrate the legacy report tree and generator references in a separate reviewed documentation-only commit.

## Security and Redaction

No password, token, API key, license content, `.env`, ISO, Docker tar, database data, or external media was added. Local asset paths are inventory facts only and are not permanent repository links.

## Reproduction Trace

Use PowerShell from `E:\Dify_Plugin`: read `AGENTS.md` and `reports/REPORTING_STANDARD.md`; run `git status --short`; inventory candidate extensions; calculate SHA-256 duplicate groups; validate Markdown targets; check `REPORT_MAP` targets; run a temporary local HTTP server for the interactive map; inspect browser title, H1, assets, and console; stop the temporary server; run `git diff --check`; inspect exact staged paths.

Failure means either a canonical/report target is missing, a canonical duplicate remains, the map has runtime console errors, a sensitive asset is tracked, or unrelated user/product work entered the staged set.

## Git State

This report-governance change is staged and committed independently from product code. Exact commit is recorded after creation.

## Final Decision

`PARTIAL`

The permanent standard is active and validated against this real cleanup. Canonical migration is complete for the current KingbaseES and selected root reports, but the entire legacy tree cannot be declared canonical until protected user/generated changes are isolated.

## Next Step

After the protected report/map changes are isolated, finish the legacy dated-path migration. The next technical gate remains official KingbaseES driver/dialect installation and import in plugin-daemon Python 3.12; it was not started here.
