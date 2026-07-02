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

from utils.adapters import get_database_adapter
from utils.errors import ConnectionFailedError, QueryTimeoutError, SqlExecutionError
from utils.formatter import format_sqlalchemy_result


logger = logging.getLogger(__name__)


def create_database_engine(config: dict[str, Any]) -> Engine:
    """Create a short-lived SQLAlchemy engine without logging credentials.

    Implemented today:
    - MySQL URL: ``mysql+pymysql://user:***@host:port/database``
    - PostgreSQL URL: ``postgresql+psycopg2://user:***@host:port/database``
    - DM8 URL: ``dm://user:***@host:port``
    - Driver connect timeout via ``connect_args``
    - PostgreSQL ``sslmode``, optional MySQL ``charset``, and DM8 ``schema``
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
    return get_database_adapter(config["database_type"]).build_database_url(config)


def build_connect_args(config: dict[str, Any]) -> dict[str, Any]:
    """Build DBAPI connect arguments for the selected driver."""
    return get_database_adapter(config["database_type"]).build_connect_args(config)


def build_engine_options(config: dict[str, Any]) -> dict[str, Any]:
    """Return SQLAlchemy engine options supported by the current lifecycle."""
    return get_database_adapter(config["database_type"]).build_engine_options(config)


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
    adapter = get_database_adapter(config["database_type"])
    started = perf_counter()
    try:
        with engine.connect() as connection:
            with connection.begin():
                adapter.configure_session(connection, config, timeout)
                result = format_sqlalchemy_result(adapter.execute_query(connection, sql), max_rows=max_rows)
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


def _is_timeout(exc: BaseException) -> bool:
    message = str(exc).lower()
    return "timeout" in message or "max_execution_time" in message or "query canceled" in message
