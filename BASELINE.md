# Stable Development Baseline — 2026-07-01

## Status

- Product version: **v1.0.0**
- Plugin version: **0.1.1**
- Project Status: **RELEASED**
- Technical acceptance: **PASS**
- Automated verification: **45 PASS / 0 FAIL / 0 SKIP**
- Screenshot Review: **PASS** — current v1.0 captures were manually approved for public display
- Environment Ready: **YES**
- Public Release: **READY**

## Frozen identity

- Git commit: `9705c619a26a690925421fd5dd522d6e644dbc48`
- Branch: `main` (dirty worktree was preserved; this document does not imply a clean commit)
- Compose project: `dify`
- Startup entry: `E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1`
- PostgreSQL system identifier: `7657369583221227555`
- PostgreSQL volume: `dify_postgres_data_v1`
- Weaviate volume: `dify_weaviate_data_v1`
- Application storage volume: `dify_app_storage`
- Dify: `1.13.3`
- Plugin daemon: `langgenius/dify-plugin-daemon:0.5.3-local`
- Plugin: `li_zijun/db_query_extended` `0.1.1`
- Workflow ID: `ec11fbde-d77c-4818-bcdf-b2b483dffe3d`
- Workflow API URL: `http://localhost/v1/workflows/run`

No password or API key is stored in this baseline.

## Recovery

1. Start Docker Desktop and WSL.
2. Run only:

   ```powershell
   & 'E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1'
   ```

3. Run `dify_preflight.ps1` and confirm system identifier `7657369583221227555`.
4. Confirm `dify` and `dify_plugin` exist and `plugin_daemon` is not restarting.
5. Inject the Workflow API key only into the process environment, then run `verify_all.ps1`.

Do not start a `docker-*` Compose project, bypass `start_dify.ps1`, recreate named volumes, or place credentials in files, reports, scripts, or Git.

## Evidence

- Snapshot: `reports/snapshots/2026-07-01/environment_snapshot.md`
- Final acceptance: `reports/documentation/Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md`
- Machine evidence: `reports/verification/2026-07-01/final_cold_boot/`

This baseline is the sole starting point for later adapters such as KingbaseES and Oracle. Existing DM8 behavior must remain regression-tested.
