# Phase 9.6 — KingbaseES Plugin-Owned Dialect and Adapter Implementation Gate

- Date: 2026-07-12
- Phase: Phase 9.6
- Status: PASS
- Database: KingbaseES
- Scope: Plugin-owned scoped SQLAlchemy dialect, formal Adapter, real Adapter runtime, and targeted PostgreSQL isolation
- Source commit: `bff16f4`
- Runtime: `dify-plugin_daemon-1`, Python 3.12.3, SQLAlchemy 2.0.51, ksycopg2 2.9.1
- Canonical path: `reports/documentation/2026-07-12/Phase09_KingbaseES/phase9_6_kingbasees_dialect_adapter_implementation_gate.md`
- Machine evidence: `reports/verification/2026-07-12/kingbasees_phase9_6_*.json`
- Logs: `reports/logs/2026-07-12/Phase09_KingbaseES/phase9_6_*.log`
- Supersedes: Phase 9.5 experimental compatibility shim as the Adapter implementation route
- Security classification: Internal engineering; credentials and external driver binary excluded

## Executive Summary

Phase 9.6 is `PASS`.

The Phase 9.5 process-local `psycopg2` namespace aliases were not reused. The plugin now owns a scoped `kingbasees.ksycopg2` SQLAlchemy dialect derived from the generic PostgreSQL base dialect, imports `ksycopg2` directly, parses the verified KingbaseES version format, and creates real Engines through the formal `KingbaseESAdapter`.

The formal Adapter connected from the real Dify plugin-daemon to the preserved KingbaseES V009R001C010 server and passed scalar, Unicode, binding, NULL, numeric, date/time, schema, rollback, close, dispose, error-redaction, and public database-utility checks. A real Dify PostgreSQL `SELECT 1` plus module/dialect identity checks confirmed the PostgreSQL path remains unchanged.

This is an Adapter-level PASS. Provider, Tool, Workflow, offline packaging, redistribution approval, and end-to-end plugin acceptance remain outside this gate.

## Goal and Acceptance Boundary

The gate converts the experimental SQLAlchemy feasibility route into a maintainable plugin-owned dialect and formal Adapter without:

- modifying SQLAlchemy;
- downgrading SQLAlchemy 2.0.51;
- modifying PostgreSQLAdapter;
- injecting `ksycopg2` into `sys.modules["psycopg2"]`;
- creating a fake top-level `psycopg2` package;
- changing Provider or Tool exposure;
- committing the external driver wheel before redistribution review.

## Baseline

- Branch: `feature/kingbasees-adapter`
- HEAD at start: `566f8d7 test: verify KingbaseES driver runtime in plugin-daemon`
- Reporting baseline: `0787d42`
- Phase 9.4 runtime baseline: `736902d`
- Phase 9.5 was already independently committed and was not amended.
- The complete initial `git status --short` was captured before coding; all pre-existing user paths remained protected.

## Minimal Architecture Analysis

Existing Adapter contract:

- `build_database_url(config) -> URL`
- `build_connect_args(config) -> dict`
- optional shared `build_engine_options` using `pool_pre_ping`
- `configure_session(connection, config, timeout)`
- shared `execute_query` using SQLAlchemy `text`

Existing registry behavior:

- `get_database_adapter(database_type)` dynamically imports `utils.adapters.<database_type>` and instantiates its `Adapter` alias;
- no central registry table needed modification;
- adding or changing the internal KingbaseES module does not itself change Provider YAML or Tool inputs.

Existing common lifecycle:

- `utils.database.create_database_engine` owns `create_engine`, `NullPool`, and engine options;
- verification and query helpers dispose engines in `finally`;
- result formatting, read-only validation, max rows, and normalized public errors remain shared and unchanged.

KingbaseES-specific responsibilities are therefore limited to one dialect module, the existing KingbaseES Adapter, and its driver availability gate.

## SQLAlchemy 2.0.51 Source Audit

Inspected the exact isolated SQLAlchemy 2.0.51 source used by the plugin-daemon.

Reusable from `PGDialect`:

- PostgreSQL compiler and identifier/type behavior;
- generic transaction SQL;
- default schema/search-path inspection;
- standard cursor/result execution;
- pool pre-ping support.

Rejected from `PGDialect_psycopg2` because it hardcodes psycopg2:

- `import psycopg2` in `import_dbapi`;
- `psycopg2.extensions` isolation constants;
- `psycopg2.extras` UUID/HSTORE/JSON registration;
- psycopg2 execution context, identifier preparer and range adapters;
- execute_batch and two-phase status constants;
- psycopg2-specific native HSTORE initialization.

The generic `PGDialect` also exposes one incompatibility: its version parser accepts PostgreSQL/EnterpriseDB strings only. KingbaseES must override that method.

## Route Decision

Chosen: **Route A — independent dialect derived from `PGDialect`**.

Reason:

- the required SELECT/binding/transaction behavior works through generic DB-API 2.0;
- no psycopg2 namespace is needed;
- the override surface is small and directly covered;
- PostgreSQL registry and Adapter remain untouched.

Rejected:

