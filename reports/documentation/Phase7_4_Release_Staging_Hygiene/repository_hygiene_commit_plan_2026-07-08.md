# Repository Hygiene Commit Plan

Date: 2026-07-08

Do not run `git add .`, `git add -A`, `git clean -fd`, `git reset --hard`, commit, or push.

## Proposed narrow sequence

### Commit 2G

Purpose: interactive map synchronization and recursive snapshot fix.

Exact staging allowlist:

```text
db_query_extended_interactive_map/db_query_extended_interactive_map/index.html
db_query_extended_interactive_map/db_query_extended_interactive_map/assets/app.js
db_query_extended_interactive_map/db_query_extended_interactive_map/assets/style.css
db_query_extended_interactive_map/db_query_extended_interactive_map/assets/timeline-data.js
db_query_extended_interactive_map/db_query_extended_interactive_map/assets/code-snapshots.generated.js
db_query_extended_interactive_map/db_query_extended_interactive_map/assets/code-snapshots/step-24-cockpit-and-map/
db_query_extended_interactive_map/db_query_extended_interactive_map/data/
db_query_extended_interactive_map/db_query_extended_interactive_map/scripts/generate_code_snapshots.py
reports/documentation/Phase7_4_Release_Staging_Hygiene/interactive_map_sync_review_2026-07-08.md
```

Exact exclusions:

```text
local_test_db/
release/
analysis/
archive/
*.difypkg
test_tool_schema/
env_check/
```

Production impact: none.

Evidence impact: map and generated snapshot evidence only.

Recommended commit message:

```text
fix: prevent recursive interactive map snapshots
```

### Commit 2H

Purpose: historical report deletion review and current index repair.

Exact staging allowlist:

```text
reports/day3_plugin_manifest_main_report.md
reports/README.md
reports/REPORT_MAP.md
reports/archive/README.md
reports/root_reports/
reports/documentation/Phase5_DM_Adapter/README.md
reports/documentation/Phase6_KingbaseES_Adapter/README.md
reports/documentation/Phase7_4_Release_Staging_Hygiene/remaining_worktree_inventory_2026-07-08.md
reports/documentation/Phase7_4_Release_Staging_Hygiene/historical_report_deletion_review_2026-07-08.md
reports/documentation/Phase7_4_Release_Staging_Hygiene/repository_hygiene_commit_plan_2026-07-08.md
```

Exact exclusions:

```text
reports/documentation/Phase5_DM_Adapter/architecture_notes.md
reports/documentation/Phase5_DM_Adapter/daily_summary.md
reports/documentation/Phase5_DM_Adapter/lessons_learned.md
reports/documentation/Phase6_KingbaseES_Adapter/architecture_notes.md
reports/documentation/Phase6_KingbaseES_Adapter/daily_summary.md
reports/documentation/Phase6_KingbaseES_Adapter/lessons_learned.md
```

Production impact: none.

Evidence impact: preserves unique Day 3 report and fixes current report links after root report consolidation.

Recommended commit message:

```text
docs: review historical reports and repair report indexes
```

### Commit 2I

Purpose: release artifact classification.

Exact staging allowlist:

```text
release/db_query_extended/0.1.0/
reports/documentation/Phase7_4_Release_Staging_Hygiene/package_and_release_artifact_review_2026-07-08.md
```

Exact exclusions:

```text
db_query_extended.difypkg
db_query_extended/db_query_extended.difypkg
junjiem-db_query_0.0.11-offline.difypkg
test_tool_schema.difypkg
```

Production impact: none.

Evidence impact: release package provenance and checksum evidence.

Recommended commit message:

```text
docs: classify release package artifacts
```

### Commit 2J

Purpose: reproducibility test infrastructure.

Exact staging allowlist:

```text
local_test_db/README.md
local_test_db/database_setup_report.md
local_test_db/docker-compose.yml
local_test_db/mysql/
local_test_db/postgres/
local_test_db/dm8/
local_test_db/verification/
start_dify.bat
reports/verification/2026-06-28/
reports/verification/2026-06-29/
reports/verification/2026-06-30/
```

Exact exclusions:

```text
local_test_db/sqlserver/logs/
local_test_db/kingbase/
env_check/.venv/
test_tool_schema/
analysis/
```

Production impact: none.

Evidence impact: improves reproducibility for existing MySQL/PostgreSQL/DM8 evidence.

Recommended commit message:

```text
test: stage reproducibility infrastructure and historical evidence
```

## NEXT commit only

Next recommended commit: **Commit 2G**.

Use the Commit 2G allowlist only. Do not stage unrelated files.
