# Phase 7.4 — Commit 2C KingbaseES Preview Code Review

Status: REVIEW ONLY  
Date: 2026-07-07  
Branch: `feature/kingbasees-adapter`  
Scope: KingbaseES Preview production-impact code only.

No files were staged or committed as part of this review.

## Reviewed files

```text
db_query_extended/provider/db_query_extended.yaml
db_query_extended/requirements.txt
db_query_extended/utils/validation.py
db_query_extended/utils/adapters/kingbasees.py
db_query_extended/utils/drivers/kingbasees.py
```

## Current behavior

The code currently does the following:

1. Exposes `kingbasees` in the Provider database type dropdown as `KingbaseES (Preview)`.
2. Updates Provider description and port help text to mention KingbaseES.
3. Adds optional `schema` credential to the Provider YAML.
4. Adds `kingbasees` to `SUPPORTED_DATABASE_TYPES`.
5. Sets KingbaseES default port to `54321`.
6. Adds a `KingbaseESAdapter` that builds SQLAlchemy URLs with `kingbase+ksycopg2`.
7. Adds a driver gate that requires:
   - DB-API module: `ksycopg2`
   - SQLAlchemy dialect registry name: `kingbase.ksycopg2`
8. Calls `require_kingbase_runtime()` before engine creation options are returned.
9. Does not add KingbaseES vendor driver, dialect, or native client to `requirements.txt`.

## Positive findings

### Fail-closed runtime gate

`KingbaseESAdapter.build_engine_options()` calls `require_kingbase_runtime()` before returning SQLAlchemy engine options. If the vendor driver or dialect is unavailable, it raises `ConnectionFailedError`.

This means a selected KingbaseES connection should fail before attempting normal execution in a runtime that lacks approved KingbaseES artifacts.

### No unapproved dependency pin

`requirements.txt` still contains only accepted runtime dependencies:

```text
dify_plugin==0.6.2
SQLAlchemy==2.0.51
PyMySQL==1.2.0
psycopg2-binary==2.9.12
dmPython==2.5.32
dmSQLAlchemy==2.0.12
```

No KingbaseES driver/dialect/native package was introduced.

### Existing MySQL / PostgreSQL / DM8 paths are unlikely to be affected

Adapter discovery loads by `database_type`. Existing adapters are unchanged. Existing Provider/Tool/Workflow regression has already passed in Phase 7.3 after the verifier harness fix.

## Risks and unresolved questions

### User-visible Preview exposure before real runtime acceptance

The Provider UI will expose `KingbaseES (Preview)`, even though Phase 10 evidence remains:

```text
evidence_level: MOCK_ONLY
real_database: BLOCKED
workflow: BLOCKED
api: BLOCKED
final_acceptance: BLOCKED
packaging: BLOCKED
```

This is acceptable only if the product policy intentionally allows user-visible preview options that fail closed when runtime artifacts are missing.

It is not acceptable if the release policy requires every provider dropdown option to be fully executable.

### Connection semantics are design assumptions

The adapter mirrors PostgreSQL behavior:

```text
connect_args: connect_timeout, sslmode
session: set_config('statement_timeout', ...)
session: set_config('search_path', ...)
```

These are reasonable PostgreSQL-compatible assumptions, but they have not passed a real KingbaseES server/runtime acceptance gate.

### Dialect registry name is unverified

The driver gate expects:

```text
kingbase.ksycopg2
kingbase+ksycopg2
```

This is a plausible SQLAlchemy naming scheme, but Phase 10 says the real dialect artifact is unavailable. The registry name must be treated as pending real driver/dialect acceptance.

### Preview runtime error message clarified

The previous runtime failure message was generic and could be mistaken for an ordinary connection/configuration failure.

Under the approved Option A preview policy, the fail-closed message now explicitly states that the KingbaseES Preview runtime is not release-accepted on the installation and requires approved Linux amd64 `ksycopg2`, SQLAlchemy dialect, and native client artifacts.

This review item is resolved for the current preview gate. It does not upgrade KingbaseES real-runtime acceptance from BLOCKED.

### `schema` field becomes global

The Provider YAML adds `schema` as a visible optional field for all database types. That is not necessarily wrong, because PostgreSQL/DM8 already use schema/search_path behavior internally, but it changes the Provider form surface beyond KingbaseES.

## Decision

Final recommendation after explicit product decision: **OPTION A APPROVED / READY FOR FINAL STAGED REVIEW**

The product decision is to allow a user-visible `KingbaseES (Preview)` option with a fail-closed runtime gate. The runtime error clarification has been applied. Production-impact files remain isolated from unrelated worktree changes.

The alternatives considered were:

### Option A — Preview is allowed

If user-visible `KingbaseES (Preview)` is allowed despite blocked real runtime acceptance:

1. Keep the provider dropdown option.
2. Keep fail-closed driver/dialect gate.
3. Add clearer docs/comments that this is preview-only and not release-accepted.
4. Optionally adjust runtime error message to mention preview/runtime artifacts explicitly.
5. Commit only these production-impact files:

```text
db_query_extended/provider/db_query_extended.yaml
db_query_extended/requirements.txt
db_query_extended/utils/validation.py
db_query_extended/utils/adapters/kingbasees.py
db_query_extended/utils/drivers/kingbasees.py
```

Potential commit message:

```text
feat: add fail-closed KingbaseES preview adapter gate
```

### Option B — Release dropdown must include only executable adapters

If every visible Provider option must be executable:

1. Do not expose `kingbasees` in Provider YAML yet.
2. Do not add `kingbasees` to `SUPPORTED_DATABASE_TYPES` in production validation.
3. Keep KingbaseES code only as experimental/unwired code or move it out of production adapter discovery.
4. Commit only docs/evidence for Phase 10 blocked status, which has already been done in 2B.

Potential outcome:

```text
Do not commit 2C production code yet.
```

## Minimal safe next step

Ask for explicit product decision before staging 2C:

```text
Should KingbaseES appear in the Provider dropdown now as a fail-closed Preview option, or should it remain hidden until real runtime acceptance passes?
```

## Not recommended

Do not combine 2C with:

```text
local_test_db/
reports/documentation/Phase11_SQLServer_Adapter/
reports/documentation/Phase11_Database_Expansion/
db_query_extended.difypkg
release/db_query_extended/
interactive map files
historical deletions/archive changes
```

Do not claim KingbaseES support is PASS in any current report.
