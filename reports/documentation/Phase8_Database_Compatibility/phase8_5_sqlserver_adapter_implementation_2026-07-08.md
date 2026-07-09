# Phase 8.5 - SQL Server minimal adapter implementation

Date: 2026-07-08  
Scope: minimal SQL Server adapter implementation plus independent smoke validation.

## 1. Goal

Add the smallest SQL Server adapter implementation that fits the current adapter architecture, then validate it independently without touching the main verification matrix.

## 2. Prior evidence

This implementation is based on already completed evidence:

- Phase 8.1 SQL Server runtime audit
- Phase 8.2 isolated probe
- Phase 8.3 dependency gate
- Phase 8.4 real connection probe

Those steps already proved:

- `sqlalchemy` import
- `pymssql` import
- `mssql+pymssql` dialect
- URL build
- real connection
- deterministic fixture read
- Unicode fixture read

## 3. Modified files

Implementation files:

- `db_query_extended/provider/db_query_extended.yaml`
- `db_query_extended/utils/validation.py`
- `db_query_extended/utils/adapters/sqlserver.py`
- `db_query_extended/requirements.txt`
- `db_query_extended/verification/sqlserver_adapter_smoke.py`

Verification artifact:

- `reports/verification/2026-07-08/sqlserver_adapter_smoke.json`

This round did not modify:

- `tools/db_query_extended.py`
- `utils/result_formatter.py`
- MySQL adapter
- PostgreSQL adapter
- DM8 adapter
- KingbaseES adapter
- `verify_all.ps1`
- `phase2_matrix.py`

## 4. SQL Server adapter design

Adapter file:

- `db_query_extended/utils/adapters/sqlserver.py`

Chosen driver path:

```text
mssql+pymssql
```

Implemented behavior:

- URL uses SQLAlchemy `URL.create(...)`
- host / port / database / username / password come from normalized config
- connect args use the current connection timeout as both:
  - `login_timeout`
  - `timeout`
- session configuration is a no-op

Why no-op is acceptable here:

- database is already selected by URL
- schema-qualified reads are used for the real SQL Server test path
- this keeps the first implementation small and avoids inventing session state we do not yet need

## 5. Provider / validation change

Provider change:

- added `sqlserver` to the `database_type` dropdown
- added display label `SQL Server`
- updated port help text to include `1433`

Validation change:

- added `sqlserver` to `SUPPORTED_DATABASE_TYPES`
- added SQL Server default port `1433`
- left the existing readonly SQL validation rules unchanged
- left existing schema/max_rows/timeout normalization behavior unchanged

## 6. Dependency change

`db_query_extended/requirements.txt` now includes:

```text
pymssql==2.3.13
```

Why this version:

- it was the probe-proven version in Phase 8.3 / 8.4
- import succeeded on Linux Python 3.12
- real connection probe succeeded with it

Important boundary:

- this does **not** mean offline packaging is already complete
- the repository wheel set still needs a dedicated packaging gate for `pymssql`

## 7. Smoke test command

Independent smoke command used:

```powershell
wsl -e bash -lc "PYTHONPATH=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe_site:/mnt/e/Dify_Plugin/db_query_extended python3 /mnt/e/Dify_Plugin/db_query_extended/verification/sqlserver_adapter_smoke.py --env-file /mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe.env --output /mnt/e/Dify_Plugin/reports/verification/2026-07-08/sqlserver_adapter_smoke.json"
```

## 8. Smoke test result

Artifact:

- `reports/verification/2026-07-08/sqlserver_adapter_smoke.json`

Actual result:

```text
PASS
```

Validated through the formal adapter path:

1. adapter import
2. URL build
3. engine creation
4. `SELECT 1 AS probe_value`
5. `SELECT TOP 5 * FROM [plugin_test].[plugin_test_users]`
6. Unicode fixture read
7. schema-qualified read

Representative returned values included:

- `张伟`
- `李娜`
- `测试用户🚀`

## 9. Main matrix status

Main verification matrix was **not** modified.

Unchanged:

- `verify_all.ps1`
- `phase2_matrix.py`
- main Workflow validation path

This implementation is still isolated from the main matrix.

## 10. Secret hygiene

Secret handling remained within the local deterministic test boundary:

- local env file was used for smoke execution
- env file was not committed
- password does not appear in the smoke artifact
- safe URL uses password redaction

## 11. Readiness after this round

After this round, SQL Server is ready for the next engineering gate.

What is ready:

- provider option
- validation entry
- adapter implementation
- independent smoke validation

What is still not closed:

- product offline packaging for `pymssql`
- any main-matrix or workflow integration

## 12. Next recommendation

Next step should be:

```text
SQL Server packaging gate
```

Reason:

- the adapter works
- the runtime dependency is declared
- but offline packaging evidence for `pymssql` is still the next real blocker before broader validation

## 13. Final verdict

Final verdict:

```text
GO - READY_FOR_SQLSERVER_PACKAGING_GATE
```
