"""DM8 data capability evidence closure runner.

Writes complete non-secret JSON artifacts for DM8 rows/columns. It does not
change the historical Provider/Tool/Workflow regression contract.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.database import execute_read_only_query  # noqa: E402
from utils.validation import validate_connection_config, validate_tool_parameters  # noqa: E402


DATABASE = {
    "database_type": "dm",
    "host": os.getenv("DM_HOST", "127.0.0.1"),
    "port": int(os.getenv("DM_PORT", "5236")),
    "database": os.getenv("DM_DATABASE", "DMSERVER"),
    "username": os.getenv("DM_USERNAME", "PLUGIN_TEST_USER"),
    "password": os.getenv("DM_PASSWORD", "PluginRead_2026!"),
    "connection_timeout": int(os.getenv("DM_CONNECTION_TIMEOUT", "10")),
    "schema": os.getenv("DM_SCHEMA", "PLUGIN_TEST_OWNER"),
    "ssl_mode": "disable",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = run()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if report["summary"]["fail"] else 0


def run() -> dict[str, Any]:
    config = validate_connection_config(DATABASE)
    capabilities = capability_specs()
    evidence = [execute_capability(config, item) for item in capabilities]
    summary = {"pass": 0, "partial": 0, "not_evidenced": 0, "fail": 0}
    for item in evidence:
        summary[item["status"].lower()] += 1
    return {
        "suite": "dm8_data_capability_closure",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "DM8 data capability evidence only; regression suite unchanged.",
        "database_type": "dm",
        "execution_layer": "tool_json",
        "summary": summary,
        "capabilities": evidence,
    }


def execute_capability(config: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    started = perf_counter()
    base = {
        "capability_id": spec["id"],
        "capability_name": spec["name"],
        "sql": spec["sql"],
        "execution_layer": "tool_json",
        "workflow_run_id": None,
        "generated_at": generated_at,
    }
    try:
        params = validate_tool_parameters(
            {"sql": spec["sql"], "max_rows": spec["max_rows"], "timeout_seconds": 30, "readonly": True}
        )
        result = execute_read_only_query(config, params["sql"], params["max_rows"], params["timeout_seconds"])
        assertion = spec["assertion"](result)
        status = "PASS" if assertion["passed"] else "FAIL"
        return {
            **base,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
            "truncated": result["truncated"],
            "max_rows": result["max_rows"],
            "execution_time_ms": int((perf_counter() - started) * 1000),
            "assertion": assertion,
            "status": status,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "truncated": False,
            "max_rows": spec["max_rows"],
            "execution_time_ms": int((perf_counter() - started) * 1000),
            "assertion": {"passed": False, "message": str(exc)},
            "status": "FAIL",
        }


def capability_specs() -> list[dict[str, Any]]:
    return [
        cap(
            "DM8-CAP-01",
            "SELECT * field values",
            'SELECT * FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" ORDER BY "ID" LIMIT 5',
            5,
            lambda r: assert_all(
                r["columns"] == ["ID", "USERNAME", "EMAIL", "DEPARTMENT", "SALARY", "CREATED_AT"],
                r["row_count"] == 5,
                r["rows"][0]["USERNAME"] == "Zhang Wei",
                r["rows"][4]["EMAIL"] is None,
            ),
        ),
        cap(
            "DM8-CAP-02",
            "WHERE filter",
            'SELECT * FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_ORDERS" WHERE "STATUS" = \'completed\' ORDER BY "ID"',
            100,
            lambda r: assert_all(r["row_count"] == 14, all(row["STATUS"] == "completed" for row in r["rows"])),
        ),
        cap(
            "DM8-CAP-03",
            "ORDER BY and max_rows first three IDs",
            'SELECT * FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" ORDER BY "ID"',
            3,
            lambda r: assert_all(r["row_count"] == 3, r["truncated"] is True, [row["ID"] for row in r["rows"]] == [1, 2, 3]),
        ),
        cap(
            "DM8-CAP-04",
            "LIMIT",
            'SELECT * FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" ORDER BY "ID" LIMIT 5',
            100,
            lambda r: assert_all(r["row_count"] == 5, r["truncated"] is False),
        ),
        cap(
            "DM8-CAP-05",
            "COUNT(*) actual value",
            'SELECT COUNT(*) AS "USER_COUNT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS"',
            10,
            lambda r: assert_all(r["row_count"] == 1, r["rows"][0]["USER_COUNT"] == 12),
        ),
        cap(
            "DM8-CAP-06",
            "GROUP BY average salary",
            'SELECT "DEPARTMENT", AVG("SALARY") AS "AVERAGE_SALARY" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" GROUP BY "DEPARTMENT" ORDER BY "DEPARTMENT"',
            20,
            lambda r: assert_all(
                r["row_count"] == 7,
                decimal_eq(group_value(r, "Engineering"), "19237.50"),
                decimal_eq(group_value(r, "Product"), "16000.25"),
                decimal_eq(group_value(r, "Support"), "12800.00"),
            ),
        ),
        cap(
            "DM8-CAP-07",
            "JOIN",
            'SELECT U."USERNAME", O."PRODUCT_NAME", O."AMOUNT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" U JOIN "PLUGIN_TEST_OWNER"."PLUGIN_TEST_ORDERS" O ON U."ID" = O."USER_ID" ORDER BY O."ID" LIMIT 10',
            100,
            lambda r: assert_all(r["row_count"] == 10, r["rows"][0]["USERNAME"] == "Zhang Wei", r["rows"][0]["PRODUCT_NAME"] == "Dify Pro License"),
        ),
        cap(
            "DM8-CAP-08",
            "Unicode literal",
            'SELECT \'中文测试\' AS "UNICODE_TEXT" FROM DUAL',
            1,
            lambda r: assert_all(r["row_count"] == 1, r["rows"][0]["UNICODE_TEXT"] == "中文测试"),
        ),
        cap(
            "DM8-CAP-09",
            "NULL to JSON null",
            'SELECT "ID", "USERNAME", "EMAIL", "SALARY" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" WHERE "EMAIL" IS NULL OR "SALARY" IS NULL ORDER BY "ID"',
            10,
            lambda r: assert_all(r["row_count"] == 2, r["rows"][0]["EMAIL"] is None, r["rows"][0]["SALARY"] is None, r["rows"][1]["EMAIL"] is None),
        ),
        cap(
            "DM8-CAP-10",
            "JSON text serialization",
            'SELECT \'{"source"\' || CHR(58) || \'"dm8","ok"\' || CHR(58) || \'true,"count"\' || CHR(58) || \'12}\' AS "JSON_TEXT" FROM DUAL',
            1,
            lambda r: assert_json_text(r),
        ),
        cap(
            "DM8-CAP-11",
            "CLOB/TEXT read",
            'SELECT "ID", "EVENT_TYPE", "EVENT_MESSAGE" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_LOGS" WHERE "ID" = 5',
            1,
            lambda r: assert_all(r["row_count"] == 1, r["rows"][0]["EVENT_MESSAGE"] == "Workflow integration smoke test."),
        ),
        cap(
            "DM8-CAP-12",
            "Parameter-safe Unicode equivalent",
            'SELECT \'中文测试\' AS "UNICODE_TEXT" FROM DUAL',
            1,
            lambda r: assert_all(r["row_count"] == 1, r["rows"][0]["UNICODE_TEXT"] == "中文测试"),
        ),
        cap(
            "DM8-CAP-13",
            "Multi-row array shape",
            'SELECT "ID", "USERNAME" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" ORDER BY "ID" LIMIT 10',
            100,
            lambda r: assert_all(r["row_count"] == 10, isinstance(r["rows"], list), isinstance(r["rows"][0], dict)),
        ),
        cap(
            "DM8-CAP-14",
            "Empty result",
            'SELECT "ID", "USERNAME" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_USERS" WHERE "ID" = -1',
            10,
            lambda r: assert_all(r["row_count"] == 0, r["rows"] == [], r["truncated"] is False),
        ),
    ]


def cap(capability_id: str, name: str, sql: str, max_rows: int, assertion: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    return {"id": capability_id, "name": name, "sql": sql, "max_rows": max_rows, "assertion": assertion}


def assert_all(*checks: bool) -> dict[str, Any]:
    passed = all(checks)
    return {"passed": passed, "message": "all checks passed" if passed else "one or more checks failed"}


def group_value(result: dict[str, Any], department: str) -> Any:
    for row in result["rows"]:
        if row["DEPARTMENT"] == department:
            return row["AVERAGE_SALARY"]
    return None


def decimal_eq(actual: Any, expected: str) -> bool:
    return actual is not None and Decimal(str(actual)) == Decimal(expected)


def assert_json_text(result: dict[str, Any]) -> dict[str, Any]:
    if result["row_count"] != 1:
        return {"passed": False, "message": "expected one JSON text row"}
    payload = json.loads(result["rows"][0]["JSON_TEXT"])
    return assert_all(payload == {"source": "dm8", "ok": True, "count": 12})


if __name__ == "__main__":
    raise SystemExit(main())
