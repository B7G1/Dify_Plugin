"""Phase 10 dependency and package readiness audit.

This runner is read-only with respect to plugin artifacts: it never installs,
downloads, builds, deletes, or repackages dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PLUGIN_ROOT.parent
WHEELS = PLUGIN_ROOT / "wheels"

V1_RELEASE_NAME = "db_query_extended-0.1.1-dm8-linux-amd64.difypkg"
V1_RELEASE_SHA256 = "CEE3B0D7D54ECF1171E78739FF01C12D204F9B0CCCF7627D51AFAA69631A142B"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    entries: list[dict[str, Any]] = []
    check(entries, "manifest_version", check_manifest_version)
    check(entries, "runtime_contract", check_runtime_contract)
    check(entries, "requirements_pins", check_requirements_pins)
    check(entries, "v1_runtime_wheels", check_v1_runtime_wheels)
    check(entries, "kingbase_not_prematurely_pinned", check_kingbase_not_pinned)
    check(entries, "v1_release_artifact", check_v1_release_artifact)
    check(entries, "artifact_selection_policy", check_artifact_policy)

    blocked(entries, "kingbase_driver_wheel", "Approved ksycopg2 CPython 3.12 Linux x86_64 wheel is not present in wheels/.")
    blocked(entries, "kingbase_sqlalchemy_dialect", "SQLAlchemy 2.0.51-compatible Kingbase dialect artifact is not present.")
    blocked(entries, "kingbase_native_client", "Required libkci/native client contents and ldd closure are not available.")
    blocked(entries, "kingbase_redistribution", "Vendor driver, dialect, native-library, image, and license redistribution review is incomplete.")
    blocked(entries, "v1_1_release_artifact", "A v1.1 package must not be built until real KingbaseES runtime acceptance passes.")

    summary = {"pass": 0, "fail": 0, "skip": 0, "blocked": 0}
    for item in entries:
        summary[item["status"].lower()] += 1

    report = {
        "suite": "phase10_packaging_readiness",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "v1.1.0-preparation",
        "entries": entries,
        "summary": summary,
        "decision": "BLOCKED" if summary["blocked"] or summary["fail"] else "READY",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if summary["fail"] else 0


def check(entries: list[dict[str, Any]], name: str, function: Any) -> None:
    try:
        message = function()
        entries.append(item(name, "PASS", message))
    except Exception as exc:  # noqa: BLE001 - normalized audit result
        entries.append(item(name, "FAIL", f"{type(exc).__name__}: {exc}"))


def blocked(entries: list[dict[str, Any]], name: str, message: str) -> None:
    entries.append(item(name, "BLOCKED", message))


def check_manifest_version() -> str:
    manifest = read_manifest()
    assert manifest["version"] == "0.1.1"
    assert manifest["meta"]["version"] == "0.1.1"
    return "Manifest remains at accepted plugin version 0.1.1; no premature v1.1 claim."


def check_runtime_contract() -> str:
    manifest = read_manifest()
    runner = manifest["meta"]["runner"]
    assert runner["language"] == "python"
    assert str(runner["version"]) == "3.12"
    assert manifest["meta"]["arch"] == ["amd64"]
    return "Runtime contract is Python 3.12 / amd64."


def check_requirements_pins() -> str:
    requirements = (PLUGIN_ROOT / "requirements.txt").read_text(encoding="utf-8")
    expected = (
        "dify_plugin==0.6.2",
        "SQLAlchemy==2.0.51",
        "PyMySQL==1.2.0",
        "psycopg2-binary==2.9.12",
        "dmPython==2.5.32",
        "dmSQLAlchemy==2.0.12",
    )
    missing = [requirement for requirement in expected if requirement not in requirements]
    assert not missing, f"missing pins: {missing}"
    return "All accepted v1 dependency pins remain present."


def check_v1_runtime_wheels() -> str:
    names = [path.name.lower() for path in WHEELS.iterdir() if path.is_file()]
    patterns = {
        "dify_plugin": ("dify_plugin-0.6.2-py3-none-any.whl",),
        "SQLAlchemy": ("sqlalchemy-2.0.51-cp312", "manylinux"),
        "PyMySQL": ("pymysql-1.2.0-py3-none-any.whl",),
        "psycopg2-binary": ("psycopg2_binary-2.9.12-cp312", "manylinux"),
        "dmPython": ("dmpython-2.5.32-cp312-cp312-linux_x86_64.whl",),
        "dmSQLAlchemy": ("dmsqlalchemy-2.0.12-py3-none-any.whl",),
    }
    missing: list[str] = []
    for package, tokens in patterns.items():
        if not any(all(token.lower() in name for token in tokens) for name in names):
            missing.append(package)
    assert not missing, f"no Python 3.12 Linux amd64-compatible wheel found for: {missing}"
    return "Accepted v1 direct dependencies have compatible offline runtime wheels."


def check_kingbase_not_pinned() -> str:
    requirements = (PLUGIN_ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "ksycopg" not in requirements
    assert "kingbase" not in requirements
    return "Unapproved Kingbase driver/dialect is not declared as a release dependency."


def check_v1_release_artifact() -> str:
    artifact = WORKSPACE_ROOT / V1_RELEASE_NAME
    assert artifact.is_file(), f"missing {V1_RELEASE_NAME}"
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest().upper()
    assert digest == V1_RELEASE_SHA256
    return f"Canonical v1 artifact exists with accepted SHA-256 {digest}."


def check_artifact_policy() -> str:
    packages = sorted(WORKSPACE_ROOT.rglob("*.difypkg"))
    assert any(path.name == V1_RELEASE_NAME for path in packages)
    noncanonical = [str(path.relative_to(WORKSPACE_ROOT)) for path in packages if path.name != V1_RELEASE_NAME]
    return (
        "Only the named 0.1.1 Linux amd64 package is canonical; "
        f"{len(noncanonical)} other package artifact(s) remain historical/test/development and must not be selected for release."
    )


def read_manifest() -> dict[str, Any]:
    return yaml.safe_load((PLUGIN_ROOT / "manifest.yaml").read_text(encoding="utf-8"))


def item(name: str, status: str, message: str) -> dict[str, str]:
    return {"case": name, "status": status, "message": message}


if __name__ == "__main__":
    raise SystemExit(main())

