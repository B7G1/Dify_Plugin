# Environment Migration and Recovery Guide

## Prerequisites

- Windows with Docker Desktop and WSL 2
- Git
- Python 3.11 for development tools
- Poetry, if used by the host development workflow
- Dify Plugin CLI compatible with the installed SDK
- Access to the DM8 server and vendor driver packages
- A secure channel for credentials; never copy secrets into this repository

## Files to transfer

Transfer the repository, the release package, and separately secured database backups. Docker named volumes are machine-local and are not transferred by copying the repository.

## Restore order

1. Install and start WSL 2 and Docker Desktop.
2. Clone or copy the repository and check out the frozen Git commit recorded in `BASELINE.md`.
3. Restore approved PostgreSQL/Weaviate backups into newly created named volumes when migrating data. Do not reuse temporary `/tmp` Compose files.
4. Confirm the required Compose source tree and fixed overrides referenced by `start_dify.ps1` exist.
5. Start only through:

   ```powershell
   & 'E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1'
   ```

6. Run `dify_preflight.ps1`; confirm `dify`, `dify_plugin`, accounts, tenants, and stable plugin daemon state.
7. Install `db_query_extended.difypkg` only if it is not present.
8. Recreate DM8 Provider credentials through Dify UI. Never import them from documentation.
9. Import/recreate the Workflow, publish it, and create a new Workflow API key.
10. Set `DIFY_WORKFLOW_API_URL` and `DIFY_WORKFLOW_API_KEY` only in the current process environment.
11. Run `verify_all.ps1`; require 45 PASS / 0 FAIL / 0 SKIP.

## Recovery checks

- Compose project is exactly `dify`; no `docker-*` project participates.
- PostgreSQL and Weaviate use stable named volumes.
- `/install` does not request initialization when restoring an existing Console database.
- Plugin is version 0.1.1, Provider validates, Workflow succeeds, and API returns HTTP 200.

For an existing machine, use the exact recovery entry in `BASELINE.md`. Database restoration is a separate, reviewed operation and must not overwrite working volumes without a backup.
