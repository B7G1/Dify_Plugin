# 2026-06-26 Plugin Core Freeze Summary

## Why Not DM Today

DM and KingbaseES are database adapter work. The plugin already passed real Dify Workflow validation for MySQL and PostgreSQL on 2026-06-25, so today focused on freezing the shared core first. This reduces the chance that future adapters rewrite connection handling, JSON formatting, SQL safety, or Tool-layer orchestration.

## Core Work Completed

### Database Layer

- `utils/database.py` now has explicit `build_database_url`, `build_connect_args`, and `build_engine_options` helpers.
- MySQL URI remains `mysql+pymysql`.
- PostgreSQL URI remains `postgresql+psycopg2`.
- `connect_timeout` is implemented through DBAPI `connect_args`.
- `pool_pre_ping=True` remains implemented.
- `NullPool` remains intentional for short-lived Dify plugin invocations.
- `pool_timeout` and `pool_recycle` are documented as reserved, not implemented, because `NullPool` does not retain a reusable queue of connections.
- Engines are still disposed in `finally` for both credential validation and query execution.

### Formatter Layer

- Added `utils/formatter.py`.
- Stable result shape:

```json
{
  "columns": [],
  "rows": [],
  "row_count": 0,
  "truncated": false,
  "max_rows": 100
}
```

- Handles tuple, dict, SQLAlchemy mapping rows, `None`, datetime/date/time, Decimal, bytes, bool, int, float, str, nested mappings/sequences, and fallback objects.
- `truncated` is true only when the caller provides more than `max_rows` rows. SQLAlchemy query execution fetches `max_rows + 1` to detect this without loading the full result set.

### SQL Read-Only Validation

- Public contract is now one `SELECT` or `WITH` statement.
- DDL, DML, procedure calls, file operations, transaction commands, `SET`, `USE`, semicolon chaining, and comment-based bypasses are blocked.
- Strings, quoted identifiers, SQL comments, and PostgreSQL dollar-quoted strings are lexed so forbidden words inside string literals do not cause false positives.
- Conservative note: unquoted identifiers that are identical to dangerous SQL verbs may be rejected. Quote such identifiers in SQL if needed.

### Tool Layer

- `tools/db_query_extended.py` remains thin: validate parameters, validate credentials, execute database query, format success/error response.
- User-facing errors still avoid full Python tracebacks.

## Stable Capabilities

- MySQL Provider credential validation.
- PostgreSQL Provider credential validation.
- MySQL/PostgreSQL read-only query execution.
- Stable JSON result keys.
- Safe truncation reporting.
- Read-only SQL guardrail.
- Wrong-password path remains user-readable through existing error handling.

## Reserved But Not Implemented

- DM adapter branch.
- KingbaseES adapter branch.
- Real connection pool lifecycle.
- `pool_timeout` and `pool_recycle`.
- Automatic reconnect.
- Markdown output.
- Workflow API rerun in this session, because API environment variables were not set.
