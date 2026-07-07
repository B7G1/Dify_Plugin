"""KingbaseES driver and SQLAlchemy dialect availability gate."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from sqlalchemy.dialects import registry
from sqlalchemy.exc import NoSuchModuleError

from utils.errors import ConnectionFailedError


DRIVER_MODULE = "ksycopg2"
DIALECT_NAME = "kingbase.ksycopg2"
SQLALCHEMY_DRIVER_NAME = "kingbase+ksycopg2"


def require_kingbase_runtime() -> dict[str, Any]:
    """Require the vendor DB-API driver and Kingbase SQLAlchemy dialect.

    This function never installs, downloads, patches, or registers dependencies.
    Vendor artifacts must already exist in the plugin's isolated runtime.
    """
    try:
        driver = import_module(DRIVER_MODULE)
    except (ImportError, OSError) as exc:
        raise ConnectionFailedError(
            "KingbaseES Preview runtime is not release-accepted on this installation. "
            "Approved Linux amd64 ksycopg2 driver, SQLAlchemy dialect, and native client artifacts are required."
        ) from exc

    try:
        dialect = registry.load(DIALECT_NAME)
    except (ImportError, NoSuchModuleError, OSError) as exc:
        raise ConnectionFailedError(
            "KingbaseES SQLAlchemy dialect is unavailable or incompatible with the plugin runtime."
        ) from exc

    return {
        "driver_module": DRIVER_MODULE,
        "driver_version": str(getattr(driver, "__version__", "unknown")),
        "dialect_name": DIALECT_NAME,
        "dialect": dialect,
    }

