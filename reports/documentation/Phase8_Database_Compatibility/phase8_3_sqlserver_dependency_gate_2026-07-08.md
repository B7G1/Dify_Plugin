# Phase 8.3 - SQL Server dependency/wheel gate

Date: 2026-07-08  
Scope: probe-only dependency gate. No product adapter implementation.

## 1. Goal

Move the SQL Server isolated probe from:

```text
FAIL_IMPORT
```

to at least:

```text
BLOCKED - MISSING_ENV
```

which proves import, dialect, and URL build readiness for the chosen probe path.

## 2. Prior state

Phase 8.1 conclusion:

- `CONDITIONAL_GO - NEED_ISOLATED_DRIVER_PROBE`

Phase 8.2 conclusion:

- `BLOCKED - SQLSERVER_DRIVER_MISSING`

Observed failures before this gate:

- `sqlalchemy` import failed
- `pymssql` import failed

## 3. Probe-only dependency file

File:

- `db_query_extended/verification/sqlserver_probe_requirements.txt`

Content:

```text
SQLAlchemy==2.0.51
pymssql
```

Rationale:

- `SQLAlchemy==2.0.51` matches the frozen plugin baseline already in the repository;
- `pymssql` remains probe-only here and is not yet promoted to product runtime dependency.

## 4. Installation environment

Chosen environment:

- WSL Linux Python, not the broken Windows probe path

Reason:

- the repository already carries Linux cp312 wheels for current product runtime dependencies;
- the earlier Windows 3.11 probe path could not consume the repository's Linux cp312 wheel set;
- WSL Python 3.12 is much closer to the eventual plugin runtime shape.

Observed environment:

| Field | Value |
| --- | --- |
| Python | `3.12.3` |
| Executable | `/usr/bin/python3` |
| Platform | `Linux x86_64` |
| pip | `24.0` |
| Isolated install location | `db_query_extended/verification/.sqlserver_probe_site` |

## 5. Installation commands

SQLAlchemy from repository wheels:

```powershell
wsl -e bash -lc "cd /mnt/e/Dify_Plugin && python3 -m pip install --no-index --find-links=/mnt/e/Dify_Plugin/db_query_extended/wheels --target=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe_site SQLAlchemy==2.0.51"
```

`pymssql` for probe-only validation:

```powershell
wsl -e bash -lc "cd /mnt/e/Dify_Plugin && python3 -m pip install --target=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe_site pymssql"
```

Probe rerun:

```powershell
wsl -e bash -lc "PYTHONPATH=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe_site python3 /mnt/e/Dify_Plugin/db_query_extended/verification/sqlserver_driver_probe.py --output /mnt/e/Dify_Plugin/reports/verification/2026-07-08/sqlserver_driver_probe_dependency_gate.json"
```

## 6. Installation result

SQLAlchemy:

- installed successfully from repository wheel
- version: `2.0.51`

`pymssql`:

- installed successfully
- version: `2.3.13`

No source build failure occurred in this probe gate.

## 7. Wheel / source build conclusion

Observed evidence:

- `SQLAlchemy` came from the repository's Linux cp312 wheel
- `pymssql` came from a binary manylinux wheel:
  - `pymssql-2.3.13-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`

Observed build mode:

```text
binary wheel install, not source compile
```

This is good probe evidence because:

- import works on Linux Python 3.12
- no compile toolchain was needed during this step

But this is still not enough to declare product runtime acceptance:

- the wheel is not yet vendored into `db_query_extended/wheels/`
- product `requirements.txt` is intentionally unchanged
- plugin offline packaging has not yet been updated or revalidated

## 8. Scenario A result

Artifact:

- `reports/verification/2026-07-08/sqlserver_driver_probe_dependency_gate.json`

Actual result:

```text
status = BLOCKED
reason = MISSING_ENV
```

Passed checks:

- `sqlalchemy` import = PASS
- `pymssql` import = PASS
- SQLAlchemy URL build = PASS
- dialect load = PASS
- dialect name = `mssql`
- driver = `pymssql`
- safe URL rendering = PASS

This is the key success condition for Phase 8.3.

## 9. Scenario B result

Scenario B was not run in this round.

Reason:

- `SQLSERVER_HOST`
- `SQLSERVER_PORT`
- `SQLSERVER_DATABASE`
- `SQLSERVER_USERNAME`
- `SQLSERVER_PASSWORD`

were not present in the current process used for the probe.

So there is no truthful SQL Server connection result to report yet.

## 10. Secret hygiene

This round preserved secret hygiene:

- no password was written into the script
- no password was written into the report
- no raw connection string was printed
- only missing environment variable names were reported
- the JSON artifact uses safe URL rendering

## 11. Promotion to product dependency?

Current answer:

```text
not yet
```

Reason:

- probe dependency success is not the same thing as product runtime acceptance
- the wheel is not yet vendored into repository offline packaging
- no product packaging readback or plugin runtime validation has been done
- no real connection probe has been completed yet

So `pymssql` should remain probe-only at this stage.

## 12. Final verdict

Final verdict:

```text
GO - READY_FOR_SQLSERVER_CONNECTION_PROBE
```

Interpretation:

- dependency gate is no longer the blocker
- the next blocker is missing connection environment for the real connection probe
- adapter implementation should still wait until the connection probe is done

## 13. Next recommendation

Next step:

1. provide `SQLSERVER_*` environment variables in the probe process
2. rerun the same isolated probe
3. capture real connection output in a second artifact
4. only then decide whether SQL Server adapter implementation should start
