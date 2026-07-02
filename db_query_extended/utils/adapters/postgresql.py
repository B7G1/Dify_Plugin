"""PostgreSQL SQLAlchemy adapter."""

from __future__ import annotations

from typing import Any

from sqlalchemy import URL, text

from utils.adapters.base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    def build_database_url(self, config: dict[str, Any]) -> URL:
        return URL.create(
            "postgresql+psycopg2",
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            database=config["database"],
        )

    def build_connect_args(self, config: dict[str, Any]) -> dict[str, Any]:
        return {
            "connect_timeout": config["connection_timeout"],
            "sslmode": config["ssl_mode"],
        }

    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        timeout_ms = timeout * 1000
        connection.execute(
            text("SELECT set_config('statement_timeout', :timeout_value, true)"),
            {"timeout_value": f"{timeout_ms}ms"},
        )
        if config["schema"]:
            connection.execute(
                text("SELECT set_config('search_path', :schema, true)"),
                {"schema": config["schema"]},
            )


Adapter = PostgreSQLAdapter
