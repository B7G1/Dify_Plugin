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


OLD_PROVIDERS, OLD_TOOL = {"db_query", "junjiem/db_query/db_query"}, "sql_query"
NEW_PROVIDER, NEW_TOOL = "li_zijun/db_query_extended/db_query_extended", "legacy_database_query"
NEW_PLUGIN_ID = "li_zijun/db_query_extended"
NEW_PLUGIN_IDENTIFIER = "li_zijun/db_query_extended:0.1.3@da9482ea6ef228311cac1e8f33efa59464c3aa25dbebf55da9c9c642a7a6078f"
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
    if isinstance(document, dict) and isinstance(document.get("workflow"), dict) and isinstance(document["workflow"].get("graph"), dict) and isinstance(document["workflow"]["graph"].get("nodes"), list):
        return document["workflow"]["graph"]["nodes"]
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
        if provider not in OLD_PROVIDERS or tool != OLD_TOOL:
            continue
        inputs = data.get("inputs", data.get("params"))
        if not isinstance(inputs, dict) or any(name not in inputs for name in PARAMETERS):
            raise ValueError(f"BLOCKED: legacy node {node.get('id', '<unnamed>')} lacks the frozen nine inputs.")
        data["provider_id"], data["tool_name"] = NEW_PROVIDER, NEW_TOOL
        for field, value in (("plugin_id", NEW_PLUGIN_ID), ("plugin_unique_identifier", NEW_PLUGIN_IDENTIFIER), ("provider_name", NEW_PROVIDER)):
            if field in data:
                data[field] = value
        changed.append(str(node.get("id", "<unnamed>")))
    rewritten = 0
    json_template_ids: list[str] = []
    json_tool_ids: set[str] = set()
    for node in node_list(updated):
        data = node.get("data") if isinstance(node, dict) else None
        if not isinstance(data, dict):
            continue
        for value in data.get("variables", []) if isinstance(data.get("variables"), list) else []:
            selector = value.get("value_selector") if isinstance(value, dict) else None
            if isinstance(selector, list) and len(selector) == 2 and str(selector[0]) in changed and selector[1] == "json":
                json_tool_ids.add(str(selector[0]))
                selector[1] = "result"
                value["value_type"] = "object"
                if data.get("type") == "template-transform":
                    json_template_ids.append(str(node.get("id")))
                    variable_name = value.get("variable")
                    if isinstance(variable_name, str):
                        data["template"] = "{{ " + variable_name + " | tojson }}"
                rewritten += 1
        for value in data.get("outputs", []) if isinstance(data.get("outputs"), list) else []:
            selector = value.get("value_selector") if isinstance(value, dict) else None
            if isinstance(selector, list) and len(selector) == 2 and str(selector[0]) in changed and selector[1] == "json":
                json_tool_ids.add(str(selector[0]))
                selector[1] = "result"
                value["value_type"] = "object"
                rewritten += 1
    if json_template_ids:
        for node in node_list(updated):
            data = node.get("data") if isinstance(node, dict) else None
            if not isinstance(data, dict) or data.get("type") != "end":
                continue
            for value in data.get("outputs", []) if isinstance(data.get("outputs"), list) else []:
                selector = value.get("value_selector") if isinstance(value, dict) else None
                if isinstance(selector, list) and len(selector) == 2 and str(selector[0]) in changed and selector[1] == "result":
                    selector[:] = [json_template_ids[0], "output"]
                    value["value_type"] = "string"
    for node in node_list(updated):
        data = node.get("data") if isinstance(node, dict) else None
        if not isinstance(data, dict) or str(node.get("id")) not in json_tool_ids:
            continue
        configuration = data.get("tool_configurations")
        if isinstance(configuration, dict) and isinstance(configuration.get("output_format"), dict):
            configuration["output_format"]["value"] = "json"
        parameters = data.get("tool_parameters")
        if isinstance(parameters, dict):
            parameters["output_format"] = {"type": "constant", "value": "json"}
    return updated, {"status": "MIGRATED" if changed else "NOOP", "changed_nodes": changed, "already_migrated_nodes": already, "rewritten_downstream_bindings": rewritten, "json_end_serialized_by_template": bool(json_template_ids), "json_output_format_overrides": sorted(json_tool_ids)}


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
