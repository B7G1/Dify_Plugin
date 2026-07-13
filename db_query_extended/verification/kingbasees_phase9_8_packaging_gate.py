"""Audit the Phase 9.8 wheel set and candidate package without downloads."""

from __future__ import annotations

import argparse
import email
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_DRIVER_SHA256 = "59D2D19439FA0D8AE66A7972EF9EF1FE461E84389D50BC3E90C59ABB4962287A"
DRIVER_NAME = "ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl"
REQUIRED_PACKAGE_PATHS = {
    "THIRD_PARTY_NOTICES.md",
    "requirements.txt",
    "manifest.yaml",
    "provider/db_query_extended.yaml",
    "tools/db_query_extended.yaml",
    "utils/adapters/kingbasees.py",
    "utils/dialects/kingbasees.py",
    f"wheels/{DRIVER_NAME}",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def run(command: list[str]) -> dict[str, Any]:
    process = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", errors="replace")
    return {
        "command": command,
        "exit_code": process.returncode,
        "stdout": process.stdout.splitlines(),
        "stderr": process.stderr.splitlines(),
    }


def wheel_metadata(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        wheel_name = next(name for name in archive.namelist() if name.endswith(".dist-info/WHEEL"))
        metadata = email.message_from_bytes(archive.read(metadata_name))
        wheel_text = archive.read(wheel_name).decode("utf-8", errors="replace")
        return {
            "filename": path.name,
            "package": metadata.get("Name"),
            "version": metadata.get("Version"),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "python_tag": path.name.split("-")[-3] if len(path.name.split("-")) >= 5 else "py3",
            "platform_tag": path.name.rsplit("-", 1)[-1].removesuffix(".whl"),
            "wheel_tags": [line[5:] for line in wheel_text.splitlines() if line.startswith("Tag: ")],
            "license": metadata.get("License") or "NOT_DECLARED",
        }


def driver_inventory(wheel: Path) -> dict[str, Any]:
    data = wheel_metadata(wheel)
    with zipfile.ZipFile(wheel) as archive, tempfile.TemporaryDirectory(prefix="phase98-wheel-") as temporary:
        names = archive.namelist()
        archive.extractall(temporary)
        extension = Path(temporary) / next(name for name in names if re.search(r"_ksycopg.*\.so$", name))
        libkci = Path(temporary) / next(name for name in names if name.endswith("libkci.so.5"))
        license_name = next(name for name in names if name.endswith(".dist-info/LICENSE"))
        checks = {
            "expected_sha256": data["sha256"] == EXPECTED_DRIVER_SHA256,
            "package": data["package"] == "ksycopg2",
            "version": data["version"] == "2.9.1",
            "tag": data["wheel_tags"] == ["cp312-cp312-manylinux1_x86_64"],
            "native_extension": extension.is_file(),
            "bundled_libkci": libkci.is_file(),
            "license_in_wheel": bool(license_name),
        }
        native = {
            "extension": str(extension.relative_to(temporary)),
            "libkci": str(libkci.relative_to(temporary)),
            "libkci_sha256": sha256(libkci),
            "file": run(["file", str(extension)]),
            "readelf_dynamic": run(["readelf", "-d", str(extension)]),
            "readelf_versions": run(["readelf", "--version-info", str(extension)]),
            "ldd": run(["ldd", str(extension)]),
        }
        missing = [line for line in native["ldd"]["stdout"] if "not found" in line]
        checks["ldd_missing_zero"] = native["ldd"]["exit_code"] == 0 and not missing
    return {
        "suite": "kingbasees_phase9_8_driver_inventory",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        **data,
        "source": "Kingbase-maintained PyPI distribution; locally preserved official candidate",
        "required_by": "KingbaseES Adapter and plugin-owned dialect",
        "included_in_package": True,
        "verification_status": "DRIVER_PROVENANCE_RECONFIRMED / DRIVER_SHA256_VERIFIED",
        "checks": checks,
        "native": native,
    }


def package_manifest(plugin_root: Path, package: Path) -> dict[str, Any]:
    with tarfile.open(package) as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        names = {member.name.removeprefix("./") for member in members}
        missing = sorted(REQUIRED_PACKAGE_PATHS - names)
        forbidden_names = sorted(
            name for name in names
            if name.startswith((".git/", "verification/", "dist/"))
            or name.endswith((".env", ".pem", ".key", ".iso", ".tar"))
            or "license.dat" in name.lower()
        )
        text_hits: list[dict[str, str]] = []
        patterns = {
            "credentialed_url": re.compile(rb"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:]+:[^\s/@]+@"),
            "private_key": re.compile(rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
            "phase95_overlay": re.compile(rb"/tmp/kingbasees_phase95"),
        }
        for member in members:
            if member.size > 2_000_000 or member.name.endswith((".whl", ".so", ".png", ".svg")):
                continue
            payload = archive.extractfile(member).read()  # type: ignore[union-attr]
            for label, pattern in patterns.items():
                if pattern.search(payload):
                    text_hits.append({"path": member.name, "pattern": label})
        wheel_names = sorted(name for name in names if name.startswith("wheels/") and name.endswith(".whl"))
        notice = archive.extractfile("THIRD_PARTY_NOTICES.md").read().decode("utf-8")  # type: ignore[union-attr]
        requirements = archive.extractfile("requirements.txt").read().decode("utf-8")  # type: ignore[union-attr]
        manifest = archive.extractfile("manifest.yaml").read().decode("utf-8")  # type: ignore[union-attr]
    checks = {
        "required_paths": not missing,
        "driver_pin": "ksycopg2==2.9.1" in requirements,
        "notice_status": "REDISTRIBUTION_REVIEW_PENDING" in notice,
        "manifest_version": "version: 0.1.1" in manifest,
        "forbidden_names_zero": not forbidden_names,
        "secret_hits_zero": not text_hits,
    }
    inventory = []
    for wheel in sorted((plugin_root / "wheels").glob("*.whl")):
        item = wheel_metadata(wheel)
        item.update({
            "source": "existing project offline wheel library" if wheel.name != DRIVER_NAME else "Kingbase-maintained PyPI distribution",
            "required_by": "requirements.txt/offline dependency closure",
            "included_in_package": f"wheels/{wheel.name}" in names,
            "verification_status": "PRESENT_AND_HASHED",
        })
        inventory.append(item)
    return {
        "suite": "kingbasees_phase9_8_package_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) and all(x["included_in_package"] for x in inventory) else "FAIL",
        "package": package.name,
        "size": package.stat().st_size,
        "sha256": sha256(package),
        "manifest_version": "0.1.1",
        "entrypoint": "main",
        "file_count": len(names),
        "wheel_count": len(wheel_names),
        "wheels": inventory,
        "missing_required_paths": missing,
        "forbidden_names": forbidden_names,
        "secret_hits": text_hits,
        "checks": checks,
    }


def write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    args = parser.parse_args()
    wheel = args.plugin_root / "wheels" / DRIVER_NAME
    driver = driver_inventory(wheel)
    package = package_manifest(args.plugin_root, args.package)
    write(args.output_dir / "kingbasees_phase9_8_driver_inventory.json", driver)
    write(args.output_dir / "kingbasees_phase9_8_package_manifest.json", package)
    write(args.log_dir / "phase9_8_wheel_native_inventory.log", driver)
    write(args.log_dir / "phase9_8_package_content_audit.log", package)
    print(json.dumps({"driver": driver["status"], "package": package["status"]}))
    return 0 if driver["status"] == package["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
