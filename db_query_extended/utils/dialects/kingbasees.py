"""Scoped SQLAlchemy dialect for the Kingbase-maintained ksycopg2 driver."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.dialects import registry
from sqlalchemy.dialects.postgresql.base import PGDialect


DIALECT_NAME = "kingbasees.ksycopg2"
SQLALCHEMY_DRIVER_NAME = "kingbasees+ksycopg2"
_VERSION_PATTERN = re.compile(
    r"^KingbaseES\s+V(?P<major>\d{3})R(?P<release>\d{3})C(?P<component>\d{3})(?:B\d{4})?(?:\s+.*)?$"
)


def parse_server_version(value: str) -> tuple[int, int, int]:
    """Parse the verified VmmmRrrrCccc KingbaseES version format."""
    match = _VERSION_PATTERN.fullmatch(value.strip())
    if not match:
        raise AssertionError(f"Unsupported KingbaseES server version string: {value!r}")
    return tuple(int(match.group(name)) for name in ("major", "release", "component"))


class KingbaseESDialect_ksycopg2(PGDialect):
    name = "kingbasees"
    driver = "ksycopg2"
    default_paramstyle = "pyformat"
    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls) -> Any:
        import ksycopg2

        return ksycopg2

    def create_connect_args(self, url: Any) -> tuple[list[Any], dict[str, Any]]:
        return [], url.translate_connect_args(username="user")

    def _get_server_version_info(self, connection: Any) -> tuple[int, int, int]:
        return parse_server_version(connection.exec_driver_sql("select pg_catalog.version()").scalar())

    def get_isolation_level_values(self, dbapi_connection: Any) -> tuple[str, ...]:
        return ("AUTOCOMMIT", *super().get_isolation_level_values(dbapi_connection))

    def set_isolation_level(self, dbapi_connection: Any, level: str) -> None:
        dbapi_connection.autocommit = level == "AUTOCOMMIT"
        if level != "AUTOCOMMIT":
            super().set_isolation_level(dbapi_connection, level)

    def is_disconnect(self, error: BaseException, connection: Any, cursor: Any) -> bool:
        del cursor
        if not isinstance(error, self.dbapi.Error):
            return False
        if getattr(connection, "closed", False):
            return True
        message = str(error).partition("\n")[0].lower()
        return any(
            marker in message
            for marker in (
                "terminating connection",
                "closed the connection",
                "connection not open",
                "connection already closed",
                "could not receive data from server",
                "could not send data to server",
            )
        )


def register_kingbasees_dialect() -> None:
    """Idempotently register only the plugin-owned KingbaseES namespace."""
    registry.register(DIALECT_NAME, __name__, "KingbaseESDialect_ksycopg2")
