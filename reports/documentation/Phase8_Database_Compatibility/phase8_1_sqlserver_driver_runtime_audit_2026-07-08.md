# Phase 8.1 - SQL Server driver/runtime entry audit

Date: 2026-07-08  
Scope: SQL Server compatibility entry audit only. No production adapter implementation in this round.

## 1. Goal

Decide whether the repository is ready to begin SQL Server adapter implementation, or whether driver/runtime proof is still missing and must be isolated first.

This round does not modify:

- interactive map / Commit 2G files;
- MySQL adapter;
- PostgreSQL adapter;
- DM8 adapter;
- KingbaseES adapter implementation;
- `tools/db_query_extended.py`;
- `utils/result_formatter.py`;
- SQL safety;
- JSON contract;
- Workflow definitions;
- `verify_all.ps1` baseline contract.

## 2. Current repository state

Observed branch:

```text
feature/kingbasees-adapter
```

Observed dirty worktree:

- remaining modified/untracked files are still dominated by deferred interactive map assets;
- those files stay outside this audit and outside Phase 8 database commits.

Recent history:

- `0c562b0` `docs: defer interactive map visual gate before database expansion`
- `060106f` `chore: tighten local artifact ignore rules`
- `cbc94fa` `test: stage reproducibility infrastructure and historical evidence`
- `1738ce6` `docs: classify release package artifacts`

## 3. Current adapter architecture

Current registration model is lazy module loading by `database_type` string.

Key files:

- `db_query_extended/utils/adapters/__init__.py`
- `db_query_extended/utils/adapters/base.py`
- `db_query_extended/utils/database.py`

Current behavior:

1. Provider credentials carry `database_type`;
2. `validate_connection_config()` normalizes and validates that type;
3. `get_database_adapter(database_type)` imports `utils.adapters.<database_type>`;
4. adapter module exposes `Adapter`;
5. shared execution path in `utils/database.py` uses adapter hooks for:
   - URL build
   - connect args
   - engine options
   - session configuration

This is already a usable adapter surface. Phase 8 should extend it, not replace it.

## 4. SQL Server minimum change surface

If SQL Server moves from audit into implementation, the minimum product change surface is:

| Area | File(s) | Why |
| --- | --- | --- |
| Provider option | `db_query_extended/provider/db_query_extended.yaml` | add `sqlserver` to the dropdown |
| Validation | `db_query_extended/utils/validation.py` | allow `sqlserver`, define default port |
| Adapter | `db_query_extended/utils/adapters/sqlserver.py` | add SQL Server URL/connect/session logic |
| Optional driver gate | `db_query_extended/utils/drivers/sqlserver.py` | only if runtime availability should fail closed |
| Runtime deps | `db_query_extended/requirements.txt` and `db_query_extended/wheels/` | add approved offline dependency set |
| Verification | `db_query_extended/verification/verification_runner.py` | only after driver/runtime proof exists |
| Optional legacy matrix | `db_query_extended/verification/phase2_matrix.py` | only if this matrix remains part of active coverage |

Files that should not change first:

- `tools/db_query_extended.py`
- `utils/result_formatter.py`
- SQL validator / read-only policy
- workflow definitions
- `verify_all.ps1`

## 5. Provider / validation entry points

Provider dropdown is defined in:

- `db_query_extended/provider/db_query_extended.yaml`

Current allowed types are defined in:

- `db_query_extended/utils/validation.py`

Current values:

- `SUPPORTED_DATABASE_TYPES = {"mysql", "postgresql", "dm", "kingbasees"}`
- `DEFAULT_PORTS = {"mysql": 3306, "postgresql": 5432, "dm": 5236, "kingbasees": 54321}`

SQL Server would minimally need:

- `sqlserver` added to `SUPPORTED_DATABASE_TYPES`
- default port `1433`
- provider label/help text added to the select control

## 6. Current runtime dependency state

Current runtime requirements:

- `dify_plugin==0.6.2`
- `SQLAlchemy==2.0.51`
- `PyMySQL==1.2.0`
- `psycopg2-binary==2.9.12`
- `dmPython==2.5.32`
- `dmSQLAlchemy==2.0.12`

Observed SQL Server dependency evidence in current plugin runtime package:

```text
none
```

No SQL Server wheel or requirement entry was found under current plugin runtime packaging for:

- `pyodbc`
- `pymssql`

Therefore SQL Server is not yet a packaging-proven runtime target in this repository.

## 7. Driver comparison

