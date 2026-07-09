"""SQL Server SQLAlchemy adapter."""

from __future__ import annotations

from typing import Any

from sqlalchemy import URL

from utils.adapters.base import DatabaseAdapter


class SQLServerAdapter(DatabaseAdapter):
    def build_database_url(self, config: dict[str, Any]) -> URL:
        return URL.create(
            "mssql+pymssql",
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            database=config["database"],
        )

    def build_connect_args(self, config: dict[str, Any]) -> dict[str, Any]:
        timeout = config["connection_timeout"]
        return {"login_timeout": timeout, "timeout": timeout}

    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        del connection, config, timeout


Adapter = SQLServerAdapter
