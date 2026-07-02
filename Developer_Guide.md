# Developer Guide

## 1. What this project is

`db_query_extended` is a Dify read-only SQL Tool. v1.0 supports MySQL, PostgreSQL, and DM8 through a shared adapter layer and has a 45-check real acceptance baseline. New work must preserve that baseline.

## 2. Start here

Read, in order:

1. `BASELINE.md`
2. `architecture/README.md`
3. `reports/release/v1.0/Compatibility.md`
4. `reports/verification/2026-07-01/final_cold_boot/README.md`

Primary directories:

| Path | Purpose |
| --- | --- |
| `db_query_extended/` | plugin source and package assets |
| `db_query_extended/provider/` | Provider schema and credential validation |
| `db_query_extended/tools/` | Tool contract and execution entry |
| `db_query_extended/utils/adapters/` | database-specific adapters |
| `db_query_extended/verification/` | startup, preflight, and acceptance runners |
| `architecture/` | current architecture |
| `reports/documentation/` | human-readable phase documents |
| `reports/verification/` | machine evidence and logs |
| `reports/release/` | publishable release material |
| `reports/snapshots/` | environment identity snapshots |
| `reports/html_reports/` | documentation website/dashboard |

## 3. Restore the environment

Install Docker Desktop, WSL 2, Git, Python 3.11, Poetry if required, and the Dify Plugin CLI. Follow `reports/release/v1.0/Migration_Guide.md` for another machine.

On the baseline machine, never start services manually. Use:

```powershell
& 'E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1'
& 'E:\Dify_Plugin\db_query_extended\verification\dify_preflight.ps1'
```

The Compose project must be `dify`; do not start historical `docker-*` projects. Do not recreate volumes to solve an application-level problem.

## 4. Add a database adapter

1. Define the database identifier and credential fields without changing existing identifiers.
2. Implement a new adapter under `utils/adapters/` against the base contract.
3. Register it in the existing adapter selection path.
4. Keep read-only SQL validation shared; do not fork or weaken the policy.
5. Normalize vendor types to the established JSON result shape.
6. Map connection, timeout, syntax, and execution failures to controlled plugin errors.
7. Pin the smallest required driver set and confirm Linux `amd64` packaging.
8. Add Provider, Tool, and real Workflow cases before declaring support.

## 5. Test strategy

Use layers, from cheapest to most realistic:

1. Adapter/unit checks for connection construction, timeouts, and formatting.
2. Tool checks for validation, row limits, truncation, error mapping, and dangerous SQL.
3. Provider credential validation against the real target database.
4. Published Workflow tests for scalar, Unicode, timestamp, truncation, and rejection paths.
5. Workflow API calls with HTTP/status/output checks.
6. Full regression:

   ```powershell
   & 'E:\Dify_Plugin\db_query_extended\verification\verify_all.ps1' -OutputDir '<new evidence directory>'
   ```

Inject API keys only into the current process. A release candidate must retain 45/0/0 for the v1.0 databases plus all new adapter cases.

## 6. Package and release

Update the manifest version intentionally, pin dependencies, build the `.difypkg`, install it in the accepted Dify environment, validate the Provider, publish the Workflow, and rerun complete automation. Update release notes, compatibility, limitations, migration instructions, evidence index, and HTML dashboard. Follow `RELEASE_CHECKLIST.md`; do not commit or tag until human review.

## 7. Common problems

| Symptom | First check |
| --- | --- |
| `/install` appears | wrong PostgreSQL mount/project; stop before changing data |
| Plugin daemon restart loop | daemon logs, `dify_plugin`, storage permissions |
| Plugin missing after restart | Console database identity and plugin installation table |
| Provider validation fails | network route, driver, database type, credentials; never print password |
| Workflow variable missing | rebind the Tool input to the Start-node variable |
| Unicode corrupted | driver encoding and JSON formatter, then real Workflow API |
| Test count unexpectedly skipped | required environment variables and target database availability |

## 8. Engineering rules

- Treat `BASELINE.md` as the recovery contract.
- Never place API keys, passwords, tokens, database dumps, or live credential exports in Git.
- Preserve machine-readable evidence; summaries must match JSON totals.
- Fix only the failing layer and rerun regression.
- Archive superseded documentation; do not rewrite history or delete acceptance evidence.
