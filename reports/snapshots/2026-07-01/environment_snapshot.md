# Environment Snapshot — 2026-07-01 Final Acceptance

Captured before the final cold-boot verification. Secrets and API keys are intentionally excluded.

## Source state

- Git commit: `9705c619a26a690925421fd5dd522d6e644dbc48`
- Branch: `main`
- Upstream state: `main...origin/main [ahead 3]`
- Worktree: dirty; existing user changes and untracked project artifacts were preserved.

## Compose baseline

- Compose project: `dify`
- Docker Compose: `v5.1.3`
- Startup entry: `db_query_extended/verification/start_dify.ps1`
- Compose files, in merge order:
  1. `/home/zli2759/projects/dify-dm/docker/docker-compose.yaml`
  2. `/home/zli2759/projects/dify-dm/outputs/dm_change_matrix/regression_scripts/plugin_daemon.local.override.yaml`
  3. `/mnt/e/Dify_Plugin/db_query_extended/verification/dify.middleware.override.yaml`
  4. `/mnt/e/Dify_Plugin/db_query_extended/verification/dify.baseline.override.yaml`
- Profiles: `postgresql`, `weaviate`
- Managed services: `db_postgres`, `init_plugin_database`, `init_permissions`, `redis`, `api`, `plugin_daemon`, `sandbox`, `ssrf_proxy`, `weaviate`, `web`, `nginx`, `worker`, `worker_beat`.

## Persistent volumes before cold boot

- `dify_postgres_data_v1`
- `dify_weaviate_data_v1`
- `dify_app_storage`
- `dify-plugin-local-test-db_mysql_data`
- `dify-plugin-local-test-db_postgres_data`
- Compose-created anonymous helper volumes present before cold boot:
  - `0f85720e1916db54cf27af5488f4cae2179682d7750a8b8e06bfaf070537fe51`
  - `9f00b0e32354f866fd4381f6a01354385871a220de1dcf92fa929635fe60030c`
  - `89c3486798cc71a1d9b26ba17fba03e5ee3c79d68d5981369c2b04cf3d4b16c5`
  - `95a18ea1b1e245c51e448a98ab6afd40d8b6b8308caab74143cb6d69b51db0c9`
  - `680c3d5291ae7cfceba76d6858e452de04243e62a8854ddffdf43274a29c190c`
  - `a1e3d5b74615125b9351e7337159d69e84911432a440e2d64a4bdc243db1f446`
  - `a58c5f898d7eaa3b22ee8eaa9a47f0139bfd4570c4ec73082c5129e7d2711ab0`

The final comparison is based on this exact set; no volume is deleted or recreated during acceptance.

## Database and application identity

- PostgreSQL image: `postgres:15-alpine`
- PostgreSQL system identifier: `7657369583221227555`
- Required databases: `dify`, `dify_plugin`
- Dify API/Web version: `1.13.3`
- Plugin daemon image/version: `langgenius/dify-plugin-daemon:0.5.3-local`
- Plugin: `li_zijun/db_query_extended` version `0.1.1`
- Workflow name: `DM8 Readonly SQL Acceptance`
- Workflow/App ID: `ec11fbde-d77c-4818-bcdf-b2b483dffe3d`
- Workflow API URL: `http://localhost/v1/workflows/run`

## Container baseline before cold boot

The `dify` project managed PostgreSQL, Weaviate, Redis, API, workers, Web, Nginx, sandbox, SSRF proxy, plugin daemon, and the two idempotent initialization jobs. Runtime container details are retained by `docker inspect`; no credentials are copied into this snapshot.

## Recovery entry

```powershell
& 'E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1'
```

Do not start a `docker-*` Compose project and do not bypass this entry with an alternate middleware file.

## Cold-boot comparison

- Full `dify` project stop: PASS; zero running project containers remained.
- Restart entry: `start_dify.ps1` only.
- Persistent volume set: unchanged.
- PostgreSQL system identifier after restart: `7657369583221227555` (unchanged).
- Required databases after restart: `dify`, `dify_plugin`.
- Plugin daemon after restart: running, restart count 0.
- Installed plugin after restart: `li_zijun/db_query_extended` `0.1.1`.
- Final automation: 45 PASS / 0 FAIL / 0 SKIP.
