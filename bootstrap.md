# Bootstrap Guide

## What `bootstrap.ps1` does

The script performs safe orchestration around the frozen v1.0 startup path:

1. Checks Git, WSL, Python, Docker Desktop WSL integration, the fixed repository location, and the accepted Dify source tree.
2. Refuses to continue when a prerequisite is ambiguous.
3. Calls only `db_query_extended/verification/start_dify.ps1`.
4. Relies on the established preflight to validate volumes, databases, administrator/tenant records, storage, and plugin daemon stability.

It never deletes containers, volumes, databases, backups, or credentials.

```powershell
# Check only
.\bootstrap.ps1 -CheckOnly

# Check, start, and preflight
.\bootstrap.ps1

# Preflight an already running baseline
.\bootstrap.ps1 -SkipStart
```

If the machine's PowerShell execution policy blocks local scripts, use the process-scoped form without changing the system policy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\bootstrap.ps1
```

## Fresh Windows computer

1. Install Git for Windows.
2. Enable WSL 2 and install the accepted Linux distribution.
3. Install Docker Desktop and enable WSL integration.
4. Install Python 3.11; install Poetry and Dify Plugin CLI for development/package work.
5. Clone this repository to the frozen location:

   ```powershell
   git clone https://github.com/B7G1/Dify_Plugin.git E:\Dify_Plugin
   ```

6. Restore the accepted Dify fork at `/home/zli2759/projects/dify-dm` inside WSL.
7. Restore approved database/volume backups if Console state must migrate.
8. Run `E:\Dify_Plugin\bootstrap.ps1`.
9. Through Dify UI, restore or create Provider credentials, Workflow, and a fresh API key when they were not part of the database backup.
10. Inject the API key into the current process and run `verify_all.ps1`.

## Why recovery is not fully unattended

| Constraint | Reason |
| --- | --- |
| Docker Desktop and WSL installation | requires Windows administrator actions and sometimes restart |
| Accepted Dify fork | currently external to this repository and frozen at a WSL path |
| PostgreSQL/Weaviate data | machine-local named volumes require an explicit backup/restore decision |
| DM8 | vendor server, licensing, network route, and drivers are external |
| Provider/API credentials | secrets must not be embedded in Git or bootstrap scripts |
| UI objects without database backup | plugin installation, Provider, and Workflow require authenticated Dify actions |

Further automation should parameterize the external Dify source location and add signed backup import/export. It must not silently create credentials or replace existing volumes.
