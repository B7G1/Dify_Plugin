"""Stable database adapter contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import URL, text


class DatabaseAdapter(ABC):
    """Encapsulate driver and session differences behind one interface."""

    @abstractmethod
    def build_database_url(self, config: dict[str, Any]) -> URL:
        """Build the SQLAlchemy URL for this database."""

    @abstractmethod
    def build_connect_args(self, config: dict[str, Any]) -> dict[str, Any]:
        """Build DBAPI connection arguments for this database."""

    def build_engine_options(self, config: dict[str, Any]) -> dict[str, Any]:
        """Build SQLAlchemy options shared by the short-lived engine lifecycle."""
        return {
            "pool_pre_ping": bool(config.get("pool_pre_ping", True)),
            "connect_args": self.build_connect_args(config),
        }

    @abstractmethod
    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        """Apply transaction-local or session-level query settings."""

    def execute_query(self, connection: Any, sql: str) -> Any:
        """Execute validated SQL without changing result semantics."""
        return connection.execute(text(sql))
