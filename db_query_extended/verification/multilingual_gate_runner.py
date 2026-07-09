"""Multilingual stored-data retrieval gate.

Creates a deterministic multilingual fixture table, reads it through the same
Tool query path, and asserts exact visible text values. No manual encode/decode
repair is allowed in assertions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from sqlalchemy import text

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from utils.database import create_database_engine, execute_read_only_query  # noqa: E402
from utils.result_formatter import success_response  # noqa: E402
from utils.validation import validate_connection_config  # noqa: E402


EXPECTED_ROWS = [
    {
        "ID": 1,
        "LANGUAGE_CODE": "zh-CN",
        "DISPLAY_NAME": "简体中文",
        "CONTENT_TEXT": "数据库连接测试",
        "SPECIAL_TEXT": "中文标点：你好，世界。",
        "LONG_TEXT": "简体中文长文本：数据库中的真实数据应被插件直接读取并返回。",
    },
    {
        "ID": 2,
        "LANGUAGE_CODE": "zh-TW",
        "DISPLAY_NAME": "繁體中文",
        "CONTENT_TEXT": "資料庫連線測試",
        "SPECIAL_TEXT": "繁體標點：你好，世界。",
        "LONG_TEXT": "繁體中文長文本：資料庫中的真實資料應被外掛直接讀取並返回。",
    },
    {
        "ID": 3,
        "LANGUAGE_CODE": "en",
        "DISPLAY_NAME": "English",
        "CONTENT_TEXT": "Database connection test",
        "SPECIAL_TEXT": "Plain ASCII text",
        "LONG_TEXT": "English long text: stored rows are retrieved through the plugin path.",
    },
    {
        "ID": 4,
        "LANGUAGE_CODE": "ja",
        "DISPLAY_NAME": "日本語",
        "CONTENT_TEXT": "日本語データ検索",
        "SPECIAL_TEXT": "かな・カナ・漢字",
        "LONG_TEXT": "日本語の長文：データベースに保存された文字列をそのまま返します。",
    },
    {
        "ID": 5,
        "LANGUAGE_CODE": "ko",
        "DISPLAY_NAME": "한국어",
        "CONTENT_TEXT": "한국어 데이터 조회",
        "SPECIAL_TEXT": "한글과 문장 부호",
        "LONG_TEXT": "한국어 긴 텍스트: 데이터베이스에 저장된 값을 그대로 반환합니다.",
    },
    {
        "ID": 6,
        "LANGUAGE_CODE": "fr",
        "DISPLAY_NAME": "Français",
        "CONTENT_TEXT": "Café déjà vu — français",
        "SPECIAL_TEXT": "é è ê ç à ù œ",
        "LONG_TEXT": "Texte long accentué: l'élève vérifie la récupération des caractères.",
    },
    {
        "ID": 7,
        "LANGUAGE_CODE": "de",
        "DISPLAY_NAME": "Deutsch",
        "CONTENT_TEXT": "Straße München",
        "SPECIAL_TEXT": "ä ö ü Ä Ö Ü ß",
        "LONG_TEXT": "Deutscher Langtext: Größe, Grüße und Straße bleiben erhalten.",
    },
    {
        "ID": 8,
        "LANGUAGE_CODE": "mixed",
        "DISPLAY_NAME": "Mixed language",
        "CONTENT_TEXT": "中文 + English + 日本語 + 한국어",
        "SPECIAL_TEXT": "Mixed punctuation: 你好, world, こんにちは",
        "LONG_TEXT": "Mixed long text: 简体中文、繁體中文、English、日本語、한국어 are stored together.",
    },
    {
        "ID": 9,
        "LANGUAGE_CODE": "emoji",
        "DISPLAY_NAME": "Emoji",
        "CONTENT_TEXT": "你好，世界 🌍🚀",
        "SPECIAL_TEXT": "emoji: 😀 🎉 🧪",
        "LONG_TEXT": "Emoji long text: supplementary Unicode characters should survive JSON output 🌟.",
    },
    {
        "ID": 10,
        "LANGUAGE_CODE": "special",
        "DISPLAY_NAME": "Special characters",
        "CONTENT_TEXT": "O'Connor + 100% \\ path",
        "SPECIAL_TEXT": "apostrophe ' plus + percent % backslash \\",
        "LONG_TEXT": "Special long text: C:\\temp\\plugin + 100% complete for O'Connor.",
    },
    {
        "ID": 11,
        "LANGUAGE_CODE": "newline",
        "DISPLAY_NAME": "Multiline text",
        "CONTENT_TEXT": "第一行\n第二行",
        "SPECIAL_TEXT": "line1\nline2\nline3",
        "LONG_TEXT": "多行长文本：\n第一行\n第二行\n第三行",
    },
    {
        "ID": 12,
        "LANGUAGE_CODE": "null",
        "DISPLAY_NAME": "Nullable fields",
        "CONTENT_TEXT": "NULL field check",
        "SPECIAL_TEXT": None,
        "LONG_TEXT": None,
    },
]


DATABASES = {
    "mysql": {
        "database_type": "mysql",
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "database": os.getenv("MYSQL_DATABASE", "plugin_test"),
        "username": os.getenv("MYSQL_USERNAME", "plugin_test_user"),
        "password": os.getenv("MYSQL_PASSWORD", "plugin_test_password"),
        "connection_timeout": int(os.getenv("MYSQL_CONNECTION_TIMEOUT", "10")),
        "ssl_mode": "disable",
    },
    "postgresql": {
        "database_type": "postgresql",
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DATABASE", "plugin_test"),
        "username": os.getenv("POSTGRES_USERNAME", "plugin_test_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "plugin_test_password"),
        "connection_timeout": int(os.getenv("POSTGRES_CONNECTION_TIMEOUT", "10")),
        "ssl_mode": os.getenv("POSTGRES_SSL_MODE", "disable"),
    },
    "dm": {
        "database_type": "dm",
        "host": os.getenv("DM_HOST", "127.0.0.1"),
        "port": int(os.getenv("DM_PORT", "5236")),
        "database": os.getenv("DM_DATABASE", "DMSERVER"),
        "username": os.getenv("DM_USERNAME", "PLUGIN_TEST_USER"),
        "password": os.getenv("DM_PASSWORD"),
        "connection_timeout": int(os.getenv("DM_CONNECTION_TIMEOUT", "10")),
        "schema": os.getenv("DM_SCHEMA", "PLUGIN_TEST_OWNER"),
        "ssl_mode": "disable",
    },
}


def resolve_database_config(name: str) -> dict[str, Any]:
    config = dict(DATABASES[name])
    if name == "dm" and not config.get("password"):
        raise RuntimeError("DM_PASSWORD environment variable is required for DM verification.")
    return validate_connection_config(config)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--databases", default="mysql,postgresql,dm")
    parser.add_argument("--skip-setup", action="store_true")
    args = parser.parse_args()

    selected = [item.strip() for item in args.databases.split(",") if item.strip()]
    entries = []
    for name in selected:
        started = perf_counter()
        try:
            config = resolve_database_config(name)
            if not args.skip_setup:
                setup_fixture(config)
            result = query_and_assert(config)
            entries.append({
                "database_type": name,
                "status": "PASS",
                "duration_ms": int((perf_counter() - started) * 1000),
                "driver": driver_name(name),
                "row_count": result["row_count"],
                "checked_fields": ["LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT"],
                "result": result,
            })
        except Exception as exc:  # noqa: BLE001 - verification report must capture failure
            entries.append({
                "database_type": name,
                "status": "FAIL",
                "duration_ms": int((perf_counter() - started) * 1000),
                "driver": driver_name(name),
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
            })

    report = {
        "suite": "multilingual_stored_data_gate",
        "generated_at": now(),
        "summary": summarize(entries),
        "fixture": {
            "table": "PLUGIN_TEST_MULTILINGUAL",
            "row_count": len(EXPECTED_ROWS),
            "sha256": sha256_text(json.dumps(EXPECTED_ROWS, ensure_ascii=False, sort_keys=True)),
            "expected_rows": EXPECTED_ROWS,
        },
        "entries": entries,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    output.write_text(serialized, encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if report["summary"]["fail"] else 0


def setup_fixture(config: dict[str, Any]) -> None:
    engine = create_database_engine(config)
    try:
        with engine.begin() as connection:
            if config["database_type"] == "dm":
                connection.execute(text('DROP TABLE "PLUGIN_TEST_MULTILINGUAL"'))
            else:
                connection.execute(text("DROP TABLE IF EXISTS plugin_test_multilingual"))
    except Exception:  # noqa: BLE001 - missing table is fine across dialects
        pass
    finally:
        engine.dispose()

    engine = create_database_engine(config)
    try:
        with engine.begin() as connection:
            ddl = {
                "mysql": """
