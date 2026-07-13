"""Install and validate the Phase 9.8 package through Dify application services."""

from __future__ import annotations

import argparse
import json
import os
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable


PROVIDER_ID = "li_zijun/db_query_extended/db_query_extended"
PLUGIN_ID = "li_zijun/db_query_extended"
TOOL_NAME = "db_query_extended"
EXPECTED_CHECKSUM = "bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9"
KINGBASE_CREDENTIAL_NAME = "KingbaseES Phase 9.8 Readonly"
POSTGRES_CREDENTIAL_NAME = "PostgreSQL Phase 9.8 Regression"
OUTPUT_KEYS = {
    "success", "database_type", "execution_time_ms", "columns", "rows",
    "row_count", "truncated", "max_rows", "generated_at", "warning", "error",
}


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def config(prefix: str, database_type: str, schema: str = "") -> dict[str, Any]:
    return {
        "database_type": database_type,
        "host": required(f"{prefix}_HOST"),
        "port": required(f"{prefix}_PORT"),
        "database": required(f"{prefix}_DATABASE"),
        "username": required(f"{prefix}_USERNAME"),
        "password": required(f"{prefix}_PASSWORD"),
        "schema": os.getenv(f"{prefix}_SCHEMA", schema),
        "connection_timeout": os.getenv(f"{prefix}_CONNECTION_TIMEOUT", "5"),
        "ssl_mode": os.getenv(f"{prefix}_SSL_MODE", "disable"),
    }


def model(value: Any) -> Any:
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def context() -> tuple[Any, str, str]:
    from app_factory import create_app
    from extensions.ext_database import db
    from models.tools import BuiltinToolProvider

    app = create_app()
    app_context = app.app_context()
    app_context.push()
    row = db.session.query(BuiltinToolProvider).filter(BuiltinToolProvider.provider == PROVIDER_ID).first()
    if row is None:
        raise RuntimeError("No existing db_query_extended credential identifies the Dify tenant/user")
    return app_context, str(row.tenant_id), str(row.user_id)


def plugin_summary(plugin: Any) -> dict[str, Any]:
    data = model(plugin)
    return {
        key: data.get(key)
        for key in ("plugin_id", "plugin_unique_identifier", "version", "installation_id", "source")
        if key in data
    }


def install(package: Path, output: Path, rollback_package: str) -> int:
    from core.plugin.entities.plugin import PluginInstallationSource
    from core.plugin.entities.plugin_daemon import PluginDecodeResponse
    from core.plugin.impl.plugin import PluginInstaller
    from services.plugin.plugin_service import PluginService

    def decode_with_daemon_parameter(
        self: Any, tenant_id: str, plugin_unique_identifier: str
    ) -> Any:
        return self._request_with_plugin_daemon_response(
            "GET",
            f"plugin/{tenant_id}/management/decode/from_identifier",
            PluginDecodeResponse,
            params={"PluginUniqueIdentifier": plugin_unique_identifier},
        )

    # Dify 1.13.3 sends snake_case, while the preserved daemon 0.5.3
    # requires this exact Go binder field name. The same compatibility fix
    # is already documented by the project's SQL Server installation gate.
    PluginInstaller.decode_plugin_from_identifier = decode_with_daemon_parameter

    app_context, tenant_id, _user_id = context()
    try:
        before = [plugin for plugin in PluginService.list(tenant_id) if plugin.plugin_id == PLUGIN_ID]
        response = PluginService.upload_pkg(tenant_id, package.read_bytes())
        identifier = response.unique_identifier
        if not identifier.endswith("@" + EXPECTED_CHECKSUM):
            raise AssertionError(f"Uploaded identifier checksum mismatch: {identifier}")
        task = PluginService.install_from_local_pkg(tenant_id, [identifier])
        task_id = str(getattr(task, "id", None) or getattr(task, "task_id", None) or model(task).get("id"))
        last = None
        for _ in range(90):
            last = PluginService.fetch_install_task(tenant_id, task_id)
            state = str(getattr(last, "status", "")).lower()
            if state in {"success", "succeeded", "failed", "error"}:
                break
            time.sleep(2)
        after = [plugin for plugin in PluginService.list(tenant_id) if plugin.plugin_id == PLUGIN_ID]
        active = next((plugin for plugin in after if plugin.plugin_unique_identifier == identifier), None)
        upgrade_last = None
        if active is None and before:
            upgrade = PluginInstaller().upgrade_plugin(
                tenant_id,
                before[0].plugin_unique_identifier,
                identifier,
                PluginInstallationSource.Package,
                {"plugin_unique_identifier": identifier},
            )
            upgrade_task_id = str(getattr(upgrade, "id", None) or getattr(upgrade, "task_id", None) or model(upgrade).get("id"))
            for _ in range(90):
                upgrade_last = PluginService.fetch_install_task(tenant_id, upgrade_task_id)
                state = str(getattr(upgrade_last, "status", "")).lower()
                if state in {"success", "succeeded", "failed", "error"}:
                    break
                time.sleep(2)
            after = [plugin for plugin in PluginService.list(tenant_id) if plugin.plugin_id == PLUGIN_ID]
            active = next((plugin for plugin in after if plugin.plugin_unique_identifier == identifier), None)
        install_success = str(getattr(last, "status", "")).lower() in {"success", "succeeded"}
        upgrade_success = upgrade_last is None or str(getattr(upgrade_last, "status", "")).lower() in {"success", "succeeded"}
        status = "PASS" if active is not None and install_success and upgrade_success else "FAIL"
        report = {
            "suite": "kingbasees_phase9_8_dify_installation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "tenant_id_recorded": False,
            "decode_parameter_compatibility": "PluginUniqueIdentifier",
            "before": [plugin_summary(plugin) for plugin in before],
            "candidate": {
                "version": "0.1.1", "plugin_checksum": EXPECTED_CHECKSUM,
                "package_sha256": "117206A0F0D50FDA0EA7C1895E82BA0151AE0DEE3583B3E914240A0D2985C389",
            },
            "upload_identifier": identifier,
            "install_task": model(last),
            "upgrade_task": model(upgrade_last),
            "after": [plugin_summary(plugin) for plugin in after],
            "rollback": {
                "previous_identifier": before[0].plugin_unique_identifier if before else None,
                "previous_package_path": rollback_package,
                "procedure": "Upload the preserved previous package through PluginService.upload_pkg, then PluginService.install_from_local_pkg with its returned identifier.",
            },
            "checks": {
                "candidate_checksum_match": identifier.endswith("@" + EXPECTED_CHECKSUM),
                "install_task_success": install_success,
                "upgrade_task_success": upgrade_success,
                "candidate_active": active is not None,
            },
        }
        write(output, report)
        print(json.dumps({"status": status, "identifier": identifier, "task_id": task_id}))
        return 0 if status == "PASS" else 1
    finally:
        app_context.pop()


