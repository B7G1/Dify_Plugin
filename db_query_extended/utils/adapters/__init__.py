"""Database adapter discovery for db_query_extended."""

from __future__ import annotations

from importlib import import_module

from utils.adapters.base import DatabaseAdapter
from utils.errors import ConnectionFailedError


def get_database_adapter(database_type: str) -> DatabaseAdapter:
    """Load the adapter whose module name matches ``database_type``."""
    try:
        module = import_module(f"utils.adapters.{database_type}")
        adapter_class = getattr(module, "Adapter")
        adapter = adapter_class()
    except (ImportError, AttributeError, TypeError) as exc:
        raise ConnectionFailedError("The selected database type is not configured.") from exc

    if not isinstance(adapter, DatabaseAdapter):
        raise ConnectionFailedError("The selected database type is not configured.")
    return adapter
