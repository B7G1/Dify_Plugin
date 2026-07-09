# SQL Server Local Test Environment

Status: **PASS** — the operator explicitly accepted the EULA, supplied runtime-only credentials, and completed initialization plus readonly verification.

This directory is independent of MySQL, PostgreSQL, DM8, and KingbaseES. It uses its own Compose project, container, port, named volume, initialization SQL, verification scripts, and logs.

## License and edition

- Image: `mcr.microsoft.com/mssql/server:2022-latest` from Microsoft Container Registry.
- Edition: Developer (`MSSQL_PID=Developer`), for development/test rather than production.
- Microsoft requires acceptance of its SQL Server container terms.
- This repository does not set or imply acceptance. The operator must review the terms and explicitly set `ACCEPT_EULA=Y` in the current process.

Reference: [Microsoft SQL Server Linux container quick start](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver16).

## Required operator input

```powershell
$env:ACCEPT_EULA = 'Y' # only after personally reviewing and accepting Microsoft terms
$env:MSSQL_SA_PASSWORD = Read-Host 'Local SQL Server SA password' -AsSecureString
```

For actual script use, convert secrets into current-process environment strings without writing them to `.env`, scripts, reports, logs, or Git. Also set `MSSQL_READONLY_PASSWORD` to a separate strong local test password.

Then run:

```powershell
Set-Location E:\Dify_Plugin\local_test_db\sqlserver
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\prepare.ps1
```

If EULA acceptance, credentials, Docker pull, startup, initialization, or verification fails, the script exits with status 2 and records BLOCKED evidence under `logs/`.

## Validated connection

```text
host=localhost
port=1433
database=plugin_test
schema=plugin_test
username=plugin_readonly
password=<MSSQL_READONLY_PASSWORD from current process>
driver candidate=pymssql
SQLAlchemy URL candidate=mssql+pymssql://...
```

The environment gate passed. Driver/package compatibility remains outside Phase 11.1 scope.

## Safe lifecycle

Stop while retaining data:

```powershell
docker compose stop
```

Do not run `docker compose down -v` without explicit approval because it deletes the SQL Server test volume.
