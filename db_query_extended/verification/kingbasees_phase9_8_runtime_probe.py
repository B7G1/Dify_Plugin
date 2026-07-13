"""Inspect the installed candidate runtime without a source-tree overlay."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--expected-checksum", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.installed_root.resolve()
    sys.path.insert(0, str(root))

    import ksycopg2
    import psycopg2
    import sqlalchemy
    from sqlalchemy.dialects import registry
    from utils.adapters import dm, kingbasees, mysql, postgresql, sqlserver
    from utils.dialects.kingbasees import register_kingbasees_dialect

    psycopg2_identity = id(psycopg2)
    postgresql_dialect_identity = id(registry.load("postgresql.psycopg2"))
    register_kingbasees_dialect()
    libkci = next(Path(ksycopg2.__file__).parent.glob("libkci.so.5"))
    provider = yaml.safe_load((root / "provider" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    tool = yaml.safe_load((root / "tools" / "db_query_extended.yaml").read_text(encoding="utf-8"))
    options = [item["value"] for item in provider["credentials_for_provider"]["database_type"]["options"]]
    module_paths = {
        "ksycopg2": ksycopg2.__file__,
        "sqlalchemy": sqlalchemy.__file__,
        "kingbasees_adapter": kingbasees.__file__,
        "provider_yaml": str(root / "provider" / "db_query_extended.yaml"),
        "tool_yaml": str(root / "tools" / "db_query_extended.yaml"),
        "libkci": str(libkci),
    }
    checks = {
        "installed_checksum_path": args.expected_checksum in str(root),
        "ksycopg2_installed_path": str(root) in str(ksycopg2.__file__),
        "libkci_installed_path": str(root) in str(libkci),
        "sqlalchemy_2_0_51": sqlalchemy.__version__ == "2.0.51",
        "no_phase95_overlay": all("/tmp/kingbasees_phase95" not in str(path) for path in module_paths.values()),
        "pythonpath_has_no_probe_overlay": "/tmp/kingbasees_phase9" not in os.getenv("PYTHONPATH", ""),
        "provider_schema": options == ["mysql", "postgresql", "dm", "sqlserver", "kingbasees"],
        "tool_schema": tool["identity"]["name"] == "db_query_extended",
        "adapter_import_smoke": all((mysql, postgresql, dm, sqlserver, kingbasees)),
        "psycopg2_identity": id(psycopg2) == psycopg2_identity,
        "postgresql_dialect_identity": id(registry.load("postgresql.psycopg2")) == postgresql_dialect_identity,
    }
    report = {
        "suite": "kingbasees_phase9_8_installed_runtime",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "installed_root": str(root),
        "installed_checksum": args.expected_checksum,
        "python": sys.version,
        "ksycopg2_version": ksycopg2.__version__,
        "sqlalchemy_version": sqlalchemy.__version__,
        "provider_options": options,
        "module_paths": module_paths,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "ksycopg2": ksycopg2.__file__}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
