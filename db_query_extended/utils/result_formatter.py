"""Uniform JSON result schema for successful and failed tool invocations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from utils.errors import DatabaseQueryError


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def success_response(database_type: str, query_result: dict[str, Any]) -> dict[str, Any]:
    truncated = bool(query_result.get("truncated", False))
    max_rows = int(query_result.get("max_rows", 100))
    return {
        "success": True,
        "database_type": database_type,
        "execution_time_ms": int(query_result.get("execution_time_ms", 0)),
        "columns": query_result.get("columns", []),
        "rows": query_result.get("rows", []),
        "row_count": int(query_result.get("row_count", 0)),
        "truncated": truncated,
        "max_rows": max_rows,
        "generated_at": utc_now_iso(),
        "warning": f"Result was truncated to max_rows={max_rows}." if truncated else None,
        "error": None,
    }


def error_response(
    exc: Exception,
    *,
    database_type: str | None = None,
    execution_time_ms: int = 0,
    max_rows: int = 100,
) -> dict[str, Any]:
    user_message = str(exc) if isinstance(exc, DatabaseQueryError) else "The query request could not be completed."
    return {
        "success": False,
        "database_type": database_type,
        "execution_time_ms": execution_time_ms,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "truncated": False,
        "max_rows": max_rows,
        "generated_at": utc_now_iso(),
        "warning": None,
        "error": {
            "type": exc.__class__.__name__,
            "message": user_message,
        },
    }
