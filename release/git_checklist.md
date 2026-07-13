# v1.0 Git Staging Checklist

This checklist is advisory. No Git staging, commit, removal, restore, or push operation is authorized by this document.

## Acceptable tracked deletions

- Root copies of `Dify本地化插件制作流程_最新整理版.html`, `.qmd`, and all 15 `_files` resources, only when the byte-identical `过往报告/01_Dify本地化插件制作流程/` copy enters the same commit.
- The former `reports/day3_plugin_manifest_main_report.md` duplicate is removed; its canonical byte-identical copy is `reports/documentation/Phase2_Plugin_Development/day3_plugin_manifest_main_report.md`.
- Phase 5 `architecture_notes.md`, `daily_summary.md`, and `lessons_learned.md`; the compatibility README must remain.
- Phase 6 `architecture_notes.md`, `daily_summary.md`, and `lessons_learned.md`; the compatibility README must remain.

## Human confirmation before commit

- Confirm the staged diff retains both compatibility README files.
- Confirm the two active Dashboard files contain only the intended path replacements.
- Confirm historical code snapshots are unchanged by this cleanup.
- Confirm every accepted deletion has its canonical or archived counterpart in the same staged change set.

## Untracked content required in the same commit

- `过往报告/01_Dify本地化插件制作流程/`
- `reports/documentation/Phase2_Plugin_Development/day3_plugin_manifest_main_report.md`
- `reports/documentation/Phase7_Domestic_Database_Adapters/`
- `release/deletion_migration_audit.md`
- `release/git_checklist.md`

## Plugin package policy

The only release package is:

- `db_query_extended-0.1.1-dm8-linux-amd64.difypkg`

Do not include the following packages in the v1.0 release commit:

- `db_query_extended.difypkg`
- `db_query_extended/db_query_extended.difypkg`
- `test_tool_schema.difypkg`
- `junjiem-db_query_0.0.11-offline.difypkg`
- `archive/*.difypkg`
- `release/db_query_extended/0.1.0/artifacts/db_query_extended-0.1.0.difypkg`

## Staging rule

- Use explicit paths and inspect the staged diff.
- Do not use `git add .`.
- Do not stage secrets, API keys, passwords, tokens, caches, temporary files, or local runtime state.
