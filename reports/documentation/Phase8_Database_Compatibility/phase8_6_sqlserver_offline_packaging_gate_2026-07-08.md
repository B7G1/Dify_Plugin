# Phase 8.6 - SQL Server offline packaging gate

Date: 2026-07-08  
Execution completed: 2026-07-09  
Scope: offline dependency closure, offline import gate, offline adapter re-check, and candidate package build. No Tool validation, no main matrix integration, no plugin-daemon install claim.

## 1. Goal

Prove that `pymssql==2.3.13` can enter the plugin's formal offline dependency chain for the target runtime:

- Python `3.12`
- Linux `amd64 / x86_64`

Required proof boundary for this round:

1. compatible binary wheel exists;
2. the wheel is usable from formal `db_query_extended/wheels/`;
3. full formal `requirements.txt` can be installed with `--no-index`;
4. offline-only runtime can import `sqlalchemy`, `pymssql`, and the formal SQL Server adapter;
5. offline-only runtime can re-run the formal SQL Server adapter smoke test;
6. a new candidate `.difypkg` can be built from the current formal source tree.

This round does **not** claim:

- Dify plugin-daemon install PASS;
- SQL Server Tool validation PASS;
- main verification matrix integration PASS.

## 2. Prior state

Prior Phase 8 conclusion:

```text
GO - READY_FOR_SQLSERVER_PACKAGING_GATE
```

Closed prerequisites already existed:

- isolated driver probe PASS;
- `pymssql==2.3.13` import PASS;
- `mssql+pymssql` dialect PASS;
- SQL Server local connection probe PASS;
- minimal SQL Server adapter PASS;
- formal adapter smoke PASS.

## 3. Current offline dependency architecture

Formal runtime dependency entrypoint:

- `db_query_extended/requirements.txt`

Formal wheel directory:

- `db_query_extended/wheels/`

Formal dependency policy already present in `requirements.txt`:

```text
--no-index
--find-links=./wheels
```

This means the intended runtime contract is already:

```text
offline pip install from repository wheels only
```

Phase 8.6 therefore focused on proving that the SQL Server addition does not break that formal contract.

## 4. Target runtime

| Field | Value |
| --- | --- |
| Python target | `3.12` |
| Runtime OS | `Linux` |
| Runtime architecture | `amd64 / x86_64` |
| Probe/install host | `WSL2 Linux x86_64` |
| Probe Python | `3.12.3` |
| Probe pip | `24.0` |

## 5. `pymssql` wheel filename

Formal wheel added to the runtime wheel directory:

```text
db_query_extended/wheels/pymssql-2.3.13-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
```

## 6. Wheel compatibility

Compatibility checks:

- package version = `2.3.13`
- Python tag = `cp312`
- ABI tag = `cp312`
- platform tags:
  - `manylinux_2_27_x86_64`
  - `manylinux_2_28_x86_64`

Conclusion:

```text
compatible with Python 3.12 Linux x86_64 runtime
```

No Windows wheel was used as SQL Server release evidence.

## 7. Wheel SHA-256

| Field | Value |
| --- | --- |
| filename | `pymssql-2.3.13-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` |
| size | `3,190,567 bytes` |
| SHA-256 | `c0ea72641cb0f8bce7ad8565dbdbda4a7437aa58bce045f2a3a788d71af2e4be` |

## 8. Wheel metadata

Extracted wheel metadata:

| Field | Value |
| --- | --- |
| Name | `pymssql` |
| Version | `2.3.13` |
| Summary | `DB-API interface to Microsoft SQL Server for Python. (new Cython-based version)` |

Wheel tag lines:

```text
Tag: cp312-cp312-manylinux_2_27_x86_64
Tag: cp312-cp312-manylinux_2_28_x86_64
```

This is a binary wheel, not an sdist.

## 9. Full requirements offline install command

Fresh local-only target directory:

```text
db_query_extended/verification/.sqlserver_offline_package_site/
```

Exact install command used:

```powershell
wsl -e bash -lc "cd /mnt/e/Dify_Plugin/db_query_extended && python3 -m pip install --no-index --find-links=/mnt/e/Dify_Plugin/db_query_extended/wheels --target=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_offline_package_site -r /mnt/e/Dify_Plugin/db_query_extended/requirements.txt"
```

Constraints preserved:

- `--no-index` used;
- `--find-links` points only to repository `wheels/`;
- install target is a fresh local-only directory;
- no fallback to product `.venv`;
- no fallback to Phase 8.3 probe site.

## 10. Offline install result

Result:

```text
PASS
exit code = 0
```

Observed pip behavior:

- `Looking in links` only referenced repository wheel paths;
- `pymssql-2.3.13` was installed from repository `wheels/`;
- install completed successfully for the full formal `requirements.txt`, not only for `pymssql`.

## 11. Installed dependency versions

Representative installed direct dependencies:

| Package | Version |
| --- | --- |
| `dify_plugin` | `0.6.2` |
| `SQLAlchemy` | `2.0.51` |
| `PyMySQL` | `1.2.0` |
| `psycopg2-binary` | `2.9.12` |
| `pymssql` | `2.3.13` |
| `dmPython` | `2.5.32` |
| `dmSQLAlchemy` | `2.0.12` |

