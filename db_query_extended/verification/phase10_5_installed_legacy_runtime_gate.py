"""Run the Phase 10.5 Legacy compatibility gate inside Dify's API worker.

The runner deliberately imports the established Phase 10.2 installer helper.
It then verifies the new Legacy-only SQL/property/error boundaries through
ToolManager against the candidate package activated in plugin-daemon.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable

from phase10_2_installed_legacy_runtime import Gate as InstalledGate
from phase10_2_installed_legacy_runtime import SELECT_ONE_GOLDEN, dump, utcnow


DATABASE_TYPES = {"mysql": "mysql", "postgresql": "postgresql", "mssql": "sqlserver"}


class Phase10_5Gate(InstalledGate):
    """Install the candidate once, then invoke only its installed Legacy Tool."""

    def legacy_parameters(self, database: str) -> dict[str, Any]:
        if database == "mysql":
            password = os.environ.get("PHASE10_5_MYSQL_PASSWORD")
            if not password:
                raise RuntimeError("PHASE10_5_MYSQL_PASSWORD is required because no installed Modern MySQL credential exists.")
            self.secrets.append(password)
            return {
                "db_type": "mysql", "db_host": "host.docker.internal", "db_port": 3306,
                "db_username": "plugin_test_user", "db_password": password, "db_name": "plugin_test",
                "db_properties": "charset=utf8mb4",
            }
        source = self.decrypted_credential(DATABASE_TYPES[database])
        properties = {
            "mysql": "charset=utf8mb4",
            "postgresql": "ssl_mode=disable",
            "mssql": "&".join(
                f"{key}={source[key]}" for key in ("schema", "charset", "ssl_mode") if source.get(key)
            ),
        }[database]
        return {
            "db_type": database,
            "db_host": source["host"],
            "db_port": source.get("port"),
            "db_username": source["username"],
            "db_password": source["password"],
            "db_name": source.get("database", ""),
            "db_properties": properties,
        }

    def capture(self, parameters: dict[str, Any]) -> dict[str, Any]:
        try:
            return {"outcome": "returned", "output": self.invoke_legacy(parameters)}
        except Exception as exc:  # noqa: BLE001 - the type is runtime evidence.
            raw = str(exc)
            sensitive = any(secret and secret in raw for secret in self.secrets) or "://" in raw or "authorization" in raw.lower()
            return {
                "outcome": "exception",
                "exception_type": exc.__class__.__name__,
                "message": "<redaction-failure>" if sensitive else raw,
                "redaction_check": not sensitive,
            }

    def case(self, name: str, request: dict[str, Any], assertion: Callable[[dict[str, Any]], dict[str, bool]]) -> dict[str, Any]:
        captured = self.capture(request)
        checks = assertion(captured)
        return {
            "name": name,
            "query_sha256": __import__("hashlib").sha256(request["query_sql"].encode("utf-8")).hexdigest(),
            "output_format": request.get("output_format"),
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "actual": captured,
        }

    @staticmethod
    def success_markdown(captured: dict[str, Any]) -> dict[str, bool]:
        output = captured.get("output", {})
        return {
            "returned": captured.get("outcome") == "returned",
            "text_message": output.get("message_type") == "text",
            "github_table": output.get("output") == SELECT_ONE_GOLDEN,
        }

    @staticmethod
    def success_json(captured: dict[str, Any]) -> dict[str, bool]:
        output = captured.get("output", {})
        records = output.get("output") if isinstance(output, dict) else None
        return {
            "returned": captured.get("outcome") == "returned",
            "json_message": output.get("message_type") == "json",
            "records_only": isinstance(records, dict) and set(records) == {"records"},
            "records_value": isinstance(records, dict) and records.get("records") == [{"probe": 1}],
            "result_variable": isinstance(output, dict) and output.get("variables", {}).get("result") == records,
        }

    @staticmethod
    def rejected(fragment: str) -> Callable[[dict[str, Any]], dict[str, bool]]:
        def assertion(captured: dict[str, Any]) -> dict[str, bool]:
            return {
                "exception_path": captured.get("outcome") == "exception",
                "dify_plugin_wrapper": "PluginInvokeError" in str(captured.get("exception_type", "")),
                "expected_safe_message": fragment in str(captured.get("message", "")),
                "redacted": captured.get("redaction_check") is True,
            }

        return assertion

    def installation(self) -> dict[str, Any]:
        result = self.install_candidate()
        old = self.output_dir / "phase10_2_installation.json"
        if old.exists():
            old.replace(self.output_dir / "phase10_5_installation.json")
        return result

    def success_contracts(self) -> dict[str, Any]:
        cases: list[dict[str, Any]] = []
        for database in DATABASE_TYPES:
            base = self.legacy_parameters(database)
            cases.append(self.case(
                f"{database}_markdown_select_1_terminal_semicolon",
                {**base, "query_sql": "SELECT 1 AS probe;", "output_format": "markdown"},
                self.success_markdown,
            ))
            cases.append(self.case(
                f"{database}_json_select_1_terminal_semicolon",
                {**base, "query_sql": "SELECT 1 AS probe;", "output_format": "json"},
                self.success_json,
            ))
        return {"status": self.status(cases), "cases": cases}

    def policy(self) -> dict[str, Any]:
        base = self.legacy_parameters("postgresql")
        cases = [
            self.case("terminal_semicolon_allowed", {**base, "query_sql": "SELECT 1 AS probe;", "output_format": "markdown"}, self.success_markdown),
            self.case("leading_comment_allowed", {**base, "query_sql": "/* Phase10.5 */ SELECT 1 AS probe;", "output_format": "markdown"}, self.success_markdown),
        ]
        for name, sql in (
            ("two_selects_rejected", "SELECT 1; SELECT 2;"),
            ("select_delete_rejected", "SELECT 1; DELETE FROM plugin_test_users;"),
            ("with_rejected", "WITH x AS (SELECT 1) SELECT * FROM x;"),
            ("select_into_rejected", "SELECT 1 INTO phase10_5_blocked_table;"),
            ("delete_rejected", "DELETE FROM plugin_test_users;"),
        ):
            cases.append(self.case(name, {**base, "query_sql": sql, "output_format": "json"}, self.rejected("Only one SELECT statement is allowed for the legacy tool.")))
        return {"status": self.status(cases), "cases": cases}

    def properties(self) -> dict[str, Any]:
        base = self.legacy_parameters("postgresql")
        cases = [
            self.case("schema_public_allowed", {**base, "db_properties": "schema=public", "query_sql": "SELECT 1 AS probe;", "output_format": "json"}, self.success_json),
        ]
        for name, value, fragment in (
            ("duplicate_rejected", "schema=public&schema=test", "Duplicate db_properties key: schema."),
            ("unknown_rejected", "unknown=value", "Unsupported db_properties key: unknown."),
            ("host_override_rejected", "host=attacker", "Unsupported db_properties key: host."),
            ("password_override_rejected", "password=value", "Unsupported db_properties key: password."),
            ("missing_value_rejected", "schema", "Invalid db_properties pair."),
            ("missing_key_rejected", "=value", "Invalid db_properties pair."),
        ):
            cases.append(self.case(name, {**base, "db_properties": value, "query_sql": "SELECT 1 AS probe;", "output_format": "json"}, self.rejected(fragment)))
        return {"status": self.status(cases), "cases": cases}

    def errors(self) -> dict[str, Any]:
        base = self.legacy_parameters("postgresql")
        case = self.case(
            "known_sql_error_is_plugin_exception",
            {**base, "query_sql": "SELECT * FROM phase10_5_missing_table;", "output_format": "json"},
            self.rejected("SQL execution failed."),
        )
        case["checks"]["no_legacy_json_error"] = case["actual"].get("outcome") == "exception"
        case["status"] = "PASS" if all(case["checks"].values()) else "FAIL"
        return {"status": self.status([case]), "cases": [case]}

    @staticmethod
    def status(cases: list[dict[str, Any]]) -> str:
        return "PASS" if cases and all(case["status"] == "PASS" for case in cases) else "FAIL"

    def run(self) -> int:
        installation = self.installation()
        success = self.success_contracts()
        policy = self.policy()
        properties = self.properties()
        errors = self.errors()
        gates = {
            "candidate_installation": installation["status"],
            "three_database_success_contracts": success["status"],
            "legacy_single_select_policy": policy["status"],
            "strict_db_properties": properties["status"],
            "sanitized_plugin_exception": errors["status"],
        }
        final = {
            "suite": "phase10_5_installed_legacy_tool_runtime_gate",
            "generated_at": utcnow(),
            "status": "PASS" if all(value == "PASS" for value in gates.values()) else "FAIL",
            "scope": "candidate package -> Dify PluginService/PluginInstaller -> ToolManager -> installed plugin-daemon Legacy Tool; no Workflow or API key action",
            "source_commit": self.args.source_commit,
            "candidate": {"package_sha256": self.package_sha256, "plugin_checksum": self.expected_checksum},
            "active_identifier": self.active_identifier,
            "gates": gates,
            "installation": installation,
            "success_contracts": success,
            "legacy_policy": policy,
            "db_properties": properties,
            "exception_path": errors,
            "allowed_conclusions": ["PHASE_10_5_INSTALLED_LEGACY_TOOL_RUNTIME_PASS"] if all(value == "PASS" for value in gates.values()) else [],
            "not_proven": ["LEGACY_WORKFLOW_REIMPORT_OR_PUBLISH_PASS", "ORACLE_RUNTIME_PASS", "ORACLE11G_RUNTIME_PASS", "DM8_NEW_RUNTIME_PASS", "KINGBASEES_NEW_RUNTIME_PASS", "FINAL_PROJECT_DELIVERY_PASS"],
        }
        dump(self.output_dir / "phase10_5_installed_legacy_tool_runtime_gate.json", self.safe(final))
        print(json.dumps({"status": final["status"], "gates": gates}))
        return 0 if final["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--expected-checksum", required=True)
    parser.add_argument("--package-sha256", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    gate = Phase10_5Gate(parser.parse_args())
    try:
        return gate.run()
    finally:
        gate.close()


if __name__ == "__main__":
    raise SystemExit(main())
