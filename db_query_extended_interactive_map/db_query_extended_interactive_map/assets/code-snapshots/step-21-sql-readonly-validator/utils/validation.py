"""Input validation without database-driver dependencies."""

from __future__ import annotations

from typing import Any

from utils.errors import (
    ParameterValidationError,
    ReadOnlyViolationError,
    UnsupportedDatabaseTypeError,
)
from utils.sql_validator import ReadOnlyValidator


SUPPORTED_DATABASE_TYPES = {"mysql", "postgresql"}
DEFAULT_PORTS = {"mysql": 3306, "postgresql": 5432}
MAX_ALLOWED_ROWS = 1_000
MAX_ALLOWED_TIMEOUT = 120

_READ_ONLY_VALIDATOR = ReadOnlyValidator()


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
    normalized["connection_timeout"] = _positive_int(
        credentials.get("connection_timeout") or credentials.get("connect_timeout") or 10,
        "connection_timeout",
        maximum=120,
    )
    ssl_mode = str(credentials.get("ssl_mode") or "disable").strip().lower()
    if ssl_mode not in {"disable", "prefer", "require"}:
        raise ParameterValidationError("ssl_mode must be disable, prefer, or require.")
    normalized["ssl_mode"] = ssl_mode
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
    _READ_ONLY_VALIDATOR.validate(sql)

    output_format = str(parameters.get("output_format") or "json").strip().lower()
    if output_format != "json":
        raise ParameterValidationError("output_format currently supports json only; markdown is planned for a future extension.")

    return {
        "sql": sql,
        "max_rows": _positive_int(parameters.get("max_rows") or 100, "max_rows", MAX_ALLOWED_ROWS),
        "timeout_seconds": _positive_int(
            parameters.get("timeout_seconds") or parameters.get("timeout") or 30,
            "timeout_seconds",
            MAX_ALLOWED_TIMEOUT,
        ),
        "output_format": output_format,
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
