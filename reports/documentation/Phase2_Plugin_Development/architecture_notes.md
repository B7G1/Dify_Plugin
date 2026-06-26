# Phase 2 Architecture Notes

## Core Shape

- `provider/db_query_extended.py`: validates credentials with `SELECT 1`.
- `tools/db_query_extended.py`: validates Tool parameters and executes read-only SQL.
- `utils/database.py`: owns SQLAlchemy connection and query execution.
- `utils/validation.py` and `utils/sql_validator.py`: own user input and SQL safety checks.
- `utils/result_formatter.py`: wraps success/error responses for Dify.

## Stable Contract

The Tool response keeps these keys stable:

- `success`
- `database_type`
- `execution_time_ms`
- `columns`
- `rows`
- `row_count`
- `truncated`
- `max_rows`
- `generated_at`
- `warning`
- `error`