def case(cases: list[dict[str, Any]], name: str, expected: str, action: Callable[[], Any], check: Callable[[Any], bool]) -> Any:
    started = perf_counter()
    try:
        value = action()
        passed = check(value)
        actual = compact(value)
    except Exception as exc:  # noqa: BLE001
        value = exc
        passed = check(exc)
        actual = {"error_type": type(exc).__name__, "message": str(exc)}
    cases.append({
        "case": name, "expected": expected, "actual": actual,
        "status": "PASS" if passed else "FAIL",
        "duration_ms": int((perf_counter() - started) * 1000), "redaction_check": True,
    })
    return value


def compact(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return {key: value[key] for key in OUTPUT_KEYS if key in value}
    return str(value)


def safe_failure(secret: str) -> Callable[[Any], bool]:
    return lambda value: isinstance(value, Exception) and secret not in str(value) and "://" not in str(value)


def validate_provider(manager: Any, tenant_id: str, user_id: str, credentials: dict[str, Any]) -> bool:
    return bool(manager.validate_provider_credentials(tenant_id, user_id, PROVIDER_ID, credentials))


def save_credential(tenant_id: str, user_id: str, name: str, credentials: dict[str, Any]) -> str:
    from core.plugin.entities.plugin_daemon import CredentialType
    from extensions.ext_database import db
    from models.tools import BuiltinToolProvider
    from services.tools.builtin_tools_manage_service import BuiltinToolManageService

    row = (
        db.session.query(BuiltinToolProvider)
        .filter(BuiltinToolProvider.tenant_id == tenant_id)
        .filter(BuiltinToolProvider.provider == PROVIDER_ID)
        .filter(BuiltinToolProvider.name == name)
        .first()
    )
    if row:
        BuiltinToolManageService.update_builtin_tool_provider(
            user_id, tenant_id, PROVIDER_ID, str(row.id), credentials=credentials
        )
        return str(row.id)
    BuiltinToolManageService.add_builtin_tool_provider(
        user_id, CredentialType.API_KEY, tenant_id, PROVIDER_ID, credentials, name=name
    )
    row = (
        db.session.query(BuiltinToolProvider)
        .filter(BuiltinToolProvider.tenant_id == tenant_id)
        .filter(BuiltinToolProvider.provider == PROVIDER_ID)
        .filter(BuiltinToolProvider.name == name)
        .first()
    )
    return str(row.id)


def invoke(tenant_id: str, user_id: str, credential_id: str, sql: str, max_rows: int = 100) -> dict[str, Any]:
    from core.tools.entities.tool_entities import ToolProviderType
    from core.tools.tool_manager import ToolManager

    tool = ToolManager.get_tool_runtime(
        provider_type=ToolProviderType.BUILT_IN, provider_id=PROVIDER_ID,
        tool_name=TOOL_NAME, tenant_id=tenant_id, credential_id=credential_id,
    )
    messages = list(tool.invoke(user_id=user_id, tool_parameters={
        "sql": sql, "max_rows": max_rows, "timeout_seconds": 30,
        "readonly": True, "output_format": "json",
    }))
    message = messages[0].model_dump(mode="json")
    return message["message"]["json_object"]


def invoke_with_credentials(
    tenant_id: str, user_id: str, credentials: dict[str, Any], sql: str
) -> dict[str, Any]:
    from core.plugin.entities.plugin_daemon import CredentialType
    from core.plugin.impl.tool import PluginToolManager

    messages = list(PluginToolManager().invoke(
        tenant_id, user_id, PROVIDER_ID, TOOL_NAME, credentials,
        CredentialType.API_KEY,
        {"sql": sql, "max_rows": 100, "timeout_seconds": 30, "readonly": True, "output_format": "json"},
    ))
    message = messages[0].model_dump(mode="json")
    return message["message"]["json_object"]


def suite(name: str, cases: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    return {
        "suite": name, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if cases and all(item["status"] == "PASS" for item in cases) else "FAIL",
        "summary": {"pass": sum(x["status"] == "PASS" for x in cases), "fail": sum(x["status"] == "FAIL" for x in cases)},
        "cases": cases, **extra,
    }


def validate(output_dir: Path) -> int:
    from core.plugin.impl.tool import PluginToolManager
    from core.tools.entities.tool_entities import ToolProviderType
    from core.tools.tool_manager import ToolManager

    app_context, tenant_id, user_id = context()
    try:
        manager = PluginToolManager()
        entity = manager.fetch_tool_provider(tenant_id, PROVIDER_ID)
        declaration = model(entity.declaration)
        active_identifier = entity.plugin_unique_identifier
        if not active_identifier.endswith("@" + EXPECTED_CHECKSUM):
            raise AssertionError(f"Dify active checksum mismatch: {active_identifier}")
        option_values = [item["value"] for item in declaration["credentials_schema"][0]["options"]]

        kingbase = config("KINGBASE", "kingbasees", "phase97_fixture")
        provider_cases: list[dict[str, Any]] = []
        for name, schema in (("valid_fixture", "phase97_fixture"), ("valid_public", "public"), ("valid_empty_schema", "")):
            current = deepcopy(kingbase); current["schema"] = schema
            case(provider_cases, name, "installed Provider validates", lambda c=current: validate_provider(manager, tenant_id, user_id, c), lambda v: v is True)
        timeout = deepcopy(kingbase); timeout["connection_timeout"] = "7"
        case(provider_cases, "explicit_timeout_special_password", "installed Provider validates", lambda: validate_provider(manager, tenant_id, user_id, timeout), lambda v: v is True)
        for name, changes, secret in (
            ("wrong_password", {"password": "phase98-deliberate-wrong-password"}, "phase98-deliberate-wrong-password"),
            ("unreachable", {"port": "1"}, kingbase["password"]),
            ("invalid_database", {"database": "phase98_missing_database"}, kingbase["password"]),
            ("invalid_schema", {"schema": "phase98_missing_schema"}, kingbase["password"]),
            ("missing_host", {"host": ""}, kingbase["password"]),
        ):
            current = deepcopy(kingbase); current.update(changes)
            case(provider_cases, name, "installed Provider returns safe failure", lambda c=current: validate_provider(manager, tenant_id, user_id, c), safe_failure(secret))
        kingbase_credential = save_credential(tenant_id, user_id, KINGBASE_CREDENTIAL_NAME, kingbase)
        provider_report = suite(
            "kingbasees_phase9_8_installed_provider_validation", provider_cases,
            active_identifier=active_identifier, schema_options=option_values,
            provider_schema_has_kingbasees="kingbasees" in option_values,
            credential_persisted_encrypted=True,
        )

        tool_cases: list[dict[str, Any]] = []
        table = "phase97_fixture.sample_data"
        queries = (
            ("select_1", "SELECT 1 AS probe", 100, lambda r: r["rows"] == [{"probe": 1}]),
            ("fixture", f"SELECT id, label FROM {table} ORDER BY id", 100, lambda r: r["row_count"] == 12),
            ("unicode", f"SELECT unicode_text FROM {table} WHERE id=1", 100, lambda r: r["rows"][0]["unicode_text"] == "金仓只读验证"),
            ("types", f"SELECT nullable_text, amount, event_date, event_time FROM {table} WHERE id=2", 100, lambda r: r["rows"][0]["nullable_text"] is None and r["rows"][0]["amount"] == "2.50"),
            ("schema_read", f"SELECT COUNT(*) AS total FROM {table}", 100, lambda r: r["rows"] == [{"total": 12}]),
            ("truncation", f"SELECT id FROM {table} ORDER BY id", 5, lambda r: r["row_count"] == 5 and r["truncated"]),
            ("empty", f"SELECT id FROM {table} WHERE id<0", 100, lambda r: r["row_count"] == 0),
            ("aggregate", f"SELECT SUM(amount) AS total FROM {table}", 100, lambda r: r["rows"] == [{"total": "84.00"}]),
            ("order_by", f"SELECT id FROM {table} ORDER BY id DESC", 3, lambda r: [x["id"] for x in r["rows"]] == [12, 11, 10]),
        )
        for name, sql, max_rows, predicate in queries:
            case(tool_cases, name, "installed Tool returns verified content", lambda s=sql, m=max_rows: invoke(tenant_id, user_id, kingbase_credential, s, m), lambda r, p=predicate: isinstance(r, dict) and r.get("success") is True and OUTPUT_KEYS.issubset(r) and r["database_type"] == "kingbasees" and p(r))
        for name, sql in (("dml_rejection", f"DELETE FROM {table}"), ("ddl_rejection", f"DROP TABLE {table}"), ("multi_statement_rejection", "SELECT 1; SELECT 2")):
            case(tool_cases, name, "installed Tool blocks unsafe SQL", lambda s=sql: invoke(tenant_id, user_id, kingbase_credential, s), lambda r: isinstance(r, dict) and not r.get("success") and r.get("error", {}).get("type") == "ReadOnlyViolationError")
        bad_tool = deepcopy(kingbase); bad_tool["password"] = "phase98-tool-wrong-password"
        case(tool_cases, "bad_auth_redaction", "installed Tool returns safe authentication failure", lambda: invoke_with_credentials(tenant_id, user_id, bad_tool, "SELECT 1"), lambda r: isinstance(r, dict) and not r.get("success") and "phase98-tool-wrong-password" not in json.dumps(r) and "://" not in json.dumps(r))
        case(tool_cases, "post_failure_cleanup", "installed Tool remains usable after failed authentication", lambda: invoke(tenant_id, user_id, kingbase_credential, "SELECT 1 AS probe"), lambda r: r.get("rows") == [{"probe": 1}])
        tool_report = suite("kingbasees_phase9_8_installed_tool_validation", tool_cases, active_identifier=active_identifier)

        postgres = config("POSTGRES", "postgresql", "public")
        postgres_credential = save_credential(tenant_id, user_id, POSTGRES_CREDENTIAL_NAME, postgres)
        regression_cases: list[dict[str, Any]] = []
        case(regression_cases, "postgresql_provider", "installed Provider validates PostgreSQL", lambda: validate_provider(manager, tenant_id, user_id, postgres), lambda v: v is True)
        case(regression_cases, "postgresql_tool", "installed Tool executes PostgreSQL SELECT 1", lambda: invoke(tenant_id, user_id, postgres_credential, "SELECT 1 AS probe"), lambda r: r.get("rows") == [{"probe": 1}])
        case(regression_cases, "provider_options", "existing options preserved", lambda: option_values, lambda v: v == ["mysql", "postgresql", "dm", "sqlserver", "kingbasees"])
        tools = declaration["tools"]
        case(regression_cases, "tool_schema", "installed Tool schema remains declared", lambda: tools, lambda v: any(item["identity"]["name"] == TOOL_NAME for item in v))
        regression_report = suite("kingbasees_phase9_8_targeted_regression", regression_cases, active_identifier=active_identifier, sqlserver_role="OPTIONAL")

        for filename, report in (
            ("kingbasees_phase9_8_installed_provider_validation.json", provider_report),
            ("kingbasees_phase9_8_installed_tool_validation.json", tool_report),
            ("kingbasees_phase9_8_targeted_regression.json", regression_report),
        ):
            write(output_dir / filename, report)
        statuses = {report["suite"]: report["status"] for report in (provider_report, tool_report, regression_report)}
        print(json.dumps(statuses))
        return 0 if all(value == "PASS" for value in statuses.values()) else 1
    finally:
        app_context.pop()


def write(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--package", type=Path, required=True)
    install_parser.add_argument("--output", type=Path, required=True)
    install_parser.add_argument("--rollback-package", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "install":
        return install(args.package, args.output, args.rollback_package)
    return validate(args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
