"""Safely migrate the frozen original Tool identity in a Workflow DSL file."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


OLD_PROVIDER, OLD_TOOL = "db_query", "sql_query"
NEW_PROVIDER, NEW_TOOL = "legacy_database_query", "legacy_database_query"
PARAMETERS = ("db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "db_properties", "query_sql", "output_format")


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def dump(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n" if path.suffix.lower() == ".json" else yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")


def node_list(document: Any) -> list[dict[str, Any]]:
    if isinstance(document, dict) and isinstance(document.get("nodes"), list):
        return document["nodes"]
    if isinstance(document, dict) and isinstance(document.get("graph"), dict) and isinstance(document["graph"].get("nodes"), list):
        return document["graph"]["nodes"]
    raise ValueError("BLOCKED: unsupported Workflow DSL; expected nodes or graph.nodes list.")


def migrate(document: Any) -> tuple[Any, dict[str, Any]]:
    updated = copy.deepcopy(document)
    changed: list[str] = []
    already: list[str] = []
    for node in node_list(updated):
        data = node.get("data") if isinstance(node, dict) else None
        if not isinstance(data, dict):
            continue
        provider, tool = data.get("provider_id"), data.get("tool_name")
        if (provider, tool) == (NEW_PROVIDER, NEW_TOOL):
            already.append(str(node.get("id", "<unnamed>")))
            continue
        if (provider, tool) != (OLD_PROVIDER, OLD_TOOL):
            continue
        inputs = data.get("inputs")
        if not isinstance(inputs, dict) or any(name not in inputs for name in PARAMETERS):
            raise ValueError(f"BLOCKED: legacy node {node.get('id', '<unnamed>')} lacks the frozen nine inputs.")
        data["provider_id"], data["tool_name"] = NEW_PROVIDER, NEW_TOOL
        changed.append(str(node.get("id", "<unnamed>")))
    return updated, {"status": "MIGRATED" if changed else "NOOP", "changed_nodes": changed, "already_migrated_nodes": already}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        original = load(args.input)
        migrated, summary = migrate(original)
        summary.update({"input": args.input.name, "output": args.output.name, "dry_run": args.dry_run})
        if not args.dry_run:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            if args.backup:
                args.backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(args.input, args.backup)
            dump(args.output, migrated)
        print(json.dumps(summary, ensure_ascii=False))
        return 0
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
