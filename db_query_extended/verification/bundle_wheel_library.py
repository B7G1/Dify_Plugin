"""Add a shared library beside a wheel extension and refresh RECORD."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import sys
import zipfile
from pathlib import Path


wheel = Path(sys.argv[1])
library = Path(sys.argv[2])
library_name = library.name

with zipfile.ZipFile(wheel, "r") as source:
    files = {name: source.read(name) for name in source.namelist() if name != library_name}

record_name = next(name for name in files if name.endswith(".dist-info/RECORD"))
library_bytes = library.read_bytes()
files[library_name] = library_bytes

rows: list[list[str]] = []
for name, content in sorted(files.items()):
    if name == record_name:
        continue
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode("ascii")
    rows.append([name, f"sha256={digest}", str(len(content))])
rows.append([record_name, "", ""])
record = io.StringIO(newline="")
csv.writer(record, lineterminator="\n").writerows(rows)
files[record_name] = record.getvalue().encode("utf-8")

temporary = wheel.with_suffix(".tmp")
with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as target:
    for name, content in files.items():
        target.writestr(name, content)
temporary.replace(wheel)
print(f"Bundled {library_name} into {wheel}")
