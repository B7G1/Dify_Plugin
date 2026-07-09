# Commit 2E — Multilingual Verification Reproduction Assets Review

Date: 2026-07-07  
Branch: `feature/kingbasees-adapter`  
HEAD: `64e1e26 docs: clarify DM8 Phase 7 evidence boundaries`

Final recommendation: **READY FOR NARROW STAGING**

## 1. Review scope

This review covers only the Commit 2E multilingual reproduction assets and the narrow 2E-0 credential hygiene fix:

- `db_query_extended/verification/verification_runner.py`
- `db_query_extended/verification/import_dm8_multilingual_fixture.ps1`
- `db_query_extended/verification/import_dm8_multilingual_fixture.py`
- `db_query_extended/verification/multilingual_gate_runner.py`

Excluded from this review:

- `db_query_extended/workflow_specs/`
- interactive map files
- Quarto HTML/QMD deletions
- `archive/`
- `analysis/`
- `local_test_db/`
- `release/`
- `.difypkg` files
- `test_tool_schema/`
- Phase 10 / Phase 11 / SQL Server / KingbaseES files
- unrelated report deletions

## 2. Why the three multilingual verification files are reproduction assets

`import_dm8_multilingual_fixture.ps1`, `import_dm8_multilingual_fixture.py`, and `multilingual_gate_runner.py` reproduce the Phase 7.2 multilingual evidence path:

- import deterministic multilingual fixture data;
- validate stored multilingual exact equality;
- preserve the expected 12-row multilingual contract;
- provide repeatable local verification without changing Provider, Tool, Adapter, Workflow, SQL security, or result formatter runtime behavior.

## 3. Why `workflow_specs/` is excluded

`db_query_extended/workflow_specs/` currently contains only:

- `kingbasees_workflow.yaml`
- `README.md`

It does not contain the Phase 7.2 multilingual contract or multilingual reference data. It is therefore not part of Commit 2E.

## 4. 12-row multilingual fixture coverage

The canonical expected rows cover:

- Simplified Chinese (`zh-CN`)
- Traditional Chinese (`zh-TW`)
- English
- Japanese
- Korean
- French / accented Latin
- German umlaut / sharp s
- mixed language
- emoji / supplementary Unicode
- apostrophe, plus sign, percent sign, backslash
- multiline text
- nullable fields
- CLOB / long text fields

## 5. DM8 fixture import admin credential handling

`import_dm8_multilingual_fixture.py` reads administrator / owner connection settings from `DM_ADMIN_*` environment variables.

`import_dm8_multilingual_fixture.ps1` prompts for `DM_ADMIN_PASSWORD` via `Read-Host -AsSecureString` when the variable is absent.

No administrator password value is recorded in this review.

## 6. Found hygiene issue

The review found that both verification runners had a non-empty fallback for `DM_PASSWORD`.

This was a credential hygiene issue in verification infrastructure. It was not Provider, Tool, Adapter, Workflow, SQL safety, or runtime production behavior.

## 7. 2E-0 fix

The fallback was removed from:

- `db_query_extended/verification/verification_runner.py`
- `db_query_extended/verification/multilingual_gate_runner.py`

Both runners now require explicit `DM_PASSWORD` only when the DM configuration is actually selected or used.

Failure behavior is fail-closed:

- error names `DM_PASSWORD`;
- no password value is printed;
- no old fallback value is printed;
- no password is guessed or copied from files/history.

## 8. Non-DM isolation gate

Result: **PASS**

With `DM_PASSWORD` removed from the current PowerShell session:

- `verification_runner.py` can resolve MySQL config;
- `verification_runner.py` can resolve PostgreSQL config;
- `multilingual_gate_runner.py` can resolve MySQL config;
- `multilingual_gate_runner.py` can resolve PostgreSQL config;
- no `DM_PASSWORD` required error is triggered for MySQL/PostgreSQL-only paths.

## 9. DM fail-closed gate

Result: **PASS**

With `DM_PASSWORD` removed from the current PowerShell session:

- selecting DM fails explicitly;
- the error message names `DM_PASSWORD`;
- the error message does not contain a password value;
- the old fallback is not emitted.

## 10. py_compile / CLI help gates

Result: **PASS**

Commands executed from `E:\Dify_Plugin\db_query_extended`:

```powershell
.\.venv\Scripts\python.exe -m py_compile `
  .\verification\verification_runner.py `
  .\verification\multilingual_gate_runner.py `
  .\verification\import_dm8_multilingual_fixture.py

.\.venv\Scripts\python.exe .\verification\verification_runner.py --help
.\.venv\Scripts\python.exe .\verification\multilingual_gate_runner.py --help
```

All completed successfully.

## 11. Production impact analysis

- `verification_runner.py` is verification infrastructure.
- `multilingual_gate_runner.py` is verification infrastructure.
- `import_dm8_multilingual_fixture.py` is a test fixture import utility.
- `import_dm8_multilingual_fixture.ps1` is a local verification wrapper.

This change does not modify:

- Tool JSON Contract;
- shared SQL Security;
- MySQL adapter implementation;
- PostgreSQL adapter implementation;
- DM adapter implementation;
- KingbaseES preview adapter;
- Provider behavior;
- Tool behavior;
- Workflow contract.

This review does not claim a new Workflow/API/UI PASS.

## 12. Final recommendation

**READY FOR NARROW STAGING**

Suggested staging allowlist:

```text
db_query_extended/verification/verification_runner.py
db_query_extended/verification/import_dm8_multilingual_fixture.ps1
db_query_extended/verification/import_dm8_multilingual_fixture.py
db_query_extended/verification/multilingual_gate_runner.py
reports/documentation/Phase7_4_Release_Staging_Hygiene/commit2e_multilingual_reproduction_assets_review_2026-07-07.md
```

Do not stage:

```text
db_query_extended/workflow_specs/
db_query_extended_interactive_map/
Dify本地化插件制作流程_最新整理版.*
archive/
analysis/
local_test_db/
release/
*.difypkg
test_tool_schema/
reports/documentation/Phase10_KingbaseES_Adapter/
reports/documentation/Phase11_Database_Expansion/
reports/documentation/Phase11_SQLServer_Adapter/
historical report deletions
```