- Route B wrapper: unnecessary after generic `PGDialect` passed real runtime tests;
- Route C `PGDialect_psycopg2`: rejected due to multiple hardcoded psycopg2 imports and extras/constants;
- Phase 9.5 global alias: rejected as non-maintainable product behavior;
- SQLAlchemy downgrade: rejected because 2.0.51 is the required plugin baseline.

## Formal Dialect

Path:

`db_query_extended/utils/dialects/kingbasees.py`

Class:

`KingbaseESDialect_ksycopg2`

Registration:

- registry name: `kingbasees.ksycopg2`
- URL driver: `kingbasees+ksycopg2`
- registration is concentrated in `register_kingbasees_dialect()` and is idempotent;
- `import_dbapi()` imports `ksycopg2` directly;
- SQLAlchemy URL `username` is translated to the ksycopg2 DB-API `user` argument.

No product file references `sys.modules` or imports psycopg2 for the KingbaseES path.

## Server Version Parsing

Accepted verified format:

`KingbaseES VmmmRrrrCccc` with an optional `Bbbbb` build suffix and surrounding whitespace.

`V009R001C010` maps to `(9, 1, 10)`, whose fields mean major, release and component. A build suffix does not change that stable compatibility tuple. Unknown formats raise an explicit `AssertionError`; the dialect does not extract arbitrary numbers or pretend the server is PostgreSQL.

## Formal Adapter

Path:

`db_query_extended/utils/adapters/kingbasees.py`

Class:

`KingbaseESAdapter`

Behavior:

- registers the plugin-owned dialect before returning its URL;
- builds URLs through `URL.create`, preserving escaping and redaction;
- uses the pre-existing explicit host, port and database configuration;
- retains the pre-existing Phase 10 test port default without claiming it as a new official product default;
- passes `connect_timeout` and `sslmode` to ksycopg2;
- retains `pool_pre_ping` and shared `NullPool` lifecycle;
- applies transaction-local statement timeout and bound `search_path` configuration;
- does not concatenate schema text into SQL.

No common Adapter base, `database.py`, validation, formatter, Provider, Tool or Workflow file changed.

## Implementation Failure and Root-Cause Fix

First formal real Adapter run:

- dialect unit tests: PASS;
- Adapter unit tests: PASS;
- PostgreSQL identity regression: PASS;
- real connection: FAIL with `ksycopg2.ProgrammingError: invalid connection option "username"`.

Root cause:

Generic `PGDialect` translated the SQLAlchemy URL field as `username`, while ksycopg2 accepts the DB-API key `user`.

Fix:

The KingbaseES dialect now overrides `create_connect_args` and calls `url.translate_connect_args(username="user")`. The rerun passed every suite. No caller, Adapter base, or common utility workaround was added.

## Verification Results

### Dialect tests — 6 PASS

- verified and build-suffixed version parsing;
- unknown format rejection;
- idempotent registry registration/load;
- direct ksycopg2 import and pyformat;
- AUTOCOMMIT and READ COMMITTED handling;
- disconnect classification;
- psycopg2 namespace isolation and no fake package.

### Adapter tests — 5 PASS

- dynamic lookup resolves `KingbaseESAdapter`;
- URL is `kingbasees+ksycopg2`, escaped and redacted;
- DB-API receives `user`, not `username`;
- timeout, SSL and engine options preserved;
- statement timeout and schema are bound parameters;
- existing MySQL, PostgreSQL, DM8 and SQL Server identities unchanged;
- shared read-only validator still allows SELECT and blocks representative DML, DDL and multi-statement SQL.

### Real formal Adapter runtime — 4 PASS

| Check | Result |
| --- | --- |
| Engine created by formal Adapter | PASS |
| real authentication | PASS |
| server version | `KingbaseES V009R001C010` |
| search path | `public` |
| `SELECT 1` | `1` |
| Unicode literal | `金仓数据库` |
| Unicode named binding | `参数绑定` |
| NULL | PASS |
| NUMERIC | `42.50` as Decimal |
| date/time | native date and timestamp values PASS |
| schema-qualified read | `pg_catalog.pg_database` returned `kingbase` |
| rollback | PASS |
| connection close | PASS |
| engine dispose | PASS |
| public result contract | columns/rows/row_count/truncated/max_rows PASS |
| deliberate bad authentication | controlled redacted error PASS |
| deliberate unreachable endpoint | controlled redacted error PASS |

All database queries were read-only; no fixture or business table was created.

### PostgreSQL targeted regression — 2 PASS

- imported psycopg2 object identity unchanged before/after KingbaseES registration;
- `postgresql.psycopg2` dialect identity unchanged;
- PostgreSQL Adapter URL remains `postgresql+psycopg2`;
- real Dify PostgreSQL `SELECT 1` returned `1`, followed by close and dispose.

## Public Contract Boundary

The unchanged common utility successfully executed the formal KingbaseES Adapter and returned:

- `columns`
- `rows`
- `row_count`
- `truncated`
- `max_rows`
- `execution_time_ms`

Provider/Tool/Workflow were not executed, so their status remains `NOT_YET_TESTED` for KingbaseES.

## Driver and Packaging Boundary

Runtime validation retains:

