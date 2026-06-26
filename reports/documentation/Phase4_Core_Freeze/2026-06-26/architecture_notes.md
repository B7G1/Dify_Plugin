# 2026-06-26 Architecture Notes

## Database Layer

`utils/database.py` now exposes clear helpers for:

- SQLAlchemy URL generation,
- DBAPI connect arguments,
- engine options,
- query execution.

Current implementation keeps `NullPool` because plugin invocations are short-lived. `pool_timeout`, `pool_recycle`, real pooling, and automatic reconnect are reserved but not implemented.

## Formatter Layer

`utils/formatter.py` owns conversion from database rows to the stable Dify Tool JSON shape:

- `columns`
- `rows`
- `row_count`
- `truncated`
- `max_rows`

It handles common database value types and falls back to string conversion for unknown objects.

## SQL Safety

The public contract is one `SELECT` or `WITH` statement. Dangerous statements, transaction control, file operations, multi-statement input, and comment-based bypass attempts are blocked.

## Tool Boundary

The Tool layer remains an orchestrator. It does not own SQL parsing, connection construction, or row formatting.
