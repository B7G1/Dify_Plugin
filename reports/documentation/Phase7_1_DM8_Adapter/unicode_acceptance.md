# DM8 Unicode Acceptance

## Scope

The ASCII-only bootstrap fixture avoids Windows DIsql script-decoding and
variable-substitution issues. It does not reduce the Unicode requirements of
the DM8 Adapter.

Unicode is accepted at the runtime boundary where production traffic actually
passes: dmPython parameter binding, SQLAlchemy result decoding, Tool JSON
formatting, and Workflow API UTF-8 transport.

## Required cases

- Bind and return `中文测试` without loss or replacement characters.
- Return accented Latin text such as `Léa Martin` unchanged.
- Return Unicode through the Adapter, Tool, and Workflow API paths.
- Preserve Unicode in the existing JSON response schema.
- Keep the runtime account read-only; Unicode verification must not require
  INSERT, UPDATE, DELETE, or DDL privileges.

## Test strategy

Use a parameterized read-only query equivalent to:

```sql
SELECT :unicode_text AS "UNICODE_TEXT" FROM DUAL
```

Bind `unicode_text` through dmPython/SQLAlchemy rather than interpolating it
into SQL. Then assert exact string equality at the Adapter and JSON output
boundaries. A Workflow-level literal query may additionally verify UTF-8 JSON
transport because it does not pass through a DIsql script file.

## Status

**PASS (2026-06-30).** Workflow API case `unicode_utf8` returned `中文测试`
without loss or replacement characters. The archived result is
`reports/verification/2026-06-30/workflow_dm8_result.json`.
