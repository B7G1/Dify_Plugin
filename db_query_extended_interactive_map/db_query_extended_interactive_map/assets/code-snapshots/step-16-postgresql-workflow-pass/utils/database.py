"""SQLAlchemy connection and query helpers for supported databases.

The current plugin runtime opens one short-lived SQLAlchemy engine per tool
invocation and disposes it after the query or credential check completes.
``NullPool`` is intentional here: the Dify plugin process should not retain
driver connections across invocations until a real pooled lifecycle is designed.
"""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError, ProgrammingError, TimeoutError as SATimeoutError
from sqlalchemy.pool import NullPool

from utils.errors import ConnectionFailedError, QueryTimeoutError, SqlExecutionError
from utils.formatter import format_sqlalchemy_result


logger = logging.getLogger(__name__)


def create_database_engine(config: dict[str, Any]) -> Engine:
    """Create a short-lived SQLAlchemy engine without logging credentials.

    Implemented today:
    - MySQL URL: ``mysql+pymysql://user:***@host:port/database``
    - PostgreSQL URL: ``postgresql+psycopg2://user:***@host:port/database``
    - Driver connect timeout via ``connect_args``
    - PostgreSQL ``sslmode`` and optional MySQL ``charset``
    - ``pool_pre_ping=True`` with ``NullPool``

    Reserved for a future pooled lifecycle:
    - ``pool_timeout`` and ``pool_recycle`` are not applied while ``NullPool``
      is active, because there is no retained pool to time out or recycle.
    """
    return create_engine(
        build_database_url(config),
        poolclass=NullPool,
        **build_engine_options(config),
    )


def build_database_url(config: dict[str, Any]) -> URL:
    """Build the SQLAlchemy URL for a supported database type."""
    database_type = config["database_type"]
    if database_type == "mysql":
        return URL.create(
            "mysql+pymysql", username=config["username"], password=config["password"],
            host=config["host"], port=config["port"], database=config["database"],
        )
    elif database_type == "postgresql":
        return URL.create(
            "postgresql+psycopg2", username=config["username"], password=config["password"],
            host=config["host"], port=config["port"], database=config["database"],
        )

    raise ConnectionFailedError("The selected database type is not configured.")


def build_connect_args(config: dict[str, Any]) -> dict[str, Any]:
    """Build DBAPI connect arguments for the selected driver."""
    database_type = config["database_type"]
    connect_args: dict[str, Any] = {"connect_timeout": config["connection_timeout"]}

    if database_type == "mysql":
        if config.get("charset"):
            connect_args["charset"] = config["charset"]
        return connect_args

    if database_type == "postgresql":
        connect_args["sslmode"] = config["ssl_mode"]
        return connect_args

    raise ConnectionFailedError("The selected database type is not configured.")


def build_engine_options(config: dict[str, Any]) -> dict[str, Any]:
    """Return SQLAlchemy engine options supported by the current lifecycle."""
    return {
        "pool_pre_ping": bool(config.get("pool_pre_ping", True)),
        "connect_args": build_connect_args(config),
    }


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
    started = perf_counter()
    try:
        with engine.connect() as connection:
            with connection.begin():
                _apply_query_timeout(connection, config["database_type"], timeout)
                if config["schema"] and config["database_type"] == "postgresql":
                    connection.execute(
                        text("SELECT set_config('search_path', :schema, true)"),
                        {"schema": config["schema"]},
                    )
                result = format_sqlalchemy_result(connection.execute(text(sql)), max_rows=max_rows)
        result["execution_time_ms"] = int((perf_counter() - started) * 1000)
        return result
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

