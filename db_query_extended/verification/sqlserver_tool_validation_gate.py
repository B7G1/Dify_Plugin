"""SQL Server optional validation gate through real Dify/plugin-daemon tool path."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROVIDER_ID = "li_zijun/db_query_extended/db_query_extended"
TOOL_NAME = "db_query_extended"
REQUIRED_SQLSERVER_ENV = (
    "SQLSERVER_HOST",
    "SQLSERVER_PORT",
    "SQLSERVER_DATABASE",
    "SQLSERVER_USERNAME",
    "SQLSERVER_PASSWORD",
)
REQUIRED_KEYS = ("columns", "rows", "row_count", "truncated", "max_rows")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default=str(Path(__file__).with_name(".sqlserver_probe.env")))
    parser.add_argument("--output", required=True)
    parser.add_argument("--container", default=os.getenv("DIFY_API_CONTAINER", "dify-api-1"))
    parser.add_argument("--credential-name", default=os.getenv("DIFY_SQLSERVER_CREDENTIAL_NAME", "SQL Server Local Readonly"))
    args = parser.parse_args()

    load_env_file(Path(args.env_file))
    result = run_gate(args.container, args.credential_name)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")
    return 0 if result["verdict"] == "PASS" else 1


def run_gate(container: str, credential_name: str) -> dict[str, Any]:
    report: dict[str, Any] = {
        "phase": "Phase 8.9 - SQL Server verification integration gate",
        "generated_at": utc_now(),
        "verdict": "FAIL",
        "provider": PROVIDER_ID,
        "tool": TOOL_NAME,
        "credential_name": credential_name,
        "connection": sanitized_connection_summary(),
        "provider_credential_validation": {},
        "cases": {},
        "output_structure_check": {},
        "sqlserver_specific_checks": {},
        "secret_hygiene": {
            "password_recorded": False,
            "token_recorded": False,
        },
        "error": None,
    }

    missing = [name for name in REQUIRED_SQLSERVER_ENV if not os.getenv(name)]
    if missing:
        report["verdict"] = "BLOCKED"
        report["error"] = {"type": "MISSING_ENV", "missing_env": missing}
        return report

    config = sqlserver_config_for_dify_container()
    proc = subprocess.run(
        ["docker", "exec", "-i", container, "/app/api/.venv/bin/python", "-"],
        input=inner_script(config, credential_name),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if proc.returncode != 0:
        report["error"] = {
            "type": "DOCKER_EXEC_FAILED",
            "exit_code": proc.returncode,
            "stderr_tail": proc.stderr.splitlines()[-20:],
        }
        return report

    try:
        runtime = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as exc:  # noqa: BLE001
        report["error"] = {
            "type": "RUNTIME_OUTPUT_PARSE_FAILED",
            "message": str(exc),
            "stdout_tail": proc.stdout.splitlines()[-20:],
            "stderr_tail": proc.stderr.splitlines()[-20:],
        }
        return report

    report["provider_credential_validation"] = {
        "credential_found": bool(runtime.get("credential_found")),
        "runtime_validate_credentials": bool(runtime.get("provider_validation_runtime")),
        "credential_name": credential_name,
    }
    report["cases"] = runtime.get("cases", {})
    report["plugin"] = {
        "plugin_unique_identifier": redact_plugin_identifier(runtime.get("plugin_unique_identifier")),
        "database_type_observed": sorted({case.get("database_type") for case in report["cases"].values()}),
    }
    report["output_structure_check"] = {
        "required_keys": list(REQUIRED_KEYS),
        "all_cases_have_required_keys": all(
            all(key in case for key in REQUIRED_KEYS) for case in report["cases"].values()
        ),
    }
    report["sqlserver_specific_checks"] = {
        "database_type_sqlserver": report["plugin"]["database_type_observed"] == ["sqlserver"],
        "select_1_pass": case_success(report, "select_1"),
        "top_query_pass": case_success(report, "top_5") and report["cases"]["top_5"].get("row_count") == 5,
        "unicode_fixture_read_pass": case_success(report, "unicode_fixture_read")
        and report["cases"]["unicode_fixture_read"].get("row_count") == 3,
        "schema_qualified_read_pass": case_success(report, "schema_qualified_read")
        and report["cases"]["schema_qualified_read"].get("rows", [{}])[0].get("log_count") == 3,
    }

    checks = [
        report["provider_credential_validation"]["credential_found"],
        report["provider_credential_validation"]["runtime_validate_credentials"],
        report["output_structure_check"]["all_cases_have_required_keys"],
        *report["sqlserver_specific_checks"].values(),
    ]
    report["verdict"] = "PASS" if all(checks) else "FAIL"
    return report


def inner_script(config: dict[str, Any], credential_name: str) -> str:
    return textwrap.dedent(
        f"""
        from app_factory import create_app
        from core.plugin.impl.tool import PluginToolManager
        from core.tools.entities.tool_entities import ToolProviderType
        from core.tools.tool_manager import ToolManager
        from extensions.ext_database import db
        from models.tools import BuiltinToolProvider
        import json

        config = {json.dumps(config, ensure_ascii=False)}
        credential_name = {json.dumps(credential_name)}
        provider_id = {json.dumps(PROVIDER_ID)}
        tool_name = {json.dumps(TOOL_NAME)}

        app = create_app()
        with app.app_context():
            row = (
                db.session.query(BuiltinToolProvider)
                .filter(BuiltinToolProvider.provider == provider_id)
                .filter(BuiltinToolProvider.name == credential_name)
                .first()
            )
            out = {{"credential_found": bool(row), "cases": {{}}}}
            if not row:
                print(json.dumps(out, ensure_ascii=False))
                raise SystemExit(0)

            manager = PluginToolManager()
            tenant_id = str(row.tenant_id)
            user_id = str(row.user_id)
            credential_id = str(row.id)
            provider_entity = manager.fetch_tool_provider(tenant_id, provider_id)
            out.update({{
                "tenant_id": tenant_id,
                "user_id": user_id,
                "credential_id": credential_id,
                "plugin_unique_identifier": provider_entity.plugin_unique_identifier,
                "provider_validation_runtime": manager.validate_provider_credentials(
                    tenant_id, user_id, provider_id, config
                ),
            }})
            tool = ToolManager.get_tool_runtime(
                provider_type=ToolProviderType.BUILT_IN,
                provider_id=provider_id,
                tool_name=tool_name,
                tenant_id=tenant_id,
                credential_id=credential_id,
            )
            cases = {{
                "select_1": "SELECT 1 AS probe_value",
                "top_5": "SELECT TOP 5 [id], [username], [display_name], [department], [created_at] FROM [plugin_test].[plugin_test_users] ORDER BY [id]",
                "unicode_fixture_read": "SELECT TOP 3 [id], [event_type], [message] FROM [plugin_test].[plugin_test_logs] ORDER BY [id]",
                "schema_qualified_read": "SELECT COUNT(*) AS [log_count] FROM [plugin_test].[plugin_test_logs]",
            }}
            for name, sql in cases.items():
                messages = list(tool.invoke(
                    user_id=user_id,
                    tool_parameters={{
                        "sql": sql,
                        "max_rows": 10,
                        "timeout_seconds": 30,
                        "readonly": True,
                        "output_format": "json",
                    }},
                ))
                message = messages[0].model_dump(mode="json") if messages else None
                if message and message.get("type") == "json":
                    out["cases"][name] = message["message"]["json_object"]
                else:
                    out["cases"][name] = {{"success": False, "error": "missing_json_message"}}
            print(json.dumps(out, ensure_ascii=False))
        """
    ).strip()


def sqlserver_config_for_dify_container() -> dict[str, Any]:
    host = os.getenv("SQLSERVER_HOST", "")
    if host in {"127.0.0.1", "localhost"}:
        host = os.getenv("SQLSERVER_DIFY_HOST", "host.docker.internal")
    return {
        "database_type": "sqlserver",
        "host": host,
        "port": os.getenv("SQLSERVER_PORT", "1433"),
        "username": os.getenv("SQLSERVER_USERNAME", ""),
        "password": os.getenv("SQLSERVER_PASSWORD", ""),
        "database": os.getenv("SQLSERVER_DATABASE", ""),
        "schema": os.getenv("SQLSERVER_SCHEMA", "plugin_test"),
        "connection_timeout": os.getenv("SQLSERVER_CONNECT_TIMEOUT", "5"),
        "ssl_mode": "disable",
    }


def sanitized_connection_summary() -> dict[str, Any]:
    config = sqlserver_config_for_dify_container()
    return {
        "database_type": "sqlserver",
        "host": config["host"],
        "port": config["port"],
        "database": config["database"],
        "schema": config["schema"],
        "username": config["username"],
        "password_recorded": False,
    }


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def case_success(report: dict[str, Any], name: str) -> bool:
    return bool(report["cases"].get(name, {}).get("success"))


def redact_plugin_identifier(identifier: str | None) -> str | None:
    if not identifier or "@" not in identifier:
        return identifier
    prefix, _checksum = identifier.rsplit("@", 1)
    return f"{prefix}@<redacted>"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    sys.exit(main())
