"""MySQL SQLAlchemy adapter."""

from __future__ import annotations

from typing import Any

from sqlalchemy import URL, text

from utils.adapters.base import DatabaseAdapter


class MySQLAdapter(DatabaseAdapter):
    def build_database_url(self, config: dict[str, Any]) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            database=config["database"],
        )

    def build_connect_args(self, config: dict[str, Any]) -> dict[str, Any]:
        connect_args: dict[str, Any] = {"connect_timeout": config["connection_timeout"]}
        if config.get("charset"):
            connect_args["charset"] = config["charset"]
        return connect_args

    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        connection.execute(
            text("SET SESSION MAX_EXECUTION_TIME = :timeout_ms"),
            {"timeout_ms": timeout * 1000},
        )


Adapter = MySQLAdapter
