"""SQLAlchemy connection and query helpers for MySQL and PostgreSQL."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError, ProgrammingError, TimeoutError as SATimeoutError
from sqlalchemy.pool import NullPool

from utils.errors import ConnectionFailedError, QueryTimeoutError, SqlExecutionError


logger = logging.getLogger(__name__)


def create_database_engine(config: dict[str, Any]) -> Engine:
    """Create an engine without logging its URL or credentials."""
    database_type = config["database_type"]
    if database_type == "mysql":
        url = URL.create(
            "mysql+pymysql", username=config["username"], password=config["password"],
            host=config["host"], port=config["port"], database=config["database"],
        )
        connect_args: dict[str, Any] = {"connect_timeout": config["connect_timeout"]}
        if config["charset"]:
            connect_args["charset"] = config["charset"]
    elif database_type == "postgresql":
        url = URL.create(
            "postgresql+psycopg2", username=config["username"], password=config["password"],
            host=config["host"], port=config["port"], database=config["database"],
        )
        connect_args = {"connect_timeout": config["connect_timeout"]}
    else:
        raise ConnectionFailedError("The selected database type is not configured.")
    # A plugin request owns a single short-lived connection. NullPool avoids
    # retaining gevent-patched connections across Dify plugin invocations.
    return create_engine(url, pool_pre_ping=True, poolclass=NullPool, connect_args=connect_args)


def verify_database_connection(config: dict[str, Any]) -> None:
    """Verify driver authentication and query readiness with SELECT 1."""
    engine = create_database_engine(config)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (OperationalError, DBAPIError) as exc:
        logger.warning("Database connection verification failed: %s", exc.__class__.__name__)
        raise ConnectionFailedError(
            "Unable to connect to the database. Check database type, host, port, database name, and credentials."
        ) from exc
    finally:
        engine.dispose()


def execute_read_only_query(config: dict[str, Any], sql: str, max_rows: int, timeout: int) -> dict[str, Any]:
    """Execute one validated read-only statement and return at most ``max_rows`` rows."""
    engine = create_database_engine(config)
    try:
        with engine.connect() as connection:
            with connection.begin():
                _apply_query_timeout(connection, config["database_type"], timeout)
                if config["schema"] and config["database_type"] == "postgresql":
                    connection.execute(
                        text("SELECT set_config('search_path', :schema, true)"),
                        {"schema": config["schema"]},
                    )
                result = connection.execute(text(sql))
                columns = list(result.keys())
                fetched_rows = result.mappings().fetchmany(max_rows + 1)
        truncated = len(fetched_rows) > max_rows
        rows = [_json_safe(dict(row)) for row in fetched_rows[:max_rows]]
        return {"columns": columns, "row_count": len(rows), "rows": rows, "truncated": truncated, "max_rows": max_rows}
    except SATimeoutError as exc:
        logger.warning("Database query timed out")
        raise QueryTimeoutError("The database query timed out. Reduce query complexity or increase timeout.") from exc
    except OperationalError as exc:
        if _is_timeout(exc):
            logger.warning("Database query timed out")
            raise QueryTimeoutError("The database query timed out. Reduce query complexity or increase timeout.") from exc
        logger.warning("Database query connection failed: %s", exc.__class__.__name__)
        raise ConnectionFailedError("Database connection failed while executing the query.") from exc
    except ProgrammingError as exc:
        logger.warning("Database query was rejected: %s", exc.__class__.__name__)
        raise SqlExecutionError("SQL execution failed. Check SQL syntax and referenced database objects.") from exc
    except DBAPIError as exc:
        if _is_timeout(exc):
            logger.warning("Database query timed out")
            raise QueryTimeoutError("The database query timed out. Reduce query complexity or increase timeout.") from exc
        logger.warning("Database query failed: %s", exc.__class__.__name__)
        raise SqlExecutionError("SQL execution failed. Check the query and database objects.") from exc
    finally:
        engine.dispose()


def _apply_query_timeout(connection: Any, database_type: str, timeout: int) -> None:
    timeout_ms = timeout * 1000
    if database_type == "mysql":
        connection.execute(text("SET SESSION MAX_EXECUTION_TIME = :timeout_ms"), {"timeout_ms": timeout_ms})
    elif database_type == "postgresql":
        connection.execute(
            text("SELECT set_config('statement_timeout', :timeout_value, true)"),
            {"timeout_value": f"{timeout_ms}ms"},
        )


def _is_timeout(exc: BaseException) -> bool:
    message = str(exc).lower()
    return "timeout" in message or "max_execution_time" in message or "query canceled" in message


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date, time, Decimal, UUID)):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
