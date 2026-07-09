# SQL Server Optional Gate Status - 2026-07-09

Final conclusion:

```text
SQLSERVER_OPTIONAL_GATE_READY_NOT_MAIN_MATRIX
```

## Current Conclusion

SQL Server support has passed the optional release gate path through packaging, plugin-daemon runtime startup, real provider credential validation, and real tool execution.

It is not part of the default main verification matrix yet.

## What Has Passed

| Layer | Status | Evidence |
| --- | --- | --- |
| Driver dependency gate | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_3_sqlserver_dependency_gate_2026-07-08.md` |
| Local SQL Server connection probe | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_4_sqlserver_connection_probe_2026-07-08.md` |
| Minimal adapter implementation | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_5_sqlserver_adapter_implementation_2026-07-08.md` |
| Offline packaging gate | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_6_sqlserver_offline_packaging_gate_2026-07-08.md` |
| Plugin-daemon runtime gate | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_7_sqlserver_plugin_runtime_gate_2026-07-09.md` |
| Real Dify/plugin-daemon tool validation | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_8_sqlserver_tool_validation_gate_2026-07-09.md` |
| Repeatable optional validation gate | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_9_sqlserver_verification_integration_gate_2026-07-09.md` |
| Release checklist | PASS | `reports/documentation/Phase8_Database_Compatibility/phase8_10_sqlserver_optional_gate_release_checklist_2026-07-09.md` |

## Package, Runtime, And Tool Status

These are separate claims:

| Area | Status | Meaning |
| --- | --- | --- |
| Offline package dependency closure | PASS | `pymssql==2.3.13` works in the target Python 3.12 Linux x86_64 offline dependency set. |
| Candidate `.difypkg` build | PASS | The candidate package was built from the formal source tree and bundled SQL Server dependencies. |
| Plugin-daemon runtime | PASS | Real Dify/plugin-daemon accepted the candidate package and started the runtime. |
| Provider credential validation | PASS | SQL Server credentials validated through real Dify/plugin-daemon runtime. |
| Tool execution | PASS | SQL Server queries executed through the real tool path. |
| Main matrix integration | NOT INCLUDED | SQL Server is optional and is not run by default in `verify_all.ps1`. |

## Evidence Index

Machine artifacts:

- `reports/verification/2026-07-08/sqlserver_driver_probe_no_env.json`
- `reports/verification/2026-07-08/sqlserver_driver_probe_dependency_gate.json`
- `reports/verification/2026-07-08/sqlserver_driver_probe_connection.json`
- `reports/verification/2026-07-08/sqlserver_adapter_smoke.json`
- `reports/verification/2026-07-08/sqlserver_offline_packaging_gate.json`
- `reports/verification/2026-07-08/sqlserver_offline_adapter_smoke.json`
- `reports/verification/2026-07-09/sqlserver_plugin_runtime_gate.json`
- `reports/verification/2026-07-09/sqlserver_tool_validation_gate.json`
- `reports/verification/2026-07-09/sqlserver_tool_validation_gate_rerun.json`

Human reports:

- `reports/documentation/Phase8_Database_Compatibility/phase8_6_sqlserver_offline_packaging_gate_2026-07-08.md`
- `reports/documentation/Phase8_Database_Compatibility/phase8_7_sqlserver_plugin_runtime_gate_2026-07-09.md`
- `reports/documentation/Phase8_Database_Compatibility/phase8_8_sqlserver_tool_validation_gate_2026-07-09.md`
- `reports/documentation/Phase8_Database_Compatibility/phase8_9_sqlserver_verification_integration_gate_2026-07-09.md`
- `reports/documentation/Phase8_Database_Compatibility/phase8_10_sqlserver_optional_gate_release_checklist_2026-07-09.md`

## Optional Gate Run Command

```powershell
python E:\Dify_Plugin\db_query_extended\verification\sqlserver_tool_validation_gate.py `
  --env-file E:\Dify_Plugin\db_query_extended\verification\.sqlserver_probe.env `
  --output E:\Dify_Plugin\reports\verification\2026-07-09\sqlserver_tool_validation_gate_rerun.json
```

Expected result:

```text
verdict = PASS
```

## Why It Is Not In The Main Matrix

SQL Server remains outside `verify_all.ps1` because the gate depends on local integration state:

- local SQL Server Docker fixture must be running
- local Dify and plugin-daemon must be running
- candidate plugin must already be installed in Dify
- local env file or equivalent env vars must be available
- missing-environment failures must be separated from product regressions before this can become a default baseline gate

This preserves the existing MySQL/PostgreSQL/DM baseline and avoids turning optional local infrastructure into a default failure source.

## Secret Hygiene

The optional gate and status page must not record:

- SQL Server password
- Dify access token
- Dify refresh token
- CSRF token
- browser cookies
- full plugin checksum

Allowed evidence:

- credential display name
- local fixture database and schema names
- local fixture username
- redacted plugin identifier, for example `li_zijun/db_query_extended:0.1.1@<redacted>`
- real query outputs without secrets

## Known Limits

- SQL Server is validated as an optional local gate, not as part of default CI or `verify_all.ps1`.
- Workflow API coverage for SQL Server is not claimed here.
- Reproducibility still depends on local operator setup for SQL Server fixture, Dify, plugin-daemon, and candidate installation.
- The optional gate assumes the Dify provider credential named `SQL Server Local Readonly` exists.

## Conditions For Main Matrix Entry

SQL Server can be reconsidered for main matrix integration only when:

- plugin package install and candidate update flow are repeatable
- SQL Server local fixture setup is one-command reproducible
- env file or secret injection is standardized
- optional gate can return BLOCKED for missing environment and FAIL for product regression
- default MySQL/PostgreSQL/DM verification remains unaffected
- maintainers explicitly decide SQL Server should be included in the baseline run

## Recommended Next Stage

Two reasonable next paths exist:

1. Evaluate SQL Server main matrix integration design, still without enabling it by default.
2. Move to the next database compatibility target while keeping SQL Server as an optional release gate.

Current recommendation:

```text
Keep SQL Server optional until environment reproducibility and failure classification are fully standardized.
```
