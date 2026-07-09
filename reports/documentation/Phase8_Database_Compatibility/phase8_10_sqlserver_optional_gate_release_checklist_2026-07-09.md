# Phase 8.10 - SQL Server Optional Gate Release Checklist

Verdict: PASS - SQLSERVER_RELEASE_CHECKLIST_READY

## Goal

Document when the SQL Server optional gate can be run, how to run it, what it depends on, and what its PASS result does not mean.

## Current Status

SQL Server optional gate status: READY

Validated before this checklist:

- Phase 8.6 offline packaging gate: PASS
- Phase 8.7 plugin-daemon runtime gate: PASS
- Phase 8.8 real Dify/plugin-daemon tool validation: PASS
- Phase 8.9 repeatable optional validation gate: PASS

This checklist does not promote SQL Server into the default main verification matrix.

## Why This Does Not Enter The Main Matrix Yet

The gate depends on local integration state that is not suitable for default `verify_all.ps1` execution:

- local SQL Server Docker fixture must be running
- local Dify and plugin-daemon must be running
- SQL Server candidate plugin must already be installed in Dify
- local SQL Server env file or equivalent environment variables must be present
- failure modes still need explicit separation between missing local environment and product regression

Do not treat optional gate PASS as full release PASS.

## Run Prerequisites

Required local components:

- Docker Desktop running
- Dify baseline running through the project startup flow
- `dify-api-1` reachable
- `dify-plugin_daemon-1` running
- SQL Server test container running and healthy
- SQL Server candidate plugin installed in Dify
- provider credential named `SQL Server Local Readonly` present in Dify

## SQL Server Local Fixture

Fixture directory:

`local_test_db/sqlserver/`

Environment preparation script:

```powershell
Set-Location E:\Dify_Plugin\local_test_db\sqlserver
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\prepare.ps1
```

The SQL Server environment requires explicit Microsoft EULA acceptance in the current process before setup. It uses Microsoft official SQL Server 2022 Developer image for local development and testing.

Expected fixture:

- database: `plugin_test`
- schema: `plugin_test`
- readonly user: `plugin_readonly`
- tables:
  - `plugin_test.plugin_test_users`
  - `plugin_test.plugin_test_orders`
  - `plugin_test.plugin_test_logs`

Readonly fixture verification:

```powershell
Set-Location E:\Dify_Plugin\local_test_db\sqlserver
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verification\verify.ps1
```

## Dify And Plugin-Daemon Preconditions

Before running the optional gate:

- Dify Console must not be in first-install mode
- plugin-daemon must not be in restart loop
- the installed `db_query_extended` plugin must be the SQL Server candidate build
- provider schema must expose `sqlserver`
- SQL Server provider credential validation must be possible through Dify/plugin-daemon

Candidate checksum note:

- the installed plugin identifier should match the SQL Server candidate lineage
- full checksum must stay out of checklist docs and routine reports
- record only redacted form when needed, such as `li_zijun/db_query_extended:0.1.1@<redacted>`

## Env File Preconditions

Default env file:

`db_query_extended/verification/.sqlserver_probe.env`

Required variable names:

- `SQLSERVER_HOST`
- `SQLSERVER_PORT`
- `SQLSERVER_DATABASE`
- `SQLSERVER_USERNAME`
- `SQLSERVER_PASSWORD`

Optional variable names:

- `SQLSERVER_SCHEMA`
- `SQLSERVER_CONNECT_TIMEOUT`
- `SQLSERVER_DIFY_HOST`
- `DIFY_API_CONTAINER`
- `DIFY_SQLSERVER_CREDENTIAL_NAME`

The env file is local-only and must not be committed.

## Run Command

```powershell
python E:\Dify_Plugin\db_query_extended\verification\sqlserver_tool_validation_gate.py `
  --env-file E:\Dify_Plugin\db_query_extended\verification\.sqlserver_probe.env `
  --output E:\Dify_Plugin\reports\verification\2026-07-09\sqlserver_tool_validation_gate_rerun.json
```

## Expected PASS Criteria

The optional gate may be marked PASS only when all checks pass:

- provider credential exists
- Dify/plugin-daemon runtime credential validation returns true
- `SELECT 1 AS probe_value` succeeds
- `SELECT TOP 5 ...` succeeds
- Unicode fixture read succeeds
- schema-qualified read succeeds
- each result contains `columns`, `rows`, `row_count`, `truncated`, and `max_rows`
- every tool result reports `database_type = sqlserver`
- artifact does not record password, token, cookie, or full checksum

## Artifact Output

Default rerun artifact:

`reports/verification/2026-07-09/sqlserver_tool_validation_gate_rerun.json`

Reference artifacts:

- `reports/verification/2026-07-09/sqlserver_tool_validation_gate.json`
- `reports/verification/2026-07-09/sqlserver_plugin_runtime_gate.json`

## Secret Hygiene

Do not write these into docs, reports, artifacts, commits, screenshots, or logs:

- SQL Server password
- Dify browser cookies
- Dify access token
- Dify refresh token
- CSRF token
- full plugin checksum

Allowed in reports:

- credential field names
- credential display name
- local fixture database name
- local fixture schema name
- local fixture username
- redacted plugin identifier

## Known Non-Blockers

These do not block optional gate usage:

- SQL Server gate is not part of `verify_all.ps1`
- SQL Server gate depends on a local env file
- SQL Server gate requires an already running Dify/plugin-daemon stack
- SQL Server gate writes a dated local artifact

## Known Blockers

These block optional gate PASS:

- SQL Server Docker fixture is not running or not initialized
- Dify/plugin-daemon is not running
- candidate plugin is not installed in Dify
- provider schema does not expose `sqlserver`
- `SQL Server Local Readonly` credential is absent
- env file or equivalent env vars are missing
- tool result does not report `database_type = sqlserver`
- output JSON contract keys are missing
- secret values appear in artifact or report

## When Main Matrix Integration Is Allowed

SQL Server can be considered for main matrix integration only after:

- plugin package install gate is fixed into a repeatable command
- candidate checksum update flow is automated or documented as an operator step
- SQL Server local fixture is one-command reproducible
- env file or secret injection is standardized
- verification output distinguishes environment missing from product failure
- MySQL/PostgreSQL/DM baseline remains unaffected
- CI or baseline runner can intentionally include or exclude SQL Server

Until then, SQL Server remains an optional release gate.

## Rollback And Cleanup Notes

Safe cleanup:

- stop SQL Server test container with `docker compose stop`
- keep SQL Server named volume unless explicitly resetting fixture data
- leave `.sqlserver_probe.env` local-only

Do not run destructive cleanup such as `docker compose down -v` without explicit approval.

If the installed plugin points to the wrong build, reinstall or upgrade using the project package flow, then rerun Phase 8.7 and Phase 8.9 evidence.

## Next Recommendation

Keep SQL Server as an optional gate for the next release documentation pass. Do not promote it into `verify_all.ps1` until the environment and install flow are fully reproducible.
