# Zero Manual Encoding Intervention Assessment

Product acceptance target:

```text
User selects database type, fills normal connection fields, enters SELECT SQL, and runs.
No manual encoding conversion is required.
```

## Current status

| Database | Status | Evidence |
| --- | --- | --- |
| MySQL | PASS | Runner inserted and read stored multilingual data without user encoding commands. |
| PostgreSQL | PASS | Runner inserted and read stored multilingual data without user encoding commands. |
| DM8 | PASS | Admin-only fixture setup was completed once; the DM8 exact equality runner then read stored multilingual data through the normal plugin query path without user encoding commands. Machine evidence: `reports/verification/2026-07-07/multilingual_dm_result.json`. |

## DM8 account boundary

`DIFY_TEST` was used only interactively as a local DM8 database administrator to grant fixture setup permission to `PLUGIN_TEST_OWNER`. No `DIFY_TEST` password is recorded. The adapter/provider/tool/workflow path continues to use `PLUGIN_TEST_USER`, preserving the normal product read-only credential boundary.

## Explicitly not required in passing paths

- No `chcp 65001`.
- No PowerShell `$OutputEncoding` change by end user.
- No manual `.encode()` / `.decode()` repair.
- No Workflow modification for each language.
- No per-language Adapter switch.
- No SQL-side conversion wrapper.

## Product improvement note

The Provider currently exposes optional `charset` in normalized credentials but the YAML does not surface it as a user-facing field. That is acceptable for the current gate because MySQL, PostgreSQL, and DM8 passed without user charset input. If future MySQL deployments need explicit charset, prefer adapter defaulting to `utf8mb4` over asking ordinary users to understand encoding.
