"""Install a candidate and capture redacted Legacy Tool runtime fixtures.

This runs inside Dify's application worker.  It deliberately uses the public
PluginService/PluginInstaller and ToolManager paths instead of a source overlay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLUGIN_ID = "li_zijun/db_query_extended"
MODERN_PROVIDER = "li_zijun/db_query_extended/db_query_extended"
LEGACY_PROVIDER = MODERN_PROVIDER
MODERN_TOOL = "db_query_extended"
LEGACY_TOOL = "legacy_database_query"
SELECT_ONE_GOLDEN = "|   probe |\n|---------|\n|       1 |"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def model(value: Any) -> Any:
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


class Gate:
    def __init__(self, args: argparse.Namespace):
        from app_factory import create_app

        self.args = args
        self.output_dir = args.output_dir
        self.package = args.package
        self.expected_checksum = args.expected_checksum.lower()
        self.package_sha256 = args.package_sha256.lower()
        self.secrets: list[str] = [value for value in (os.getenv("PHASE10_2_MYSQL_PASSWORD"), os.getenv("PHASE10_2_POSTGRESQL_PASSWORD")) if value]
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.tenant_id = ""
        self.user_id = ""
        self.active_identifier = ""

    def close(self) -> None:
        self.context.pop()

    def safe(self, value: Any) -> Any:
        text = json.dumps(value, ensure_ascii=False, default=str)
        for secret in self.secrets:
            text = text.replace(secret, "***REDACTED***")
        return json.loads(text)

    def context_ids(self) -> tuple[str, str]:
        from extensions.ext_database import db
        from models.tools import BuiltinToolProvider

        row = db.session.query(BuiltinToolProvider).filter(BuiltinToolProvider.provider == MODERN_PROVIDER).first()
        if row is None:
            raise RuntimeError("An existing db_query_extended credential is required to identify the Dify tenant.")
        return str(row.tenant_id), str(row.user_id)

    def plugin_summary(self, plugin: Any) -> dict[str, Any]:
        value = model(plugin)
        return {key: value.get(key) for key in ("plugin_id", "plugin_unique_identifier", "version", "installation_id", "source") if key in value}

    def install_candidate(self) -> dict[str, Any]:
        from core.plugin.entities.plugin import PluginInstallationSource
        from core.plugin.entities.plugin_daemon import PluginDecodeResponse
        from core.plugin.impl.plugin import PluginInstaller
        from services.plugin.plugin_service import PluginService

        def decode_with_daemon_parameter(self: Any, tenant_id: str, plugin_unique_identifier: str) -> Any:
            return self._request_with_plugin_daemon_response(
                "GET",
                f"plugin/{tenant_id}/management/decode/from_identifier",
                PluginDecodeResponse,
                params={"PluginUniqueIdentifier": plugin_unique_identifier},
            )

        PluginInstaller.decode_plugin_from_identifier = decode_with_daemon_parameter
        self.tenant_id, self.user_id = self.context_ids()
        before = [plugin for plugin in PluginService.list(self.tenant_id) if plugin.plugin_id == PLUGIN_ID]
        expected_identifier = f"{PLUGIN_ID}:0.1.1@{self.expected_checksum}"
        active_before = next((plugin for plugin in before if plugin.plugin_unique_identifier == expected_identifier), None)
        if active_before is not None:
            self.active_identifier = expected_identifier
            report = {
                "status": "PASS", "generated_at": utcnow(), "tenant_id_recorded": False,
                "candidate": {"checksum": self.expected_checksum, "package_sha256": self.package_sha256},
                "install_status": "already_active", "upgrade_status": "not_required",
                "before": [self.plugin_summary(item) for item in before], "after": [self.plugin_summary(item) for item in before],
                "active_identifier": self.active_identifier,
            }
            dump(self.output_dir / "phase10_2_installation.json", self.safe(report))
            return report
        upload = PluginService.upload_pkg(self.tenant_id, self.package.read_bytes())
        identifier = upload.unique_identifier
        if not identifier.endswith("@" + self.expected_checksum):
            raise AssertionError("Candidate upload checksum does not match the recorded Dify checksum.")
        task = PluginService.install_from_local_pkg(self.tenant_id, [identifier])
        install_last = self.wait_task(PluginService, task)
        after = [plugin for plugin in PluginService.list(self.tenant_id) if plugin.plugin_id == PLUGIN_ID]
        active = next((plugin for plugin in after if plugin.plugin_unique_identifier == identifier), None)
        upgrade_last = None
        if active is None and before:
            upgrade = PluginInstaller().upgrade_plugin(
                self.tenant_id, before[0].plugin_unique_identifier, identifier,
                PluginInstallationSource.Package, {"plugin_unique_identifier": identifier},
            )
            upgrade_last = self.wait_task(PluginService, upgrade)
            after = [plugin for plugin in PluginService.list(self.tenant_id) if plugin.plugin_id == PLUGIN_ID]
            active = next((plugin for plugin in after if plugin.plugin_unique_identifier == identifier), None)
        if active is None:
            raise AssertionError("Candidate was not activated for the tenant after install/upgrade.")
        self.active_identifier = identifier
        report = {
            "status": "PASS",
            "generated_at": utcnow(),
            "tenant_id_recorded": False,
            "candidate": {"checksum": self.expected_checksum, "package_sha256": self.package_sha256},
            "decode_parameter_compatibility": "PluginUniqueIdentifier",
            "before": [self.plugin_summary(item) for item in before],
            "after": [self.plugin_summary(item) for item in after],
            "install_status": str(getattr(install_last, "status", "")),
            "upgrade_status": None if upgrade_last is None else str(getattr(upgrade_last, "status", "")),
            "active_identifier": self.active_identifier,
        }
        dump(self.output_dir / "phase10_2_installation.json", self.safe(report))
        return report

    def wait_task(self, service: Any, task: Any) -> Any:
        task_id = str(getattr(task, "id", None) or getattr(task, "task_id", None) or model(task).get("id"))
        last = None
        for _ in range(90):
            last = service.fetch_install_task(self.tenant_id, task_id)
            if str(getattr(last, "status", "")).lower() in {"success", "succeeded", "failed", "error"}:
                break
            time.sleep(2)
        if str(getattr(last, "status", "")).lower() not in {"success", "succeeded"}:
            raise RuntimeError("Dify package task did not succeed.")
        return last

    def decrypted_credential(self, database_type: str) -> dict[str, Any]:
        from core.tools.tool_manager import ToolManager
        from extensions.ext_database import db
        from models.tools import BuiltinToolProvider
        from services.tools.builtin_tools_manage_service import BuiltinToolManageService

        rows = db.session.query(BuiltinToolProvider).filter(BuiltinToolProvider.provider == MODERN_PROVIDER).all()
        controller = ToolManager.get_builtin_provider(MODERN_PROVIDER, self.tenant_id)
        for row in rows:
            encrypter, _ = BuiltinToolManageService.create_tool_encrypter(self.tenant_id, row, MODERN_PROVIDER, controller)
            credential = dict(encrypter.decrypt(row.credentials))
            if credential.get("database_type") == database_type:
                self.secrets.extend(str(value) for key, value in credential.items() if key in {"password", "token", "api_key"} and value)
                return credential
        raise RuntimeError(f"No installed Modern credential found for {database_type}.")

    def legacy_parameters(self, database: str) -> dict[str, Any]:
        if database in {"mysql", "postgresql"}:
            password = os.getenv(f"PHASE10_2_{database.upper()}_PASSWORD")
            if not password:
                raise RuntimeError(f"PHASE10_2_{database.upper()}_PASSWORD is required for the local {database} fixture.")
            return {"db_type": database, "db_host": "host.docker.internal", "db_port": 3306 if database == "mysql" else 5432, "db_username": "plugin_test_user", "db_password": password, "db_name": "plugin_test", "db_properties": "charset=utf8mb4" if database == "mysql" else "ssl_mode=disable"}
        source = self.decrypted_credential("sqlserver")
        return {
            "db_type": "postgresql" if database == "postgresql" else "mssql",
            "db_host": source["host"], "db_port": source.get("port"),
            "db_username": source["username"], "db_password": source["password"],
            "db_name": source.get("database", ""),
            "db_properties": "&".join(f"{key}={source[key]}" for key in ("schema", "charset", "ssl_mode") if source.get(key)),
        }

    def legacy_tool(self) -> Any:
        from core.tools.entities.tool_entities import ToolProviderType
        from core.tools.tool_manager import ToolManager

        return ToolManager.get_tool_runtime(
            provider_type=ToolProviderType.BUILT_IN, provider_id=LEGACY_PROVIDER,
            tool_name=LEGACY_TOOL, tenant_id=self.tenant_id, credential_id=None,
        )

    def invoke_legacy(self, parameters: dict[str, Any]) -> dict[str, Any]:
        messages = list(self.legacy_tool().invoke(user_id=self.user_id, tool_parameters=parameters))
        if len(messages) != 1:
            raise AssertionError("Legacy Tool returned an unexpected message count.")
        raw = model(messages[0])
        message = raw.get("message", {})
        if "text" in message:
            return {"message_type": "text", "output": message["text"]}
        if "json_object" in message:
            return {"message_type": "json", "output": message["json_object"]}
        return {"message_type": "unknown", "output": raw}

    def database_query(self, database: str) -> str:
        if database == "mssql":
            return "SELECT TOP 5 id, username, display_name, department FROM plugin_test.plugin_test_users ORDER BY id"
        return "SELECT id, username, email, department FROM plugin_test_users ORDER BY id LIMIT 5"

    def runtime_fixtures(self) -> dict[str, Any]:
        fixtures: list[dict[str, Any]] = []
        for database in ("mysql", "postgresql", "mssql"):
            base = self.legacy_parameters(database)
            for output_format in ("markdown", "json"):
                parameters = {**base, "query_sql": self.database_query(database), "output_format": output_format}
                started = utcnow()
                try:
                    output = self.invoke_legacy(parameters)
                    if output_format == "markdown":
                        checks = {"message_type": output["message_type"] == "text", "table_read": isinstance(output["output"], str) and "|" in output["output"]}
                    else:
                        records = output.get("output", {}).get("records") if isinstance(output.get("output"), dict) else None
                        checks = {"message_type": output["message_type"] == "json", "records_only": isinstance(output.get("output"), dict) and set(output["output"]) == {"records"}, "table_read": isinstance(records, list) and bool(records), "legacy_null": isinstance(records, list) and any("" in row.values() for row in records)}
                    status = "PASS" if all(checks.values()) else "FAIL"
                    error = None
                except Exception as exc:  # noqa: BLE001
                    output, checks, status, error = None, {}, "FAIL", str(exc)
                fixture = {
                    "fixture_kind": "raw_installed_legacy_tool_output",
                    "captured_at": started,
                    "database": database,
                    "query_id": f"{database}_table_read",
                    "query_sha256": digest(self.database_query(database)),
                    "output_format": output_format,
                    "runtime": "Dify ToolManager -> installed plugin-daemon Tool",
                    "source_commit": self.args.source_commit,
                    "plugin_checksum": self.expected_checksum,
                    "package_sha256": self.package_sha256,
                    "encoding": "utf-8",
                    "line_ending": "LF",
                    "status": status,
                    "checks": checks,
                    "output": output,
                    "error": error,
                }
                dump(self.output_dir / "phase10_2_runtime_fixtures" / f"{database}_{output_format}_table_raw.json", self.safe(fixture))
                fixtures.append(fixture)
        return {"status": "PASS" if fixtures and all(item["status"] == "PASS" for item in fixtures) else "FAIL", "fixtures": fixtures}

    def select_one_golden(self) -> dict[str, Any]:
        cases: list[dict[str, Any]] = []
        for database in ("mysql", "postgresql", "mssql"):
            try:
                output = self.invoke_legacy({**self.legacy_parameters(database), "query_sql": "SELECT 1 AS probe", "output_format": "markdown"})
                status = "PASS" if output == {"message_type": "text", "output": SELECT_ONE_GOLDEN} else "FAIL"
                error = None
            except Exception as exc:  # noqa: BLE001
                output, status, error = None, "FAIL", str(exc)
            cases.append({"database": database, "status": status, "expected": SELECT_ONE_GOLDEN, "actual": output, "error": error})
        report = {"status": "PASS" if all(item["status"] == "PASS" for item in cases) else "FAIL", "contract": "original_select_1_markdown", "cases": cases}
        dump(self.output_dir / "phase10_2_select1_golden.json", self.safe(report))
        return report

    def schema_and_security(self) -> dict[str, Any]:
        from core.plugin.impl.tool import PluginToolManager
        from core.tools.entities.tool_entities import ToolProviderType
        from core.tools.tool_manager import ToolManager

        manager = PluginToolManager()
        provider = model(manager.fetch_tool_provider(self.tenant_id, MODERN_PROVIDER).declaration)
        legacy = next(item for item in provider["tools"] if item["identity"]["name"] == LEGACY_TOOL)
        modern = next(item for item in provider["tools"] if item["identity"]["name"] == MODERN_TOOL)
        legacy_names = [item["name"] for item in legacy["parameters"]]
        schema_checks = {
            "legacy_provider_present": legacy["identity"]["name"] == LEGACY_TOOL,
            "modern_provider_present": modern["identity"]["name"] == MODERN_TOOL,
            "distinct_tool_identities": legacy["identity"]["name"] != modern["identity"]["name"],
            "legacy_parameter_order": legacy_names == ["db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "db_properties", "query_sql", "output_format"],
        }
        blocked = self.invoke_legacy({**self.legacy_parameters("mysql"), "query_sql": "DELETE FROM plugin_test_users", "output_format": "json"})
        output = blocked.get("output") if isinstance(blocked, dict) else None
        error = output.get("error", {}) if isinstance(output, dict) else {}
        security_checks = {"dml_blocked": error.get("type") == "ReadOnlyViolationError", "no_secret_in_error": all(secret not in json.dumps(blocked, ensure_ascii=False) for secret in self.secrets)}
        pg = self.decrypted_credential("postgresql")
        rows = __import__("extensions.ext_database", fromlist=["db"]).db.session
        from models.tools import BuiltinToolProvider
        row = rows.query(BuiltinToolProvider).filter(BuiltinToolProvider.provider == MODERN_PROVIDER).filter(BuiltinToolProvider.name == "PostgreSQL Phase 9.8 Regression").first()
        modern_tool = ToolManager.get_tool_runtime(ToolProviderType.BUILT_IN, MODERN_PROVIDER, MODERN_TOOL, self.tenant_id, credential_id=str(row.id))
        modern_message = model(list(modern_tool.invoke(user_id=self.user_id, tool_parameters={"sql": "SELECT 1 AS probe", "max_rows": 1, "timeout_seconds": 30, "readonly": True, "output_format": "json"}))[0])
        modern_output = modern_message["message"]["json_object"]
        modern_checks = {"modern_postgresql_select1": modern_output.get("rows") == [{"probe": 1}], "modern_response_preserved": "records" not in modern_output}
        report = {"status": "PASS" if all(schema_checks.values()) and all(security_checks.values()) and all(modern_checks.values()) else "FAIL", "schema_checks": schema_checks, "security_checks": security_checks, "modern_checks": modern_checks, "security_output": blocked}
        dump(self.output_dir / "phase10_2_schema_security_modern_regression.json", self.safe(report))
        return report

    def run(self) -> int:
        installation = self.install_candidate()
        fixtures = self.runtime_fixtures()
        golden = self.select_one_golden()
        regression = self.schema_and_security()
        final = {
            "suite": "phase10_2_installed_legacy_runtime",
            "generated_at": utcnow(),
            "status": "PASS" if all(item["status"] == "PASS" for item in (installation, fixtures, golden, regression)) else "FAIL",
            "source_starting_commit": "8ef7306",
            "source_commit": self.args.source_commit,
            "candidate": {"package_sha256": self.package_sha256, "plugin_checksum": self.expected_checksum},
            "active_identifier": self.active_identifier,
            "gates": {"installation": installation["status"], "legacy_runtime_fixtures": fixtures["status"], "select1_golden": golden["status"], "schema_security_modern_regression": regression["status"]},
            "workflow": {"status": "BLOCKED", "reason": "Dify api/nginx containers cannot start because Docker Desktop WSL bind-mount sources are missing."},
            "allowed_conclusions": ["LEGACY_INSTALLED_TOOL_RUNTIME_THREE_DATABASE_PASS"] if all(item["status"] == "PASS" for item in (installation, fixtures, golden, regression)) else [],
            "not_proven": ["LEGACY_WORKFLOW_MIGRATION_PASS", "PHASE_10_2_PASS", "ORACLE_REPRODUCTION_PASS", "ORACLE11G_REPRODUCTION_PASS", "DM8_FINAL_DELIVERY_PASS", "KINGBASEES_FINAL_DELIVERY_PASS", "FINAL_PROJECT_DELIVERY_PASS"],
        }
        dump(self.output_dir / "phase10_2_installed_runtime_final.json", self.safe(final))
        print(json.dumps({"status": final["status"], "gates": final["gates"]}))
        return 0 if final["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--expected-checksum", required=True)
    parser.add_argument("--package-sha256", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    gate = Gate(args)
    try:
        return gate.run()
    finally:
        gate.close()


if __name__ == "__main__":
    raise SystemExit(main())