- ksycopg2 2.9.1;
- wheel SHA-256 `59D2D19439FA0D8AE66A7972EF9EF1FE461E84389D50BC3E90C59ABB4962287A`;
- SQLAlchemy 2.0.51.

The driver remains in ignored external assets and the isolated plugin-daemon test directory. Formal wheel inclusion, LGPL notice, bundled `libkci.so.5` redistribution review, requirements and offline package closure are deferred.

## Commands Executed

Representative reproducible commands from `E:\Dify_Plugin`:

```powershell
git status --short
git log -15 --oneline
git branch --show-current

docker cp db_query_extended\utils dify-plugin_daemon-1:/tmp/kingbasees_phase96/plugin/
docker cp db_query_extended\verification\kingbasees_phase9_6_gate.py `
  dify-plugin_daemon-1:/tmp/kingbasees_phase96/kingbasees_phase9_6_gate.py

docker exec --env PYTHONPATH=/tmp/kingbasees_phase95/site:/tmp/kingbasees_phase96/plugin `
  --env KINGBASE_HOST=host.docker.internal --env KINGBASE_PORT=54321 `
  --env KINGBASE_DATABASE=kingbase --env KINGBASE_SCHEMA=public `
  --env KINGBASE_USERNAME=<runtime-user> --env KINGBASE_PASSWORD=<runtime-secret> `
  --env POSTGRES_HOST=dify-db_postgres-1 --env POSTGRES_PORT=5432 `
  --env POSTGRES_DATABASE=<runtime-db> --env POSTGRES_USERNAME=<runtime-user> `
  --env POSTGRES_PASSWORD=<runtime-secret> dify-plugin_daemon-1 `
  /usr/bin/python3 /tmp/kingbasees_phase96/kingbasees_phase9_6_gate.py `
  --output-dir /tmp/kingbasees_phase96/output
```

Credentials came from existing container environments, were passed transiently and were never printed or persisted.

## Files Changed

Product implementation:

- added `db_query_extended/utils/dialects/__init__.py`;
- added `db_query_extended/utils/dialects/kingbasees.py`;
- updated `db_query_extended/utils/drivers/kingbasees.py` from external-dialect gate to plugin-owned dialect gate;
- updated existing `db_query_extended/utils/adapters/kingbasees.py` to use the scoped registration and new URL.

Verification:

- added `db_query_extended/verification/kingbasees_phase9_6_gate.py`;
- added four machine JSON files and five redacted logs;
- added this report and one `REPORT_MAP` row.

## Decisions

- Chosen: generic PGDialect plus four Kingbase-specific concerns—DB-API import, connect-key mapping, version parsing and isolation/disconnect behavior.
- Kept: existing dynamic Adapter registry, shared engine lifecycle, validation, formatter and read-only security.
- Rejected: global aliases, fake psycopg2 package, PostgreSQL Adapter changes, SQLAlchemy downgrade, broad registry refactor and premature wheel packaging.

## Blockers

No Phase 9.6 acceptance blocker remains.

Future gates still require:

- Provider/Tool integration;
- formal credential schema and UI lifecycle validation;
- offline wheel/notice/redistribution closure;
- installed-plugin and Workflow evidence.

## Abandoned Paths

- `PGDialect_psycopg2` inheritance: rejected after source audit exposed extensive hardcoded psycopg2 behavior.
- DB-API wrapper: unnecessary because Route A passed.
- Phase 9.5 `sys.modules` alias: prohibited and absent from product code.
- First Route A connection: failed on `username`; fixed once at dialect connection-argument translation.
- SQLAlchemy 1.x downgrade: rejected.
- PostgreSQL Adapter modification: unnecessary and rejected.

## Security and Redaction

No password, `.env`, license content, ISO, Docker tar, external wheel, API token, or credentialed URL is tracked. Deliberate failure tests verify public messages do not contain submitted secrets.

## Reproduction Trace

Prerequisites: preserved KingbaseES container, running plugin-daemon, isolated Phase 9.5 driver/SQLAlchemy site, running Dify PostgreSQL, and transient runtime credentials.

Run the Phase 9.6 gate from the real plugin-daemon with the copied current `utils` tree and explicit `PYTHONPATH`. PASS requires all four generated suites to report PASS and product source scans to contain neither `sys.modules` aliasing nor psycopg2 dependencies in the KingbaseES dialect/Adapter/driver modules.

Failure meanings remain distinct: dialect registration/version/connect-argument failure, Adapter contract failure, real database/authentication/query/type/schema/cleanup failure, or PostgreSQL isolation regression.

## Git State

Only Phase 9.6 implementation, dedicated test, report, evidence, logs and the single REPORT_MAP entry are eligible for the independent commit. The stored baseline is compared against final status before staging.

## Final Decision

`PASS`

All Phase 9.6 criteria are met without an alias or fake psycopg2 package. The formal Adapter owns the Engine path and passed real execution in the required runtime.

## Next Step

Proceed to Phase 9.7 — KingbaseES Provider and Tool Integration Gate. Do not treat this Adapter PASS as Provider, Tool, Workflow, packaging or final compatibility PASS.
