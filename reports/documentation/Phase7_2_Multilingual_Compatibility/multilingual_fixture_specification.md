# Multilingual Fixture Specification

Fixture table:

```text
PLUGIN_TEST_MULTILINGUAL
```

Canonical logical fields:

```text
ID
LANGUAGE_CODE
DISPLAY_NAME
CONTENT_TEXT
SPECIAL_TEXT
LONG_TEXT
CREATED_AT
```

Canonical expected fixture SHA-256:

```text
f901d5099bdfd3c4ef6eb98ccb963b48356c8ff2f45e361aed91ab8d8a675a7f
```

Coverage:

| ID | Code | Class |
| --- | --- | --- |
| 1 | zh-CN | Simplified Chinese |
| 2 | zh-TW | Traditional Chinese |
| 3 | en | English |
| 4 | ja | Japanese |
| 5 | ko | Korean |
| 6 | fr | Accented Latin / French |
| 7 | de | German umlaut / ß |
| 8 | mixed | Mixed-language Unicode |
| 9 | emoji | Emoji / supplementary Unicode |
| 10 | special | Apostrophe, plus, percent, backslash |
| 11 | newline | Multiline text |
| 12 | null | Nullable multilingual fields |

Implementation files:

- Runner and canonical expected values: `db_query_extended/verification/multilingual_gate_runner.py`
- DM8 admin import SQL: `local_test_db/dm8/04_multilingual_fixture.sql`

Current database execution:

- MySQL and PostgreSQL fixtures are created automatically by the runner.
- DM8 fixture setup is complete for Phase 7.2. A local DM8 administrator used `C:\dmdbms\bin\disql.exe` interactively as `DIFY_TEST` to grant `CREATE TABLE` to `PLUGIN_TEST_OWNER`; grant verification returned `PLUGIN_TEST_OWNER / CREATE TABLE / ADMIN_OPTION NO`.
- The `DIFY_TEST` password is not recorded and must not be added to evidence.
- The normal adapter/provider/tool/workflow path still uses `PLUGIN_TEST_USER`.
- DM8 fixture import command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verification\import_dm8_multilingual_fixture.ps1`.
- DM8 fixture import result: `{"status": "PASS", "duration_ms": 582}`.
- DM8 exact equality machine evidence: `reports/verification/2026-07-07/multilingual_dm_result.json` with `{"pass": 1, "fail": 0, "skip": 0}`.
