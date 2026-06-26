"""Input validation without database-driver dependencies."""

from __future__ import annotations

import re
from typing import Any

from utils.errors import (
    ParameterValidationError,
    ReadOnlyViolationError,
    UnsupportedDatabaseTypeError,
)


SUPPORTED_DATABASE_TYPES = {"mysql", "postgresql"}
DEFAULT_PORTS = {"mysql": 3306, "postgresql": 5432}
MAX_ALLOWED_ROWS = 10_000
MAX_ALLOWED_TIMEOUT = 300


def validate_connection_config(credentials: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize provider credentials without logging secrets."""
    database_type = str(credentials.get("database_type", "")).strip().lower()
    if database_type not in SUPPORTED_DATABASE_TYPES:
        raise UnsupportedDatabaseTypeError(
            "Unsupported database type. Only mysql and postgresql are available in this phase."
        )

    normalized = {"database_type": database_type}
    for field in ("host", "username", "password", "database"):
        value = credentials.get(field)
        if value is None or not str(value).strip():
            raise ParameterValidationError(f"Missing required connection parameter: {field}.")
        normalized[field] = str(value).strip()

    normalized["port"] = _positive_int(
        credentials.get("port") or DEFAULT_PORTS[database_type], "port", maximum=65535
    )
    normalized["connect_timeout"] = _positive_int(
        credentials.get("connect_timeout") or 10, "connect_timeout", maximum=120
    )
    normalized["schema"] = str(credentials.get("schema") or "").strip()
    normalized["charset"] = str(credentials.get("charset") or "").strip()
    return normalized


def validate_tool_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    """Validate the placeholder tool contract for later database execution."""
    sql = str(parameters.get("sql") or "").strip()
    if not sql:
        raise ParameterValidationError("Missing required parameter: sql.")

    readonly = parameters.get("readonly", True)
    if readonly is not True:
        raise ReadOnlyViolationError("Read-only mode must be enabled for this tool.")
    _validate_read_only_sql(sql)

    return {
        "sql": sql,
        "max_rows": _positive_int(parameters.get("max_rows") or 100, "max_rows", MAX_ALLOWED_ROWS),
        "timeout": _positive_int(parameters.get("timeout") or 30, "timeout", MAX_ALLOWED_TIMEOUT),
        "readonly": True,
    }


def _positive_int(value: Any, field: str, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ParameterValidationError(f"{field} must be a whole number.") from exc
    if not 1 <= parsed <= maximum:
        raise ParameterValidationError(f"{field} must be between 1 and {maximum}.")
    return parsed


def _validate_read_only_sql(sql: str) -> None:
    """Conservative guard for the scaffold; a parser-based guard follows later."""
    stripped = sql.strip().rstrip(";").strip()
    if not stripped or ";" in stripped:
        raise ReadOnlyViolationError("Only one SQL statement is allowed.")
    if not re.match(r"^(select|with|show|desc|describe|explain)\b", stripped, flags=re.IGNORECASE):
        raise ReadOnlyViolationError(
            "Only SELECT, WITH, SHOW, DESC, DESCRIBE, and EXPLAIN statements are allowed in read-only mode."
        )
    forbidden = r"\b(insert|update|delete|merge|drop|alter|create|truncate|grant|revoke|call|execute)\b"
    if re.search(forbidden, stripped, flags=re.IGNORECASE):
        raise ReadOnlyViolationError("The SQL contains an operation not allowed in read-only mode.")
