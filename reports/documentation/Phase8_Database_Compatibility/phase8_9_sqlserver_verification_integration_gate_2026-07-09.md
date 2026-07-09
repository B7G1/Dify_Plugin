# Phase 8.9 - SQL Server Verification Integration Gate

Status: PASS - SQLSERVER_OPTIONAL_GATE_READY

## Goal

Turn the Phase 8.8 SQL Server tool validation into a repeatable independent gate, then decide whether it is ready for the main verification matrix.

## Phase 8.8 Baseline

Phase 8.8 already proved the real Dify/plugin-daemon path:

- Provider credential validation: PASS
- `SELECT 1`: PASS
- `SELECT TOP 5`: PASS
- Unicode fixture read: PASS
- schema-qualified read: PASS
- output shape `columns / rows / row_count / truncated / max_rows`: PASS
- observed `database_type = sqlserver`

Reference evidence:

- `reports/verification/2026-07-09/sqlserver_tool_validation_gate.json`
- `reports/documentation/Phase8_Database_Compatibility/phase8_8_sqlserver_tool_validation_gate_2026-07-09.md`

## New Optional Gate

Entry:

```powershell
python E:\Dify_Plugin\db_query_extended\verification\sqlserver_tool_validation_gate.py `
  --env-file E:\Dify_Plugin\db_query_extended\verification\.sqlserver_probe.env `
  --output E:\Dify_Plugin\reports\verification\2026-07-09\sqlserver_tool_validation_gate_rerun.json
```

The runner:

- reads SQL Server connection values from env or local env file
- does not enter `verify_all.ps1`
- does not import or modify product code on the host
- executes inside `dify-api-1` against the real Dify application runtime
- invokes plugin-daemon through Dify `PluginToolManager` and `ToolManager`
- writes a sanitized JSON artifact

## Rerun Result

Artifact:

- `reports/verification/2026-07-09/sqlserver_tool_validation_gate_rerun.json`

Result: PASS

Rerun checks:

| Check | Result |
| --- | --- |
| SQL Server provider credential found | PASS |
| Runtime provider credential validation | PASS |
| `SELECT 1 AS probe_value` | PASS |
| `SELECT TOP 5 ...` | PASS |
| Unicode fixture read | PASS |
| schema-qualified read | PASS |
| required output keys | PASS |
| `database_type = sqlserver` | PASS |
| password/token leakage | PASS |

Representative rerun facts:

- `SELECT 1` returned `probe_value = 1`
- `SELECT TOP 5` returned 5 fixture rows
- Unicode read returned Chinese text and emoji
- schema-qualified log count returned `3`

## Main Matrix Assessment

SQL Server is repeatable as an optional local gate today.

It is not ready for default `verify_all.ps1` inclusion yet.

Reasons:

- depends on Dify/plugin-daemon being already running
- depends on the SQL Server candidate plugin being installed in local Dify
- depends on local SQL Server Docker fixture availability
- depends on a local env file or equivalent environment variables
- uses Dify runtime internals from the API container, not the existing host-only provider/tool matrix shape

This is the right shape for a release gate or optional database gate, not a default main matrix gate.

## Recommended Integration Model

Recommended now:

- keep `sqlserver_tool_validation_gate.py` as an optional gate
- run it after packaging and plugin-daemon runtime gates
- keep `verify_all.ps1` stable for v1.0 MySQL/PostgreSQL/DM regression

Recommended later:

- add a separate SQL Server verification wrapper
- add explicit skip/block reporting when SQL Server Docker or installed candidate is absent
- only then consider main matrix integration

## Secret Hygiene

The runner and artifact do not persist:

- SQL Server password
- Dify auth token
- browser/session cookies
- full plugin checksum

The artifact records only sanitized local test connection metadata and real query outputs.

## Verdict

PASS - SQLSERVER_OPTIONAL_GATE_READY

SQL Server validation is now repeatable as an independent optional gate.

## Next Step

Proceed to SQL Server optional gate documentation / release checklist before considering main matrix integration.
