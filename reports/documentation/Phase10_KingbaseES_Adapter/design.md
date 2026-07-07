# Phase 10 — KingbaseES Adapter Design

## Status

Design only. No Provider, Tool, Adapter, dependency, Workflow, packaging, or verification logic is changed by this document.

Baseline: `v1.0.0` / `f7b26b1` / `45 PASS / 0 FAIL / 0 SKIP`.

## Recommended integration

### Server compatibility mode

Use one explicitly identified KingbaseES server release initialized in **PostgreSQL compatibility mode** for Phase 10. KingbaseES offers PostgreSQL, Oracle, MySQL, and SQL Server compatibility modes, so “KingbaseES” alone is not a sufficient runtime contract. The exact server build, compatibility mode, architecture, encoding, and image/installer source must be recorded in evidence.

PostgreSQL compatibility is useful for SQL behavior, session settings, schemas, and common types, but it must not be treated as proof that the existing PostgreSQL Adapter or `psycopg2-binary` is a supported KingbaseES client.

### Python driver and SQLAlchemy dialect

Primary recommendation:

- official KingbaseES `ksycopg2` DB-API driver;
- official KingbaseES SQLAlchemy dialect;
- URL: `kingbase+ksycopg2://user:password@host:54321/database`;
- default port: `54321`;
- short-lived SQLAlchemy engine with the existing `NullPool` lifecycle.

The official documentation identifies `ksycopg2` as the Python DB-API adapter and documents both `kingbase+ksycopg2://...` and `kingbase://...`. It also states that the dialect depends on `ksycopg2`. Do not use generic `psycopg2` as the release solution merely because the server is PostgreSQL-compatible.

Before implementation, obtain and verify a vendor-supported Linux `amd64` combination for:

- the Dify plugin-daemon Python version (currently Python 3.12);
- SQLAlchemy `2.0.51`;
- the selected KingbaseES server build;
- required native client library (`libkci` or the library shipped with that driver);
- offline installation and redistribution terms.

Older official documentation describes narrower Python support and a dialect built against SQLAlchemy 1.3.17. Therefore compatibility with the frozen runtime must be demonstrated, not inferred.

### URL and connection arguments

Proposed Adapter behavior, subject to a real driver probe:

- SQLAlchemy URL driver name: `kingbase+ksycopg2`;
- `host`, `port`, `database`, `username`, and `password` supplied through `sqlalchemy.URL.create`, never string interpolation;
- `connect_timeout` supplied through `connect_args`;
- `sslmode` mapped from the existing `disable | prefer | require` field only if the selected driver accepts the same values;
- no failover, retry, load-balancing, or multi-host fields in the first release.

The vendor driver supports additional HA parameters such as retries, delay, target-session attributes, and load balancing. Those are deliberately out of Phase 10 v1.1 scope because they expand Provider and availability semantics.

### Schema and search path

Keep `database` and `schema` distinct:

- `database` selects the KingbaseES database in the connection URL;
- optional `schema` controls object resolution after connection;
- an empty schema leaves the server/user default unchanged;
- never concatenate an unvalidated schema into SQL.

First probe the same transaction-local pattern used by the PostgreSQL Adapter:

```sql
SELECT set_config('search_path', :schema, true)
```

If the selected compatibility mode or dialect does not support that parameterized form, test `SET LOCAL search_path` with driver-safe identifier quoting. Do not silently fall back to unquoted string composition. Verify rollback/connection-close behavior so a schema setting cannot leak between invocations.

### Timeout

Probe transaction-local `statement_timeout` using the PostgreSQL Adapter pattern. Acceptance requires a real long-running query to be cancelled and mapped to the existing controlled timeout error. Driver connection timeout and statement timeout are separate requirements.

### Values and JSON contract

No KingbaseES-specific output contract is allowed. Values must pass through the existing formatter and preserve:

- Chinese and emoji text as Python `str` and UTF-8 JSON;
- `DATE`, `TIME`, `TIMESTAMP`, and timezone values as stable strings;
- `NUMERIC`/`DECIMAL` precision through `Decimal` string conversion;
- `NULL` as JSON `null`;
- booleans and integers as JSON primitives;
- `BYTEA`/binary values through the current bytes behavior;
- `JSON`/`JSONB`, whether returned as dict/list or text by the selected driver;
- unknown vendor objects through the existing final string conversion only after an explicit test.

The test database must use UTF-8-compatible server and client encodings. Record `SHOW server_encoding` and `SHOW client_encoding`; never rely on the workstation locale.

## SQL security

Do not fork or weaken `utils/sql_validator.py`.

The current allowlist admits only one statement beginning with `SELECT` or `WITH`; its forbidden tokens already cover the major DML, DDL, transaction, privilege, procedure, copy, and maintenance operations. Phase 10 should add KingbaseES security cases without changing the shared validator:

