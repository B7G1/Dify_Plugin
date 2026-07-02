"""DM8 SQLAlchemy adapter."""

from __future__ import annotations

import os
import ctypes
from pathlib import Path
from typing import Any

from sqlalchemy import URL, text

from utils.adapters.base import DatabaseAdapter


_DM_DLL_HANDLES: list[Any] = []
_DM_RUNTIME_READY = False
_DM_LOCAL_CODE_UTF8 = 1


def _ensure_dm_runtime() -> None:
    global _DM_RUNTIME_READY
    if _DM_RUNTIME_READY:
        return

    if os.name != "nt":
        bundled_library = Path(__file__).resolve().parents[2] / "lib" / "dm" / "libdmdpi.so"
        if not bundled_library.is_file():
            raise RuntimeError(f"Bundled DM8 client library is missing: {bundled_library}")
        ctypes.CDLL(str(bundled_library), mode=ctypes.RTLD_GLOBAL)
        _DM_RUNTIME_READY = True
        return

    dm_home = Path(os.environ.get("DM_HOME", r"C:\dmdbms"))
    os.environ.setdefault("DM_HOME", str(dm_home))

    runtime_dirs = [
        str(dm_home / "drivers" / "dpi" / "dependencies"),
        str(dm_home / "drivers" / "dpi"),
        str(dm_home / "bin" / "dependencies"),
        str(dm_home / "bin" / "external_crypto_libs"),
        str(dm_home / "bin"),
    ]

    path_entries = [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry]
    for runtime_dir in reversed(runtime_dirs):
        if runtime_dir not in path_entries:
            path_entries.insert(0, runtime_dir)
    os.environ["PATH"] = os.pathsep.join(path_entries)

    add_dll_directory = getattr(os, "add_dll_directory", None)
    if add_dll_directory is not None:
        for runtime_dir in runtime_dirs:
            try:
                _DM_DLL_HANDLES.append(add_dll_directory(runtime_dir))
            except OSError:
                continue

    _DM_RUNTIME_READY = True


class DMAdapter(DatabaseAdapter):
    def build_database_url(self, config: dict[str, Any]) -> URL:
        _ensure_dm_runtime()
        return URL.create(
            "dm",
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )

    def build_connect_args(self, config: dict[str, Any]) -> dict[str, Any]:
        _ensure_dm_runtime()
        connect_args: dict[str, Any] = {
            "connection_timeout": config["connection_timeout"],
            "local_code": _DM_LOCAL_CODE_UTF8,
        }
        if config.get("schema"):
            connect_args["schema"] = config["schema"]
        return connect_args

    def configure_session(self, connection: Any, config: dict[str, Any], timeout: int) -> None:
        del timeout
        schema = config.get("schema")
        if schema:
            quoted_schema = schema.replace('"', '""')
            connection.execute(text(f'SET SCHEMA "{quoted_schema}"'))


Adapter = DMAdapter