Offline install also completed all transitive dependencies required by `dify_plugin`.

## 12. Offline runtime import result

Artifact:

- `reports/verification/2026-07-08/sqlserver_offline_packaging_gate.json`

Result:

```text
PASS
```

Validated from the offline-only install site:

1. `sqlalchemy` import;
2. `pymssql` import;
3. `pymssql.__version__ == 2.3.13`;
4. `sqlalchemy.engine.URL` build;
5. `mssql+pymssql` dialect load;
6. safe URL rendering without password exposure.

## 13. SQL Server adapter import result

The same artifact also proves formal adapter import:

- `utils.adapters.sqlserver.Adapter` import = PASS
- adapter URL build = PASS
- `drivername = mssql+pymssql`
- dialect name = `mssql`
- connect args = `{"login_timeout": 5, "timeout": 5}`

## 14. Offline adapter smoke result

Artifact:

- `reports/verification/2026-07-08/sqlserver_offline_adapter_smoke.json`

Runtime path:

```powershell
wsl -e bash -lc "PYTHONPATH=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_offline_package_site:/mnt/e/Dify_Plugin/db_query_extended python3 -S /mnt/e/Dify_Plugin/db_query_extended/verification/sqlserver_adapter_smoke.py --env-file /mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe.env --output /mnt/e/Dify_Plugin/reports/verification/2026-07-08/sqlserver_offline_adapter_smoke.json"
```

Result:

```text
PASS
```

This is not a repeat of the online dependency probe. It proves the full chain:

```text
offline packaged dependency environment
-> formal SQL Server adapter
-> real SQL Server local test environment
```

Verified checks:

- adapter import;
- URL build;
- engine creation;
- `SELECT 1 AS probe_value`;
- `SELECT TOP 5 * FROM [plugin_test].[plugin_test_users]`;
- Unicode fixture read;
- schema-qualified read.

Representative returned values included:

- `Alice`
- `张伟`
- `李娜`
- `测试用户🚀`
- `只读账号测试`

## 15. Package build result

Candidate package output:

```text
release/db_query_extended/phase8_sqlserver_candidate/db_query_extended-0.1.1-sqlserver-candidate.difypkg
```

Build result:

```text
PASS
```

Command used:

```powershell
E:\Dify_Plugin\dify-plugin-windows-amd64.exe plugin package E:\Dify_Plugin\db_query_extended -o E:\Dify_Plugin\release\db_query_extended\phase8_sqlserver_candidate\db_query_extended-0.1.1-sqlserver-candidate.difypkg
```

Important packaging note:

- initial package attempt failed because the wheel directory still contained an incompatible local-only DM wheel:
  - `dmpython-2.5.32-cp311-cp311-win_amd64.whl`
- that file does not belong to the target runtime (`Python 3.12 / Linux amd64`);
- removing that incompatible local wheel allowed the package to build successfully;
- this was packaging hygiene cleanup, not a database-logic change.

## 16. Package content inspection

Candidate package inspection confirmed:

- `requirements.txt` contains `pymssql==2.3.13`
- package contains:

```text
wheels/pymssql-2.3.13-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
```

Observed candidate wheel count:

```text
43
```

## 17. Candidate package SHA-256

| Field | Value |
| --- | --- |
| filename | `db_query_extended-0.1.1-sqlserver-candidate.difypkg` |
| size | `36,891,110 bytes` |
| SHA-256 | `8a3c8e931da66e373831b8d1c5f3c77af1df33771fec0719f41be093db5e9e20` |

## 18. Secret hygiene

This round preserved the requested credential boundary.

Applied rules:

- deterministic local test credentials were allowed for local execution;
- no SQL Server password was written into the report body;
- no SQL Server password was written into JSON artifacts;
- safe URLs use password redaction;
- local env file remained local-only:
  - `db_query_extended/verification/.sqlserver_probe.env`
- offline install target remained local-only:
  - `db_query_extended/verification/.sqlserver_offline_package_site/`

## 19. Boundary: package PASS vs plugin-daemon runtime PASS

These are **not** the same claim.

Current truth after Phase 8.6:

| Gate | Status |
| --- | --- |
| `pymssql` compatible wheel closure | `PASS` |
| full `requirements.txt` offline pip install | `PASS` |
| offline runtime import | `PASS` |
| offline dependency environment -> formal adapter -> real SQL Server smoke | `PASS` |
| candidate package build | `PASS` |
| Dify plugin-daemon install of candidate package | `NOT YET VERIFIED` |
| SQL Server Tool validation | `NOT YET VERIFIED` |

Therefore this round closes packaging readiness, but does **not** skip the plugin runtime gate.

## 20. Next recommendation

Final verdict:

```text
GO - READY_FOR_SQLSERVER_PLUGIN_RUNTIME_GATE
```

Why this is the correct next gate:

- offline wheel closure is complete;
- full formal requirements install is complete;
- offline runtime import is complete;
- formal adapter still works in the offline dependency environment;
- package build is complete;
- but the candidate package has not yet been installed and run inside the real Dify plugin-daemon.

That plugin-daemon runtime gate should be the next exact task.