- `INSERT`, `UPDATE`, `DELETE`, `MERGE`;
- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`;
- `COPY`, `CALL`, `EXECUTE`;
- `GRANT`, `REVOKE`;
- `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`, `SET`;
- `VACUUM`, `ANALYZE`, `REINDEX`, `CLUSTER`;
- multi-statement and comment/obfuscation attempts;
- data-modifying CTEs;
- vendor functions with observable side effects, if present in the selected mode.

Use a database login granted only `CONNECT`, `USAGE` on the accepted schema, and `SELECT` on test objects. Database permissions are the second safety boundary. If a real bypass is discovered, stop and open a separate shared-security change with full v1.0 regression; do not hide it in the KingbaseES Adapter.

## Files to add during implementation

- `db_query_extended/utils/adapters/kingbasees.py`
- `db_query_extended/verification/verify_kingbasees.ps1`
- `db_query_extended/verification/verify_kingbasees.py` or an equivalent additive runner
- `reports/verification/<date>/kingbasees_*.json`
- KingbaseES environment/setup documentation under the Phase 10 report directory
- approved offline driver/dialect artifacts only after license and runtime review

Files that will require narrowly scoped extension:

- `db_query_extended/provider/db_query_extended.yaml`: add the KingbaseES option and help text;
- `db_query_extended/utils/validation.py`: add `kingbasees`, default port `54321`, and schema normalization without altering existing branches;
- `db_query_extended/requirements.txt`: add exact offline vendor driver/dialect pins;
- `TEST_MATRIX.md`: change KingbaseES from PLANNED only after real evidence exists.

## Frozen files and behavior

Do not modify as part of the normal Adapter implementation:

- `db_query_extended/utils/adapters/base.py`
- `db_query_extended/tools/db_query_extended.py`
- `db_query_extended/utils/sql_validator.py`
- `db_query_extended/utils/formatter.py`
- `db_query_extended/utils/result_formatter.py`
- `db_query_extended/verification/verify_all.ps1`
- existing MySQL, PostgreSQL, and DM8 adapters and verification expectations
- the published v1.0 Workflow contract

If any frozen file appears necessary, pause for architecture review and prove why an additive Adapter cannot satisfy the requirement.

## Risks and gates

| Risk | Required gate |
| --- | --- |
| Python 3.12 wheel/native ABI unavailable | clean import inside the Linux amd64 plugin-daemon |
| Vendor dialect incompatible with SQLAlchemy 2.0.51 | URL creation, connect, `SELECT 1`, transaction, and result tests in the frozen dependency set |
| Driver/native library redistribution restriction | documented license review before committing binaries or publishing a package |
| Wrong KingbaseES compatibility mode | record server build and mode before test data creation |
| `search_path` or timeout syntax differs | real session probe and rollback/cleanup evidence |
| JSON/type conversion differs | real type matrix through Tool, Workflow, and API |
| PostgreSQL assumptions leak into KingbaseES | dedicated Adapter; no alias to `postgresql.py` |
| Existing behavior regresses | inherited suite remains exactly `45/0/0` |

## Acceptance SQL

Read-only success cases:

```sql
SELECT 1 AS value
SELECT '中文测试 🚀' AS unicode_text
SELECT CURRENT_TIMESTAMP AS current_timestamp
SELECT CAST(1234567890.123456789 AS NUMERIC(28,9)) AS exact_number
SELECT CAST(NULL AS VARCHAR(20)) AS null_value
SELECT TRUE AS boolean_value
SELECT CAST('{"name":"金仓","enabled":true}' AS JSON) AS json_value
SELECT id, unicode_text FROM plugin_test_rows ORDER BY id
SELECT id FROM plugin_test_rows ORDER BY id
```

The final query is executed with a smaller `max_rows` to prove truncation. Add a selected-version-specific sleep query only for timeout verification and never expose it as a normal example.

Blocked cases use the security list above and must be rejected before database execution. Invalid table, invalid credentials, unavailable host, and query timeout must return controlled errors without connection URLs or secrets.

## Regression plan and PASS target

1. Run the untouched v1.0 suite before KingbaseES work: `45 PASS / 0 FAIL / 0 SKIP`.
2. Run additive KingbaseES Adapter/Provider checks against a real server.
3. Install the package into the accepted Dify baseline and validate Provider credentials.
4. Publish a separate KingbaseES Workflow using the frozen input/output contract.
5. Run Workflow API tests with the key supplied only through process environment variables.
6. Rerun the untouched v1.0 suite and compare its three suite totals.

Minimum Phase 10 target:

- inherited regression: exactly `45 PASS / 0 FAIL / 0 SKIP`;
- additive KingbaseES suite: at least `24 PASS / 0 FAIL / 0 SKIP` covering Provider, connection/session behavior, values, truncation, errors, security, Workflow, and API;
- combined evidence target: at least `69 PASS / 0 FAIL / 0 SKIP`.

The precise additive count must be frozen in the verification specification before implementation; tests must not be removed merely to reach the target.

## Research sources

- [KingbaseES Python driver overview](https://help.kingbase.com.cn/v8/development/client-interfaces/python/python-1.html)
- [KingbaseES SQLAlchemy usage and URL](https://help.kingbase.com.cn/v8/development/client-interfaces-frame/sqlalchemy/sqlalchemy-2.html)
- [KingbaseES V9 SQLAlchemy example](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/application_development/client-interfaces-frame/sqlalchemy/sqlalchemy-3.html)
- [KingbaseES compatibility modes and SQL capabilities](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/data_migration/migration_overview.html)
- [KingbaseES Python HA/connection parameters](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/application_development/client-interfaces/python/python-5.html)
- [KingbaseES character sets and client encoding](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/local/local-3.html)
- [KingbaseES common types including JSON](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/application_development/development-guide/development-sql.html)

## Implementation readiness

The architecture is suitable for an additive KingbaseES Adapter, but code implementation is **not yet authorized** until the exact server build/compatibility mode and a redistributable Linux amd64 Python 3.12 + SQLAlchemy 2.0.51 driver/dialect combination pass the clean-runtime probe.
