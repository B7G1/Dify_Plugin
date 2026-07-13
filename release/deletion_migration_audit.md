# Deletion Migration Audit

Date: 2026-07-02  
Scope: v1.0 Release Category D tracked deletions

## Conclusion

The 26 tracked deletions were reviewed by content comparison and reference search. The migration is intentional and can enter selective staging after the compatibility and archive conditions below are observed.

## Deleted items

### Quarto report: 17 items

The following deleted root-level items have byte-identical copies under `过往报告/01_Dify本地化插件制作流程/`:

- `Dify本地化插件制作流程_最新整理版.html`
- `Dify本地化插件制作流程_最新整理版.qmd`
- all 15 files below `Dify本地化插件制作流程_最新整理版_files/`

Disposition: safe to accept as moved historical material, provided the archive directory is included in the same release commit. The archived HTML remains self-contained because all 15 supporting resources are present and byte-identical.

### Day 3 report: 1 item

The former `reports/day3_plugin_manifest_main_report.md` had a byte-identical replacement at `reports/documentation/Phase2_Plugin_Development/day3_plugin_manifest_main_report.md`; the duplicate was removed by the 2026-07-12 reporting-governance migration.

Disposition: safe to accept, provided the replacement is included in the same release commit.

### Phase 5 DM Adapter: 4 items

The old README was a planning document. Its goals are represented and superseded by the completed Phase 7 DM8 documentation. A lightweight README now preserves the old path and points to the canonical document.

- `README.md`: retained as a compatibility entry; no longer deleted.
- `architecture_notes.md`: deletion accepted as historical cleanup; the real implementation is documented under Phase 7.
- `daily_summary.md`: deletion accepted as historical cleanup; the old content only stated that work had not started.
- `lessons_learned.md`: deletion accepted as historical cleanup; completed lessons are documented under Phase 7.

Canonical target: `reports/documentation/Phase7_Domestic_Database_Adapters/DM8/README.md`.

### Phase 6 KingbaseES Adapter: 4 items

The Phase 6 planning material was incorporated into Phase 7 Domestic Database Adapters. A lightweight README now preserves the old path and points to the canonical document.

- `README.md`: retained as a compatibility entry; no longer deleted.
- `architecture_notes.md`: deletion accepted as historical cleanup.
- `daily_summary.md`: deletion accepted as historical cleanup.
- `lessons_learned.md`: deletion accepted as historical cleanup.

Canonical target: `reports/documentation/Phase7_Domestic_Database_Adapters/KingbaseES/README.md`.

## Active Dashboard link repairs

| File | Old path | New path | Status |
| --- | --- | --- | --- |
| `reports/html_reports/2026-06-24/project_dashboard.html` | `reports/documentation/Phase5_DM_Adapter/README.md` | `reports/documentation/Phase7_Domestic_Database_Adapters/DM8/README.md` | Updated |
| same file | `reports/documentation/Phase6_KingbaseES_Adapter/README.md` | `reports/documentation/Phase7_Domestic_Database_Adapters/KingbaseES/README.md` | Updated |
| `reports/html_reports/2026-06-24/data/cockpit-data.json` | Phase 5 old path | Phase 7 DM8 path | Updated |
| same file | Phase 6 old path | Phase 7 KingbaseES path | Updated |

Historical code snapshots were intentionally not modified. Their historical text remains valid, and the compatibility README files keep their old navigation targets resolvable.

## Release decision

Category D is resolved for selective staging. This decision does not authorize `git add .`; release files and archive counterparts must be selected explicitly according to `release/git_checklist.md`.
