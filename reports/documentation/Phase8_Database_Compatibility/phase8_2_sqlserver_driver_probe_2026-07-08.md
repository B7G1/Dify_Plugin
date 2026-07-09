# Phase 8.2 - SQL Server isolated driver probe

Date: 2026-07-08  
Scope: isolated probe only. No product adapter implementation.

## 1. Goal

Add one isolated SQL Server probe to answer the runtime question left open by Phase 8.1:

- can this environment import the chosen driver path;
- can SQLAlchemy build the `mssql+pymssql` URL/dialect path;
- if connection variables exist, can the probe attempt a real database connection without touching product code.

## 2. Probe script path

- `db_query_extended/verification/sqlserver_driver_probe.py`

The script is intentionally not imported by product code and is not connected to the main verification matrix.

## 3. Checks performed

The probe checks:

1. Python version and executable;
2. platform information;
3. `sqlalchemy` import;
4. `pymssql` import;
5. SQLAlchemy URL object build for `mssql+pymssql`;
6. dialect load;
7. safe URL rendering without password exposure;
8. missing environment detection;
9. optional connection probe only when all connection variables are present.

## 4. Run commands

Scenario A - no credentials / missing environment:

```powershell
py -3 E:\Dify_Plugin\db_query_extended\verification\sqlserver_driver_probe.py `
  --output E:\Dify_Plugin\reports\verification\2026-07-08\sqlserver_driver_probe_no_env.json
```

Scenario B - real connection probe, only if all environment variables are present:

```powershell
py -3 E:\Dify_Plugin\db_query_extended\verification\sqlserver_driver_probe.py `
  --output E:\Dify_Plugin\reports\verification\2026-07-08\sqlserver_driver_probe_with_env.json
```

## 5. Scenario A result

Actual result in this environment:

- `sqlalchemy` import: not available in the Python used for the probe
- `pymssql` import: not available in the Python used for the probe
- connection environment variables: not present

Because driver/runtime imports already fail, Scenario A does not reach the URL/dialect/connection stage.

Expected artifact:

- `reports/verification/2026-07-08/sqlserver_driver_probe_no_env.json`

Observed status:

```text
FAIL_IMPORT
```

Observed reason:

```text
MISSING_DRIVER_DEPENDENCY
```

Observed missing imports:

- `sqlalchemy`
- `pymssql`

## 6. Scenario B result

Scenario B was not executed to PASS/FAIL completion in this round.

Reason:

- no `SQLSERVER_*` connection environment variables were present in the current process;
- the probe runtime also lacks the required Python dependencies.

Therefore there is no truthful connection result to report.

## 7. Driver import result

Current result:

- `sqlalchemy`: missing in probe Python
- `pymssql`: missing in probe Python

Artifact confirms:

- probe interpreter: `E:\python.exe`
- Python version: `3.11.0`

This does not yet prove runtime incompatibility of the final plugin package. It proves only that the currently used isolated probe Python environment does not contain the required dependencies.

## 8. SQLAlchemy dialect result

Current result:

- not reached

Reason:

- SQLAlchemy import failed before dialect loading could be attempted.

## 9. Wheel / dependency conclusion

Current repository evidence remains:

- no SQL Server dependency entry in product `requirements.txt`
- no SQL Server wheel evidence under current plugin wheels
- no probe-time Python dependency available for `sqlalchemy` or `pymssql` in the interpreter used this round

So the current practical blocker is still dependency availability, not adapter code.

## 10. Secret hygiene

The probe:

- reads only environment variables;
- does not print `SQLSERVER_PASSWORD`;
- does not print a full raw connection string;
- uses safe URL rendering only;
- reports missing variable names, not values.

No real secret was written into the script or this report.

## 11. Adapter implementation readiness

Current answer:

```text
not yet
```

The repository should not begin SQL Server adapter implementation until the isolated runtime probe can at least import the chosen dependency path truthfully.

## 12. Next recommendation

Next step should be to provide the SQL Server probe dependency path first:

1. make `sqlalchemy` and `pymssql` available to the isolated probe environment;
2. rerun Scenario A;
3. if imports pass, rerun with connection environment variables present;
4. only then decide whether adapter implementation can begin.

## 13. Final verdict

Final verdict:

```text
BLOCKED - SQLSERVER_DRIVER_MISSING
```
