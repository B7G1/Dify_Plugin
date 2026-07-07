# Cross-Database Multilingual Verification Result

Machine evidence:

```text
reports/verification/2026-07-07/multilingual_mysql_postgresql_result.json
reports/verification/2026-07-07/multilingual_dm_result.json
```

## Summary

| Database | Driver | Result | Evidence |
| --- | --- | --- | --- |
| MySQL | PyMySQL | PASS | 12/12 rows exact text equality. |
| PostgreSQL | psycopg2 | PASS | 12/12 rows exact text equality. |
| DM8 | dmPython + dmSQLAlchemy | PASS | Fixture import PASS; DM8 exact equality gate PASS with `{"pass": 1, "fail": 0, "skip": 0}`. |

## MySQL result

```text
PASS: 12 multilingual stored rows read through plugin query path.
```

Verified exact values include:

- `数据库连接测试`
- `資料庫連線測試`
- `日本語データ検索`
- `한국어 데이터 조회`
- `Café déjà vu — français`
- `Straße München`
- `中文 + English + 日本語 + 한국어`
- `你好，世界 🌍🚀`
- `O'Connor + 100% \\ path`
- `第一行\n第二行`
- JSON `null`

## PostgreSQL result

```text
PASS: 12 multilingual stored rows read through plugin query path.
```

The same canonical values passed exact equality.

## DM8 result

```text
PASS: 12 multilingual stored rows read through the DM8 plugin query path with exact equality.
```

Fixture setup closure:

```text
Admin login path: C:\dmdbms\bin\disql.exe
Admin user used interactively: DIFY_TEST
Command executed: GRANT CREATE TABLE TO "PLUGIN_TEST_OWNER";
Grant verification: PLUGIN_TEST_OWNER / CREATE TABLE / ADMIN_OPTION NO
```

Fixture import:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verification\import_dm8_multilingual_fixture.ps1
```

```json
{"status": "PASS", "duration_ms": 582}
```

DM8 exact equality runner:

```powershell
.\.venv\Scripts\python.exe .\verification\multilingual_gate_runner.py --databases dm --skip-setup --output E:\Dify_Plugin\reports\verification\2026-07-07\multilingual_dm_result.json
```

```json
{"pass": 1, "fail": 0, "skip": 0}
```

Interpretation:

- The previous fixture-import blockage is resolved.
- The administrator account `DIFY_TEST` was used only interactively for local DM8 fixture setup permission.
- No `DIFY_TEST` password is recorded or required in evidence.
- The plugin runtime path still validates the normal adapter/provider/tool/workflow behavior with `PLUGIN_TEST_USER`.
- Failure layer from the earlier run was fixture setup privilege, not DM8 Unicode retrieval.
- DM8 storage, dmPython, dmSQLAlchemy, Adapter, formatter, and JSON serialization are now covered by the machine evidence file `reports/verification/2026-07-07/multilingual_dm_result.json`.
