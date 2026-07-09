# Remaining Worktree Inventory

Date: 2026-07-08  
Branch observed: `feature/kingbasees-adapter`

This inventory classifies the remaining dirty/untracked workspace after v1.0 baseline and Phase 7.4 staging work. It is not a staging command. Do not use `git add .`.

## Classification table

| Path/group | Git state | Classification | Canonical? | Recommended action | Reason |
| --- | --- | --- | --- | --- | --- |
| `db_query_extended_interactive_map/` | modified + untracked nested data/assets | `ACTIVE_PROJECT_ASSET` | Yes | Stage only after map sync review. | Interactive map is a deliverable. Changes update the map UI and generated snapshots. |
| `reports/day3_plugin_manifest_main_report.md` | restored from tracked deletion | `HISTORICAL_REPORT` | Yes, historical | Keep restored. | Contains unique Day 3 Provider/Tool/manifest evidence; not a duplicate. |
| `reports/documentation/Phase5_DM_Adapter/architecture_notes.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Old file only said “Not started”; Phase 5 now points to Phase 7 DM8 evidence. |
| `reports/documentation/Phase5_DM_Adapter/daily_summary.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Placeholder only; no unique evidence. |
| `reports/documentation/Phase5_DM_Adapter/lessons_learned.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Placeholder only; no unique evidence. |
| `reports/documentation/Phase6_KingbaseES_Adapter/architecture_notes.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Old file only said future scope; Phase 6 now points to Phase 7 domestic adapter docs. |
| `reports/documentation/Phase6_KingbaseES_Adapter/daily_summary.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Placeholder only; no unique evidence. |
| `reports/documentation/Phase6_KingbaseES_Adapter/lessons_learned.md` | deleted tracked | `HISTORICAL_DUPLICATE` | No | Keep deletion if compatibility README is staged. | Placeholder only; no unique evidence. |
| `analysis/` | untracked | `LOCAL_ONLY_ARTIFACT` | No | Do not stage; consider ignore or archive outside release. | Third-party reference plugin extraction and wheel cache, about 111 MB with many binaries. |
| `archive/` | untracked | `HISTORICAL_REPORT` / `RELEASE_ARTIFACT` | Partial | Stage only if policy says historical packages belong in repo. | Contains early `.difypkg` packages and `.gitkeep`; useful history but not current source. |
| root-level `*.difypkg` | untracked | `RELEASE_ARTIFACT` / `LOCAL_ONLY_ARTIFACT` | No, except duplicate reference | Do not stage root copies. | Root `db_query_extended.difypkg` duplicates the release artifact hash; others are third-party/test artifacts. |
| `db_query_extended/*.difypkg` | untracked | `LOCAL_ONLY_ARTIFACT` | No | Do not stage. | Local package output from early build, not proven release candidate. |
| `local_test_db/` | untracked | `TEST_INFRASTRUCTURE` | Yes for reproducibility | Stage selectively in a dedicated commit. | Needed to reproduce MySQL/PostgreSQL/DM8 fixtures and Phase 11 environment gates. |
| `release/db_query_extended/` | untracked | `RELEASE_ARTIFACT` | Yes | Stage as release artifact commit after package review. | Contains structured release 0.1.0 package, metadata, checksums, and verification outputs. |
| `env_check/` | untracked | `LOCAL_ONLY_ARTIFACT` | No | Do not stage `.venv`; stage only small manifest if needed. | Contains a local virtual environment and dependency experiment files. |
| `test_tool_schema/` | untracked | `LOCAL_ONLY_ARTIFACT` | No | Do not stage. | Separate test plugin scaffold, not current product source. |
| `staged.txt` | untracked | `SAFE_TO_IGNORE` | No | Do not stage; consider narrow ignore. | Temporary staging list. |
| `start_dify.bat` | untracked | `TEST_INFRASTRUCTURE` | Yes, convenience | Stage only after manual review. | Windows convenience entrypoint; does not change plugin runtime. |
| `reports/architecture/` | untracked | `HISTORICAL_REPORT` | Yes | Stage with report structure commit. | Report taxonomy pointer. |
| `reports/archive/` | untracked + modified README | `HISTORICAL_REPORT` | Yes | Stage with report/index commit. | Defines archive policy; updated for `reports/root_reports/`. |
| `reports/verification/2026-06-28/` | untracked | `HISTORICAL_REPORT` | Yes | Stage as machine evidence. | Architecture freeze evidence. |
| `reports/verification/2026-06-29/` | untracked | `HISTORICAL_REPORT` | Yes | Stage as dated machine evidence. | DM8 draft/partial evidence; historical, not current PASS statement. |
| `reports/verification/2026-06-30/` | untracked | `HISTORICAL_REPORT` | Yes | Stage as dated machine evidence, but review dumps policy. | Persistence migration, backups, startup evidence. |
| `reports/documentation/Phase11_Database_Expansion/` | untracked | `HISTORICAL_REPORT` | Yes | Stage docs only; no adapter implementation. | Feasibility report for later expansion. |
| `reports/documentation/Phase11_SQLServer_Adapter/` | untracked | `HISTORICAL_REPORT` | Yes | Stage docs only. | SQL Server environment gate report; not plugin integration. |
| `reports/documentation/Phase4_Core_Freeze/2026-06-26/recovery/` | untracked | `HISTORICAL_REPORT` | Yes | Stage if docx/html/md recovery guide is desired. | Recovery guide; no runtime impact. |
| `reports/README.html` | untracked | `GENERATED_ARTIFACT` | No | Do not stage unless HTML report policy includes it. | Rendered form of report index. |
| `reports/root_reports/` | untracked | `HISTORICAL_REPORT` | Yes | Stage with report consolidation commit. | Consolidated loose root-level report artifacts without deletion. |

## Current conclusion

The repository is **not clean**. It is now more explainable, but several groups still require narrow staging decisions.

Next useful commit: interactive map synchronization plus its review report.

## Analysis / archive classification

`analysis/` was inspected as a third-party reference extraction, not current project source. It contains a copied plugin tree, images, Python code, YAML, and 54 wheel files. It should not be staged in a product commit.

`archive/` contains historical `.difypkg` packages. It may be useful as history, but it is not the current release artifact location.

Narrow secret scan result, values not printed:

| Path | Pattern category | Human action required |
| --- | --- | --- |
| `analysis/junjiem-db_query_0.0.11/tools/db_util.py` | password/credential handling reference | Review before any staging; do not stage by default. |
| `analysis/junjiem-db_query_0.0.11/tools/sql_query.py` | password/credential handling reference | Review before any staging; do not stage by default. |
| `analysis/junjiem-db_query_0.0.11/tools/sql_query.yaml` | secret/input schema reference | Review before any staging; do not stage by default. |

No secret values were printed during this scan.

## Test infrastructure classification

| Path/group | Classification | Recommended action |
| --- | --- | --- |
| `local_test_db/mysql/` | required reproducibility asset | Stage in a dedicated reproducibility commit. |
| `local_test_db/postgres/` | required reproducibility asset | Stage in a dedicated reproducibility commit. |
| `local_test_db/dm8/` | required reproducibility asset | Stage in a dedicated reproducibility commit; fixture credentials are deterministic local test credentials only. |
| `local_test_db/kingbase/` | blocked environment preparation | Do not present as PASS; stage only if documenting blocked Kingbase setup. |
| `local_test_db/sqlserver/` | Phase 11 environment gate | Stage docs/scripts separately from v1.0 regression. |
| `local_test_db/sqlserver/logs/` | generated logs | Do not stage unless a specific log is cited by a report. |
| `env_check/` | local dependency experiment | Do not stage `.venv`; stage neither by default. |
| `test_tool_schema/` | separate scaffold/test plugin | Do not stage in product release. |
| `start_dify.bat` | optional local convenience | Stage only after reviewing it does not bypass `start_dify.ps1`. |

## `.gitignore` review

Current `.gitignore` already covers:

- local CLI binaries;
- OS/editor noise;
- `.env` files except `.env.example`;
- Python caches;
- temporary editor output;
- private key material.

Potential narrow additions for a later cleanup commit:

```text
staged.txt
*.difypkg
!release/**/artifacts/*.difypkg
local_test_db/sqlserver/logs/
env_check/.venv/
```

Do not ignore broad directories such as `reports/`, `archive/`, `analysis/`, or all `*.html`.
