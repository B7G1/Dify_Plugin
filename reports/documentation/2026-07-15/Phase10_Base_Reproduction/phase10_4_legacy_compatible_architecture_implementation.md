# Phase 10.4 — Legacy-Compatible Architecture Implementation

- Date: 2026-07-15
- Phase: Phase 10.4 — Legacy-Compatible Architecture Implementation
- Status: PASS
- Database: No database runtime invoked; Legacy MySQL/PostgreSQL/MSSQL mapping retained; Oracle/Oracle11g remain controlled unsupported
- Scope: Implement only the three Phase 10.3 Legacy boundaries: single-SELECT policy, strict `db_properties`, and sanitized exception re-raise.
- Source commit: `63231ad` at start; Phase 10.4 changes remain uncommitted.
- Runtime: Credential-free Python unit/static Gate; no database, installed plugin, Dify API, Workflow, publish, or API key use.
- Canonical path: `reports/documentation/2026-07-15/Phase10_Base_Reproduction/phase10_4_legacy_compatible_architecture_implementation.md`
- Machine evidence: `reports/verification/2026-07-15/phase10_4_legacy_implementation_gate.json`
- Logs: NOT_APPLICABLE
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / NO_CREDENTIALS

## Executive Summary

Phase 10.4 implements the three decisions frozen in Phase 10.3 without expanding database scope or altering any Workflow. The Legacy path now has its own narrow SQL policy, `db_properties` parser, and exception exit. The Modern Tool, Provider credential schema, adapter registry, and modern structured envelope remain untouched and are checked by the implementation Gate.

`PASS` here is an implementation and credential-free regression result. It is not a Dify installed-plugin runtime result, Oracle/Oracle11g runtime result, DM8/KingbaseES result, or final project delivery result.

## Implemented Call Direction

```text
legacy_database_query
  -> validate_legacy_parameters / LegacySingleSelectValidator
  -> execute_read_only_query
  -> legacy formatter

legacy failure
  -> sanitized DatabaseQueryError
  -> Dify Tool exception handling path
```

The shared `execute_read_only_query` function remains unchanged. No new adapter, connection lifecycle, provider field, Legacy parameter, or Workflow node was introduced.

## 1. Legacy Single-SELECT Policy

`LegacySingleSelectValidator` reuses the existing conservative SQL lexer but has a separate contract from `ReadOnlyValidator`:

| Input | Frozen result |
| --- | --- |
| one `SELECT` | allowed |
| leading comment followed by `SELECT` | allowed |
| one terminal semicolon | allowed, matching original `sqlparse`-style single-statement compatibility |
| two `SELECT` statements | rejected |
| `SELECT ...; DELETE ...` | rejected |
| `SELECT ... INTO ...` | rejected as a safety enhancement |
| `WITH ...` | rejected; Legacy does not silently inherit modern `WITH` behavior |
| non-`SELECT` / DDL / DML | rejected |

This restores the original public acceptance boundary while retaining the existing lexer protections. Rejecting `SELECT INTO` is an explicit safety enhancement, not a claim about original plugin behavior.

## 2. Strict `db_properties`

`parse_legacy_properties` accepts only query-pair syntax and only these keys:

```text
schema
charset
ssl_mode
```

Empty properties are allowed. Any empty/malformed pair, duplicate key, unknown key, or attempt to override `host`, `port`, `username`, `password`, `database`, or `driver` raises a `ParameterValidationError`. Error messages expose at most the property key, never its value.

The parsed values remain a Legacy mapper concern. They do not alter the Modern Provider credential schema and cannot become arbitrary SQLAlchemy URL fragments.

## 3. Legacy Exception Path

The Legacy Tool no longer emits a structured JSON error envelope. Known `DatabaseQueryError` values are re-raised; unexpected exceptions become the sanitized message:

```text
The query request could not be completed.
```

No password, URL, driver message, authorization data, or raw connection detail is copied into this message. Successful Markdown and JSON branches are unchanged: Markdown remains a GitHub table and JSON remains exactly `{"records": [...]}`.

The code-level re-raise path is verified. The installed Dify runtime's wrapping into `PluginInvokeError` was not rerun in this phase because no package installation or Workflow/runtime mutation was in scope.

## Verification

Run from PowerShell in `E:\Dify_Plugin`:

```powershell
python db_query_extended\verification\phase10_4_legacy_implementation_gate.py `
  --output reports\verification\2026-07-15\phase10_4_legacy_implementation_gate.json
```

The Gate passed 26 credential-free checks covering SQL inputs, property parsing, five Legacy database declarations/mapping, Legacy Markdown/JSON shapes, error-source behavior, Modern Tool and Provider schemas, Modern envelope, and the persisted JSON DSL field.

Expected result is exit code 0. A failure means one of the frozen Legacy/Modern contracts changed and must be resolved before packaging or runtime validation; it does not authorize changing a Workflow or adding a new database.

## Files Changed

| File | Responsibility after change |
| --- | --- |
| `utils/sql_validator.py` | adds the narrow `LegacySingleSelectValidator`; Modern validator unchanged |
| `utils/legacy.py` | validates strict Legacy properties and calls Legacy SQL policy before shared execution |
| `tools/legacy_database_query.py` | re-raises known safe exceptions and sanitizes unexpected exceptions instead of producing Legacy error JSON |
| `verification/phase10_4_legacy_implementation_gate.py` | repeatable credential-free implementation Gate |

## Final Decision

```text
PHASE_STATUS: PASS
ALLOWED_CONCLUSIONS:
  - LEGACY_SINGLE_SELECT_POLICY_IMPLEMENTED
  - LEGACY_DB_PROPERTIES_ALLOWLIST_IMPLEMENTED
  - LEGACY_SANITIZED_EXCEPTION_CODE_PATH_IMPLEMENTED
  - LEGACY_AND_MODERN_OUTPUT_CONTRACTS_REMAIN_SEPARATE
NOT_YET_PROVEN:
  - DIFY_PLUGIN_INVOKE_ERROR_RUNTIME_PASS
  - ORACLE_RUNTIME_PASS
  - ORACLE11G_RUNTIME_PASS
  - DM8_NEW_RUNTIME_PASS
  - KINGBASEES_NEW_RUNTIME_PASS
  - FINAL_PROJECT_DELIVERY_PASS
FINAL_DELIVERY_IMPACT: records a reusable compatibility implementation step; no final delivery gate is closed.
NEXT_PHASE: choose an installed-plugin Tool runtime gate before any new database expansion work.
```

### Record classification

- `TUTORIAL_REQUIRED`: separate Legacy SQL/property/error boundaries over a shared execution core.
- `TUTORIAL_REFERENCE`: terminal-semicolon compatibility decision and strict property allowlist.
- `DEVELOPMENT_HISTORY_ONLY`: removal of the interim structured Legacy JSON error behavior.
- `EVIDENCE_ONLY`: 26-check Gate JSON.
- `TEMPORARY`: terminal output and local test values.
