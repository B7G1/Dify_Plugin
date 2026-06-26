"""Query-result formatting for the stable Dify Tool JSON contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


BASE_RESULT_KEYS = ("columns", "rows", "row_count", "truncated", "max_rows")


def format_sqlalchemy_result(result: Any, *, max_rows: int) -> dict[str, Any]:
    """Convert a SQLAlchemy result object into the stable tool result shape."""
    columns = [str(column) for column in result.keys()]
    fetched_rows = result.mappings().fetchmany(max_rows + 1)
    return format_rows(columns, fetched_rows, max_rows=max_rows)


def format_rows(columns: Sequence[Any], rows: Sequence[Any], *, max_rows: int) -> dict[str, Any]:
    """Format rows from DBAPI/SQLAlchemy-style records.

    ``truncated`` is true only when the caller supplied more than ``max_rows``
    records. Callers that fetch from a cursor should request ``max_rows + 1`` so
    this function can detect truncation without reading the full result set.
    """
    stable_columns = [str(column) for column in columns]
    limited_rows = list(rows[: max_rows + 1])
    truncated = len(limited_rows) > max_rows
    normalized_rows = [
        _format_row(row, stable_columns)
        for row in limited_rows[:max_rows]
    ]
    return {
        "columns": stable_columns,
        "rows": normalized_rows,
        "row_count": len(normalized_rows),
        "truncated": truncated,
        "max_rows": max_rows,
    }


def _format_row(row: Any, columns: Sequence[str]) -> dict[str, Any]:
    if row is None:
        return {}

    if hasattr(row, "_mapping"):
        return _format_mapping(row._mapping)

    if isinstance(row, Mapping):
        return _format_mapping(row)

    if isinstance(row, tuple):
        return {
            column: json_safe(row[index]) if index < len(row) else None
            for index, column in enumerate(columns)
        }

    if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)):
        return {
            column: json_safe(row[index]) if index < len(row) else None
            for index, column in enumerate(columns)
        }

    return {"value": json_safe(row)}


def _format_mapping(row: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(key): json_safe(value) for key, value in row.items()}


def json_safe(value: Any) -> Any:
    """Convert common database values to JSON-serializable primitives."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time, UUID)):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, bytearray):
        return bytes(value).decode("utf-8", errors="replace")
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return str(value)
