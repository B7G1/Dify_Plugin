# Phase 8.7 - SQL Server Plugin-Daemon Runtime Gate

## 1. Phase 8.7 status

`PASS`

This round answered one narrow question only:

> Can the Phase 8.6 SQL Server candidate `.difypkg` pass the real Dify/plugin-daemon decode, install, dependency preparation, and runtime startup path?

Answer:

```text
Yes.
```

## 2. What exactly was tested

This round verified only the runtime gate:

```text
candidate .difypkg
-> real Dify upload/install API
-> plugin-daemon decode
-> dependency/runtime preparation
-> plugin install task
-> runtime startup
-> runtime ready
```

This round did **not** test:

- SQL Server Provider credential validation
- SQL Server Tool execution
- SQL Server `SELECT 1`
- Workflow/API regression
- main verification matrix integration

## 3. Candidate package identity

Candidate used:

- `E:\Dify_Plugin\release\db_query_extended\phase8_sqlserver_candidate\db_query_extended-0.1.1-sqlserver-candidate.difypkg`

Confirmed before install:

| Field | Value |
| --- | --- |
| exists | `true` |
| size | `36,891,110 bytes` |
| SHA-256 | `8a3c8e931da66e373831b8d1c5f3c77af1df33771fec0719f41be093db5e9e20` |
| bundled `requirements.txt` readable | `true` |
| bundled `pymssql==2.3.13` present | `true` |
| bundled wheel present | `pymssql-2.3.13-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` |

Upload response from the real Dify API returned this candidate identity:

```text
li_zijun/db_query_extended:0.1.1@4d1e293d9c5df7a8614e7d5e086a6a8a856a7a76accf835bc18ab6736f84af47
```

That is different from the previously installed 0.1.1 checksum:

```text
li_zijun/db_query_extended:0.1.1@81c92f7804b3b306c52e2f028b6fb1f0d9bd579236763c728f310dc90fa92dc7
```

So this was a real candidate runtime attempt, not a no-op read of the old package.

## 4. Existing Dify/plugin-daemon environment

Observed runtime inventory during this gate:

| Component | Value |
| --- | --- |
| git HEAD | `b627a87` |
| localhost | `200` |
| localhost/install | `200` |
| API | `dify-api-1`, `langgenius/dify-api:1.13.3`, running |
| plugin-daemon | `dify-plugin_daemon-1`, `langgenius/dify-plugin-daemon:0.5.3-local`, running |
| nginx | `dify-nginx-1`, `nginx:latest`, running |
| web | `dify-web-1`, `langgenius/dify-web:1.13.3`, running |

Pre-existing plugin state before the new install attempt:

- old installed plugin checksum was still the earlier 0.1.1 package
- plugin page already showed `db_query_extended 0.1.1`

Chosen path:

```text
upgrade/reinstall via real Dify local-package install path
```

Why:

- lower risk than uninstalling the existing plugin first
- directly tests whether the new candidate can be accepted by the real install chain

## 5. How the candidate was installed

This round did **not** mock plugin-daemon and did **not** fake runtime readiness.

Actual path used:

1. localhost admin session confirmed
2. real Dify Console/API upload endpoint used:
   - `/console/api/workspaces/current/plugin/upload/pkg`
3. real Dify install endpoint used:
   - `/console/api/workspaces/current/plugin/install/pkg`
4. real install task queried:
   - `/console/api/workspaces/current/plugin/tasks/<task_id>`

Install task id:

```text
019f45ab-3e56-79b9-84a2-271e9c3b2a3a
```

## 6. What plugin-daemon actually did

Observed real runtime sequence from plugin-daemon logs:

1. package upload accepted
2. decode from candidate identifier succeeded
3. install task created
4. local runtime started for the candidate checksum
5. dependency file `requirements.txt` detected
6. dependency install started via `uv pip install`
7. plugin pre-compiled
8. local runtime scaled up
9. tool installed
10. local runtime marked ready
11. install task finished successfully

This is exactly the layer Phase 8.7 was supposed to test.

## 7. Decode result

`PASS`

Evidence:

```text
GET /management/decode/from_identifier?... status=200
```

## 8. Dependency/runtime preparation result

`PASS`

Evidence:

```text
detected dependency file=requirements.txt
installing plugin dependencies method="uv pip install"
```

This proves the real plugin-daemon runtime consumed the packaged dependency set instead of only trusting the earlier offline packaging gate.

## 9. `pymssql` runtime evidence

`PASS`

Observed runtime evidence:

```text
Listing './.venv/lib/python3.12/site-packages/pymssql-2.3.13.dist-info/licenses'...
```

This is not full SQL Server query proof. It is the required Phase 8.7 proof that the packaged `pymssql` dependency made it into the real plugin-daemon runtime environment without wheel-compatibility or import-layer failure.

## 10. Plugin install result

`PASS`

Install task result:

| Field | Value |
| --- | --- |
| task id | `019f45ab-3e56-79b9-84a2-271e9c3b2a3a` |
| task status | `success` |
| plugin status | `success` |
| plugin message | `installed` |

## 11. Runtime startup result

`PASS`

Evidence:

```text
local runtime starting plugin=li_zijun/db_query_extended:0.1.1@4d1e293d...
local runtime scale up ... instance_nums=1
```

## 12. Runtime ready evidence

`PASS`

Evidence:

```text
Installed tool: db_query_extended
local runtime ready plugin=li_zijun/db_query_extended:0.1.1@4d1e293d...
```

No immediate crash loop was observed for the candidate.

## 13. Errors or warnings observed

Hard failure:

```text
none
```

Warnings:

1. The install task and plugin-daemon runtime clearly moved to the new candidate checksum.
2. However, the Console/API plugin list and PostgreSQL `plugins` / `plugin_installations` tables still showed the older 0.1.1 checksum during this observation window.

Interpretation:

- this did **not** block upload
- did **not** block decode
- did **not** block dependency preparation
- did **not** block runtime startup
- did **not** block runtime ready

So it is a post-install read-model or list-synchronization warning, not a runtime-gate blocker.

## 14. Secret hygiene result

`PASS`

Applied boundary:

- no SQL Server password recorded
- no Dify API key recorded
- no browser cookies copied into artifact/report
- no authorization headers copied into artifact/report

## 15. Files changed

This round only produced:

- `reports/verification/2026-07-09/sqlserver_plugin_runtime_gate.json`
- `reports/documentation/Phase8_Database_Compatibility/phase8_7_sqlserver_plugin_runtime_gate_2026-07-09.md`

No Provider/Tool/Adapter/Workflow code was changed in this phase.

## 16. Commit result

Commit created:

```text
test: verify sqlserver plugin runtime gate
```

## 17. Final verdict

Final verdict:

```text
PASS
GO - READY_FOR_SQLSERVER_TOOL_VALIDATION
```

Why this is PASS:

1. candidate identity confirmed
2. candidate submitted through real Dify install path
3. plugin-daemon received package
4. decode succeeded
5. dependency preparation succeeded
6. install task succeeded
7. runtime started
8. runtime reached ready state
9. no immediate crash/restart loop from candidate
10. candidate runtime identity was observable from task/log/runtime side

## 18. Next exact task

Next step should be:

```text
Phase 8.8 - SQL Server Tool validation
```

That next phase should start with:

- SQL Server Provider credential validation
- `SELECT 1`
- `SELECT TOP 5`
- Unicode
- schema-qualified query

But not before this Phase 8.7 runtime gate is recorded as passed.
