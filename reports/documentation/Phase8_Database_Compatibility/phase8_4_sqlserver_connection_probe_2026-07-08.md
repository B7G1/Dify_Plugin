# Phase 8.4 - SQL Server connection probe with local env file

Date: 2026-07-08  
Scope: isolated connection probe only. No product adapter implementation.

## 1. Goal

Use the existing SQL Server local test environment and deterministic local test credentials to prove the isolated SQL Server probe can perform a real connection and read deterministic fixture data.

## 2. Reused environment assets

This round reused the existing SQL Server local test assets instead of designing a new fixture path:

- `local_test_db/sqlserver/docker-compose.yml`
- `local_test_db/sqlserver/.env.example`
- `local_test_db/sqlserver/prepare.ps1`
- `local_test_db/sqlserver/init/01_admin_setup.sql`
- `local_test_db/sqlserver/init/02_schema_data.sql`
- `local_test_db/sqlserver/verification/verify.ps1`
- `local_test_db/sqlserver/verification/verify.sql`

Confirmed connection facts from those assets:

| Field | Value |
| --- | --- |
| host | `127.0.0.1` |
| exposed port | `1433` |
| database | `plugin_test` |
| readonly username | `plugin_readonly` |
| schema | `plugin_test` |

Readonly password was taken from the deterministic local test credential already used by the SQL Server environment gate, but is not repeated in this report body.

## 3. Local env file

Local file created:

- `db_query_extended/verification/.sqlserver_probe.env`

Purpose:

- provide the isolated probe with SQL Server connection values
- keep probe invocation simple
- avoid hardcoding connection data inside the probe script

This file is local-only and should not be committed.

## 4. Probe script update

`db_query_extended/verification/sqlserver_driver_probe.py` was updated to support:

- `--env-file`

Implementation is intentionally small:

- plain `KEY=VALUE` loading
- no product imports
- no main verification-matrix integration
- no secret echo

The probe was also corrected to serialize SQLAlchemy row mappings into normal JSON objects for connection output.

## 5. Environment readiness

The SQL Server local environment was checked and prepared using the existing `prepare.ps1` flow with the authorized deterministic local test credentials.

Observed result:

- container `dify-plugin-test-sqlserver`: `healthy`
- administrator initialization: PASS
- deterministic fixture initialization: PASS
- readonly verification: PASS
- final marker: `PHASE11_SQLSERVER_VERIFY_PASS`

This reconfirmed:

- `SELECT 1`
- `TOP 5`
- `COUNT`
- Unicode fixture read
- JOIN / aggregation
- readonly permission enforcement

## 6. Probe runtime path used

The successful probe path remained the Phase 8.3 isolated Linux path:

- WSL Python `3.12.3`
- `PYTHONPATH=/mnt/e/Dify_Plugin/db_query_extended/verification/.sqlserver_probe_site`

This reused the already-proven probe dependency gate rather than changing product dependencies.

## 7. Connection artifact

Artifact:

- `reports/verification/2026-07-08/sqlserver_driver_probe_connection.json`

Actual result:

```text
status = PASS
reason = CONNECTION_PROBE_OK
```

## 8. Verified checks

The real connection probe passed:

- SQLAlchemy import
- `pymssql` import
- `mssql+pymssql` drivername
- dialect name `mssql`
- safe URL rendering
- `SELECT 1 AS probe_value`
- `SELECT TOP 5` from schema-qualified fixture table
- Unicode fixture read in returned rows
- schema-qualified table access via `[plugin_test].[plugin_test_users]`

Representative read result included:

- `张伟`
- `李娜`
- `测试用户🚀`

So this round proved not only connectivity, but real deterministic fixture retrieval including Unicode content.

## 9. Secret hygiene

This round treated the authorized SQL Server values as deterministic local test credentials.

Applied boundaries:

- credentials were allowed for local script execution
- credentials were not repeated in report prose
- probe JSON does not expose the password
- safe URL rendering uses `***`
- env file remains local-only and uncommitted

## 10. Product-dependency conclusion

This round does **not** by itself promote `pymssql` into product runtime dependency.

Still missing before formal dependency promotion:

- vendor the accepted wheel into repository offline packaging
- update product `requirements.txt`
- verify packaged runtime behavior in the plugin path, not only in the isolated probe path

But this round does remove the earlier blocker that said SQL Server runtime readiness was unknown.

## 11. Final verdict

Final verdict:

```text
GO - READY_FOR_SQLSERVER_ADAPTER_IMPLEMENTATION
```

Interpretation:

- isolated dependency gate passed
- isolated real connection probe passed
- local deterministic SQL Server fixture read passed
- adapter implementation may begin next

## 12. Next recommendation

Next step should be the smallest real SQL Server adapter implementation slice:

1. add `sqlserver` as a new allowed `database_type`
2. add `utils/adapters/sqlserver.py`
3. keep verification independent at first
4. do not touch MySQL / PostgreSQL / DM8 behavior
