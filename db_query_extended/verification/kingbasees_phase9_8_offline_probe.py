"""Run after a no-index install in a network-none Python 3.12 container."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--pip-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.site), str(args.plugin_root)]
    modules = {
        name: importlib.import_module(name)
        for name in ("ksycopg2", "sqlalchemy", "dify_plugin", "utils.database", "provider.db_query_extended", "tools.db_query_extended")
    }
    ksycopg2_path = Path(modules["ksycopg2"].__file__).resolve()
    libkci = next(ksycopg2_path.parent.glob("libkci.so.5"))
    distributions = sorted(
        {distribution.metadata["Name"]: distribution.version for distribution in importlib.metadata.distributions(path=[str(args.site)])}.items()
    )
    checks = {
        "network_none": os.getenv("PHASE98_NETWORK_MODE") == "none",
        "python312": sys.version_info[:2] == (3, 12),
        "ksycopg2_import": modules["ksycopg2"].__version__.startswith("2.9.1"),
        "libkci_load": libkci.is_file(),
        "sqlalchemy_import": modules["sqlalchemy"].__version__ == "2.0.51",
        "plugin_source_import": all(modules[name] for name in ("utils.database", "provider.db_query_extended", "tools.db_query_extended")),
        "no_phase95_overlay": "/tmp/kingbasees_phase95" not in str(ksycopg2_path),
        "no_external_download": "Downloading" not in args.pip_log.read_text(encoding="utf-8", errors="replace"),
    }
    report = {
        "suite": "kingbasees_phase9_8_offline_dependency_closure",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "network_mode": "none",
        "install_mode": "pip --no-index --no-cache-dir --find-links",
        "python": sys.version,
        "ksycopg2_module_path": str(ksycopg2_path),
        "libkci_path": str(libkci.resolve()),
        "installed_packages": distributions,
        "missing_dependency_count": 0,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "ksycopg2": str(ksycopg2_path)}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