| Candidate | SQLAlchemy URL | Python 3.12 Linux amd64 wheel evidence in repo | System dependency risk | Offline packaging fit | SQLAlchemy 2.x fit | Runtime fit for plugin-daemon | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pyodbc` | `mssql+pyodbc://...` | none in current repo | high | weak | good if driver exists | risky | usually needs Microsoft ODBC driver + unixODBC in the runtime image, which this plugin runtime does not currently provision |
| `pymssql` | `mssql+pymssql://...` | none in current repo | lower than pyodbc | better | historically supported by SQLAlchemy dialect | better candidate | pure plugin packaging story is simpler if a working cp312 Linux wheel exists |
| SQLAlchemy dialect + `pyodbc` | `mssql+pyodbc://...` | dialect is in SQLAlchemy, DBAPI proof missing | high | weak | yes | risky | dialect availability alone does not solve native ODBC driver requirement |
| SQLAlchemy dialect + `pymssql` | `mssql+pymssql://...` | dialect is in SQLAlchemy, DBAPI proof missing | medium | better | yes | plausible | best fit if cp312 Linux amd64 wheel imports cleanly in isolated probe |

## 8. Recommended driver path

Recommended path:

```text
mssql+pymssql
```

Reason:

- current repo already records `driver candidate=pymssql` in `local_test_db/sqlserver/README.md`;
- `pyodbc` likely pulls in a system-level ODBC dependency chain that is a poor fit for the current isolated plugin runtime;
- current plugin packaging is offline and wheel-driven, so a DBAPI that can live entirely inside plugin packaging is the simpler route.

Important limit:

This is still a recommendation, not a release-accepted runtime fact. The repository does not yet contain wheel/import proof for `pymssql` on Python 3.12 Linux amd64.

## 9. Connect URL / args expectations

If `pymssql` is accepted, the likely minimal shape is:

```text
mssql+pymssql://username:password@host:1433/database
```

Likely connect-arg starting point:

- login/connect timeout
- charset / Unicode behavior only if required by actual driver behavior

Session-shaping likely needed:

- database comes from URL;
- schema is likely object qualification rather than PostgreSQL-style `search_path`;
- timeout behavior must be validated with the selected driver before adding product logic.

This is exactly why a probe is needed before product adapter code.

## 10. Verification integration strategy

SQL Server should not go straight into the main verification matrix yet.

Current active verification code:

- `db_query_extended/verification/verification_runner.py`
- `db_query_extended/verification/phase2_matrix.py`

Current matrix coverage already includes:

- MySQL
- PostgreSQL
- DM8

Recommended order:

1. isolated driver/runtime probe;
2. adapter implementation;
3. SQL Server-specific independent verification;
4. only then decide whether it belongs in `verification_runner.py`;
5. only later consider legacy `phase2_matrix.py`.

So the answer is:

```text
yes - verification should start with an independent gate, not the main matrix
```

## 11. `local_test_db/sqlserver` readiness

Current local test environment is materially ready and already evidenced.

Present assets:

- `docker-compose.yml`
- `.env.example`
- `prepare.ps1`
- `init/01_admin_setup.sql`
- `init/02_schema_data.sql`
- `verification/verify.ps1`
- `verification/verify.sql`
- timestamped logs under `logs/`

What it already proves:

- official Microsoft container image path;
- explicit EULA gate;
- isolated Compose project and named volume;
- database `plugin_test`;
- schema `plugin_test`;
- readonly login/user `plugin_readonly`;
- deterministic fixtures;
- readonly permission enforcement;
- SQL verification for `SELECT 1`, `TOP 5`, `COUNT`, Unicode, JOIN, aggregation, and write-blocking.

What it does not prove:

- plugin runtime driver availability;
- SQLAlchemy DBAPI import success for the plugin package;
- offline wheel compatibility for Python 3.12 Linux amd64.

What should remain out of future commits by default:

- `local_test_db/sqlserver/logs/`
- any runtime-only secret output

## 12. Isolated probe decision

Probe decision:

```text
required
```

Reason:

- current product runtime has no SQL Server dependency entry;
- current wheels set has no SQL Server driver proof;
- local Docker database PASS is not equivalent to plugin runtime PASS;
- the cheapest next step is to test import/dialect/URL build readiness in isolation before touching product adapter code.

## 13. Out of scope this round

Not entering this round:

- SQL Server adapter implementation;
- provider dropdown changes;
- validation changes;
- verification matrix integration;
- workflow/API integration;
- interactive map cleanup;
- any modification to MySQL/PostgreSQL/DM8/KingbaseES production behavior.

## 14. Next implementation plan

Smallest safe next step:

1. add one isolated probe script;
2. read only environment variables;
3. test Python import and SQLAlchemy dialect loading;
4. build candidate URL without secrets in output;
5. if full environment exists, optionally test a real connection outside product code;
6. only after that decide whether product adapter work can start.

## 15. Final conclusion

Final conclusion:

```text
CONDITIONAL_GO - NEED_ISOLATED_DRIVER_PROBE
```

SQL Server is the best next database candidate, but the repository does not yet contain runtime-proof evidence for its Python driver path. The local database environment is ready; the plugin runtime is not yet proven.
