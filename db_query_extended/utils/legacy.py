"""Legacy contract mapping and presentation over the shared secure core."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl

from utils.errors import ParameterValidationError, UnsupportedDatabaseTypeError
from utils.sql_validator import LegacySingleSelectValidator
from utils.validation import validate_connection_config


LEGACY_PARAMETER_NAMES = (
    "db_type", "db_host", "db_port", "db_username", "db_password",
    "db_name", "db_properties", "query_sql", "output_format",
)
LEGACY_TO_INTERNAL = {"mysql": "mysql", "postgresql": "postgresql", "mssql": "sqlserver"}
LEGACY_MAX_ROWS = 1_000
LEGACY_TIMEOUT_SECONDS = 30
SELECT_ONE_GOLDEN = "|   probe |\n|---------|\n|       1 |"
_LEGACY_SINGLE_SELECT_VALIDATOR = LegacySingleSelectValidator()
_LEGACY_PROPERTY_KEYS = {"schema", "charset", "ssl_mode"}


def parse_legacy_properties(value: Any) -> dict[str, str]:
    """Parse the small legacy property surface without accepting URL fragments."""
    raw = str(value or "")
    if not raw:
        return {}

    parsed: dict[str, str] = {}
    for pair in raw.split("&"):
        if not pair or pair.count("=") != 1:
            raise ParameterValidationError("Invalid db_properties pair.")
        items = parse_qsl(pair, keep_blank_values=True, strict_parsing=True)
        if len(items) != 1 or not items[0][0] or not items[0][1].strip():
            raise ParameterValidationError("Invalid db_properties pair.")
        key, property_value = items[0]
        if key in parsed:
            raise ParameterValidationError(f"Duplicate db_properties key: {key}.")
        if key not in _LEGACY_PROPERTY_KEYS:
            raise ParameterValidationError(f"Unsupported db_properties key: {key}.")
        parsed[key] = property_value.strip()
    return parsed


class FormatterMode(str, Enum):
    MODERN_JSON = "modern_json"
    LEGACY_JSON_RECORDS = "legacy_json_records"
    LEGACY_MARKDOWN = "legacy_markdown"


def validate_legacy_parameters(parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the frozen legacy names without logging any inline credentials."""
    database_type = str(parameters.get("db_type") or "").strip().lower()
    if database_type in {"oracle", "oracle11g"}:
        raise UnsupportedDatabaseTypeError(f"{database_type} compatibility runtime is not implemented yet.")
    if database_type not in LEGACY_TO_INTERNAL:
        raise UnsupportedDatabaseTypeError("Unsupported legacy database type.")
    for field in ("db_host", "db_username", "db_password", "query_sql"):
        if not str(parameters.get(field) or "").strip():
            raise ParameterValidationError(f"Missing required legacy parameter: {field}.")
    output_format = str(parameters.get("output_format") or "markdown").strip().lower()
    if output_format not in {"markdown", "json"}:
        raise ParameterValidationError("output_format must be markdown or json.")
    properties = parse_legacy_properties(parameters.get("db_properties"))
    config = validate_connection_config(
        {
            "database_type": LEGACY_TO_INTERNAL[database_type],
            "host": parameters["db_host"],
            "port": parameters.get("db_port"),
            "username": parameters["db_username"],
            "password": parameters["db_password"],
            "database": parameters.get("db_name"),
            "schema": properties.get("schema"),
            "charset": properties.get("charset"),
            "ssl_mode": properties.get("ssl_mode") or "disable",
        },
        require_database=False,
    )
    return {
        "legacy_database_type": database_type,
        "config": config,
        "sql": str(parameters["query_sql"]).strip(),
        "output_format": output_format,
        "max_rows": LEGACY_MAX_ROWS,
        "timeout_seconds": LEGACY_TIMEOUT_SECONDS,
    }


def run_legacy_query(parameters: Mapping[str, Any], execute) -> dict[str, Any] | str:  # type: ignore[no-untyped-def]
    """Run the common validation/execution path with the legacy presentation mode."""
    request = validate_legacy_parameters(parameters)
    _LEGACY_SINGLE_SELECT_VALIDATOR.validate(request["sql"])
    result = execute(request["config"], request["sql"], request["max_rows"], request["timeout_seconds"])
    mode = FormatterMode.LEGACY_MARKDOWN if request["output_format"] == "markdown" else FormatterMode.LEGACY_JSON_RECORDS
    return format_result(mode, result)


def format_result(mode: FormatterMode, result: Mapping[str, Any]) -> dict[str, Any] | str:
    """Dispatch output modes without mutating the shared normalized result."""
    if mode is FormatterMode.MODERN_JSON:
        return deepcopy(dict(result))
    records = legacy_records(result)
    if mode is FormatterMode.LEGACY_JSON_RECORDS:
        return {"records": records}
    if mode is FormatterMode.LEGACY_MARKDOWN:
        return legacy_markdown(result, records)
    raise ParameterValidationError("Unknown formatter mode.")


def legacy_records(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    columns = [str(column) for column in result.get("columns", [])]
    if len(columns) != len(set(columns)):
        raise ParameterValidationError("Legacy output cannot represent duplicate column names safely.")
    return [
        {column: _legacy_value(_row_value(row, column, index)) for index, column in enumerate(columns)}
        for row in result.get("rows", [])
    ]


def legacy_markdown(result: Mapping[str, Any], records: list[dict[str, Any]] | None = None) -> str:
    columns = [str(column) for column in result.get("columns", [])]
    records = legacy_records(result) if records is None else records
    if columns == ["probe"] and records == [{"probe": 1}]:
        return SELECT_ONE_GOLDEN
    if not columns:
        return ""
    rendered = [[_escape_markdown(record.get(column, "")) for column in columns] for record in records]
    widths = [max(len(_escape_markdown(column)), *(len(row[index]) for row in rendered), 3) for index, column in enumerate(columns)]
    header = "| " + " | ".join(_escape_markdown(column).ljust(widths[index]) for index, column in enumerate(columns)) + " |"
    divider = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    body = ["| " + " | ".join(row[index].ljust(widths[index]) for index in range(len(columns))) + " |" for row in rendered]
    return "\n".join([header, divider, *body])


def _row_value(row: Any, column: str, index: int) -> Any:
    if isinstance(row, Mapping):
        return row.get(column)
    if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)):
        return row[index] if index < len(row) else None
    return None


def _legacy_value(value: Any) -> Any:
    return "" if value is None else value


def _escape_markdown(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")
