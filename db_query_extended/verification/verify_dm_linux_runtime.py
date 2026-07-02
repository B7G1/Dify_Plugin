"""Verify that the bundled Linux DM8 client can load the cp312 dmPython wheel."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path


plugin_root = Path(__file__).resolve().parents[1]
library = plugin_root / "lib" / "dm" / "libdmdpi.so"
if os.name == "nt":
    raise SystemExit("This verification must run in the Linux plugin runtime.")
if not library.is_file():
    raise SystemExit(f"Missing bundled library: {library}")

ctypes.CDLL(str(library), mode=ctypes.RTLD_GLOBAL)
import dmPython  # noqa: E402

print(f"PASS dmPython={dmPython.version} library={library}")