CREATE TABLE plugin_test_multilingual (
  id INTEGER PRIMARY KEY,
  language_code VARCHAR(20) NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  content_text TEXT NOT NULL,
  special_text TEXT NULL,
  long_text TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
""",
                "postgresql": """
CREATE TABLE plugin_test_multilingual (
  id INTEGER PRIMARY KEY,
  language_code VARCHAR(20) NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  content_text TEXT NOT NULL,
  special_text TEXT NULL,
  long_text TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""",
                "dm": """
CREATE TABLE "PLUGIN_TEST_MULTILINGUAL" (
  "ID" INTEGER PRIMARY KEY,
  "LANGUAGE_CODE" VARCHAR(20) NOT NULL,
  "DISPLAY_NAME" VARCHAR(100) NOT NULL,
  "CONTENT_TEXT" CLOB NOT NULL,
  "SPECIAL_TEXT" CLOB NULL,
  "LONG_TEXT" CLOB NULL,
  "CREATED_AT" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
""",
            }[config["database_type"]]
            connection.execute(text(ddl))
            for row in EXPECTED_ROWS:
                connection.execute(text(insert_sql(config["database_type"])), bind_row(row))
    finally:
        engine.dispose()


def insert_sql(database_type: str) -> str:
    if database_type == "dm":
        return """
INSERT INTO "PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT")
VALUES (:ID, :LANGUAGE_CODE, :DISPLAY_NAME, :CONTENT_TEXT, :SPECIAL_TEXT, :LONG_TEXT)
"""
    return """
INSERT INTO plugin_test_multilingual
(id, language_code, display_name, content_text, special_text, long_text)
VALUES (:ID, :LANGUAGE_CODE, :DISPLAY_NAME, :CONTENT_TEXT, :SPECIAL_TEXT, :LONG_TEXT)
"""


def query_and_assert(config: dict[str, Any]) -> dict[str, Any]:
    sql = (
        'SELECT "ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT" '
        'FROM "PLUGIN_TEST_MULTILINGUAL" ORDER BY "ID"'
        if config["database_type"] == "dm"
        else "SELECT id, language_code, display_name, content_text, special_text, long_text "
        "FROM plugin_test_multilingual ORDER BY id"
    )
    result = execute_read_only_query(config, sql, max_rows=100, timeout=30)
    response = success_response(config["database_type"], result)
    rows = normalize_rows(response["rows"])
    assert len(rows) == len(EXPECTED_ROWS), f"expected {len(EXPECTED_ROWS)} rows, got {len(rows)}"
    for expected, actual in zip(EXPECTED_ROWS, rows, strict=True):
        for key in ("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT"):
            assert actual[key] == expected[key], (
                f"{config['database_type']} row {expected['ID']} {key}: "
                f"expected {expected[key]!r}, got {actual[key]!r}"
            )
    response["rows"] = rows
    return response


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "ID": int(row.get("ID", row.get("id"))),
            "LANGUAGE_CODE": row.get("LANGUAGE_CODE", row.get("language_code")),
            "DISPLAY_NAME": row.get("DISPLAY_NAME", row.get("display_name")),
            "CONTENT_TEXT": row.get("CONTENT_TEXT", row.get("content_text")),
            "SPECIAL_TEXT": row.get("SPECIAL_TEXT", row.get("special_text")),
            "LONG_TEXT": row.get("LONG_TEXT", row.get("long_text")),
        }
        for row in rows
    ]


def bind_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in ("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT")}


def summarize(entries: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "pass": sum(1 for entry in entries if entry["status"] == "PASS"),
        "fail": sum(1 for entry in entries if entry["status"] == "FAIL"),
        "skip": sum(1 for entry in entries if entry["status"] == "SKIP"),
    }


def driver_name(database_type: str) -> str:
    return {"mysql": "PyMySQL", "postgresql": "psycopg2", "dm": "dmPython + dmSQLAlchemy"}[database_type]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
