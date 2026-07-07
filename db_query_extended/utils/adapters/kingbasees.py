"""KingbaseES SQLAlchemy adapter (runtime acceptance pending)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import URL, text

from utils.adapters.base import DatabaseAdapter
from utils.drivers.kingbasees import SQLALCHEMY_DRIVER_NAME, require_kingbase_runtime


class KingbaseESAdapter(DatabaseAdapter):
    """Keep KingbaseES-specific connection and session behavior isolated."""

    def build_database_url(self, config: dict[str, Any]) -> URL:
        return URL.create(
            SQLALCHEMY_DRIVER_NAME,
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

    def build_engine_options(self, config: dict[str, Any]) -> dict[str, Any]:
        require_kingbase_runtime()
        return super().build_engine_options(config)

    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        timeout_ms = timeout * 1000
        connection.execute(
            text("SELECT set_config('statement_timeout', :timeout_value, true)"),
            {"timeout_value": f"{timeout_ms}ms"},
        )
        schema = config.get("schema")
        if schema:
            connection.execute(
                text("SELECT set_config('search_path', :schema, true)"),
                {"schema": schema},
            )


Adapter = KingbaseESAdapter

