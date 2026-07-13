"""KingbaseES driver and plugin-owned SQLAlchemy dialect gate."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from sqlalchemy.dialects import registry

from utils.dialects.kingbasees import DIALECT_NAME, register_kingbasees_dialect
from utils.errors import ConnectionFailedError


DRIVER_MODULE = "ksycopg2"
SQLALCHEMY_DRIVER_NAME = "kingbasees+ksycopg2"


def require_kingbase_runtime() -> dict[str, Any]:
    """Require the vendor DB-API driver and Kingbase SQLAlchemy dialect.

    This function never installs, downloads, or patches dependencies. Vendor
    artifacts must already exist in the plugin's isolated runtime.
    """
    try:
        driver = import_module(DRIVER_MODULE)
    except (ImportError, OSError) as exc:
        raise ConnectionFailedError(
            "KingbaseES Preview runtime is not release-accepted on this installation. "
            "Approved Linux amd64 ksycopg2 driver, SQLAlchemy dialect, and native client artifacts are required."
        ) from exc

    register_kingbasees_dialect()
    dialect = registry.load(DIALECT_NAME)

    return {
        "driver_module": DRIVER_MODULE,
        "driver_version": str(getattr(driver, "__version__", "unknown")),
        "dialect_name": DIALECT_NAME,
        "dialect": dialect,
    }
