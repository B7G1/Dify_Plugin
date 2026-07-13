# Phase 8.8 — SQL Server Tool Validation Gate

Status: PASS

Machine evidence:

- [sqlserver_tool_validation_gate.json](../../verification/2026-07-09/sqlserver_tool_validation_gate.json)

## Goal

Validate the SQL Server candidate plugin through the real Dify/plugin-daemon tool path, not through mock execution or adapter-only smoke checks.

## Scope actually executed

- Real provider credential validation through the Dify/plugin-daemon runtime
- Real tool execution against the local SQL Server fixture database
- Real output shape checks on tool JSON results

Not executed in this phase:

- main verification matrix integration
- Workflow API
- MySQL/PostgreSQL/DM/Kingbase regression changes
- formatter/security refactor

## Required precondition found during execution

At the start of Phase 8.8, the Dify control plane still pointed to the older installed plugin checksum, even though Phase 8.7 had already proven that the SQL Server candidate package could be decoded, installed, and started by plugin-daemon.

Observed symptom before correction:

- provider schema only exposed `mysql`, `postgresql`, and `dm`
- runtime validation returned `Unsupported database type. Only mysql, postgresql, and dm are available in this phase.`

Minimal correction performed:

- uploaded the existing candidate `.difypkg` again through the real Dify console package upload path
- executed a local Dify plugin upgrade from the old installed checksum to the candidate checksum
- verified that the installed `plugin_unique_identifier` became:

`li_zijun/db_query_extended:0.1.1@4d1e293d9c5df7a8614e7d5e086a6a8a856a7a76accf835bc18ab6736f84af47`

After that correction:

- console provider schema exposed `sqlserver`
- provider info resolved to the candidate checksum
- runtime credential validation passed

This was an environment/control-plane alignment step, not a business-code change.

## Validation target

- Provider: `li_zijun/db_query_extended/db_query_extended`
- Tool: `db_query_extended`
- Credential used: `SQL Server Local Readonly`
- SQL Server test environment: local deterministic fixture

Credential hygiene:

- password was used only during runtime validation
- password is not written into this report
- password is not written into the machine artifact

## Provider credential validation

Result: PASS

Evidence:

- SQL Server credential exists in Dify console provider credentials
- runtime `validate_provider_credentials` returned `True`
- no secret was persisted into evidence

## Real tool execution cases

### 1. `SELECT 1`

Result: PASS

Representative output:

- `columns = ["probe_value"]`
- `rows = [{"probe_value": 1}]`
- `row_count = 1`
- `database_type = "sqlserver"`

### 2. `SELECT TOP 5 ...`

Result: PASS

Representative output:

| id | username | display_name | department |
| --- | --- | --- | --- |
| 1 | alice | Alice | Engineering |
| 2 | zhang_wei | 张伟 | 研发部 |
| 3 | li_na | 李娜 | 财务部 |
| 4 | emoji_user | 测试用户🚀 | NULL |
| 5 | readonly | 只读账号测试 | Quality |

What this proved:

- SQL Server `TOP` syntax works through the real tool path
- Unicode values are returned correctly in normal row payloads
- JSON row serialization is correct

### 3. Unicode fixture read

SQL executed:

```sql
SELECT TOP 3 [id], [event_type], [message]
FROM [plugin_test].[plugin_test_logs]
ORDER BY [id]
```

Result: PASS

Representative output:

| id | event_type | message |
| --- | --- | --- |
| 1 | LOGIN | Alice logged in |
| 2 | 查询 | 中文日志测试 |
| 3 | UNICODE | Unicode 与 Emoji 🚀 |

What this proved:

- stored multilingual SQL Server fixture data was read successfully
- Chinese text and emoji survived the real Dify/plugin-daemon tool path
- output JSON preserved Unicode characters without manual encoding fixes

### 4. Schema-qualified read

SQL executed:

```sql
SELECT COUNT(*) AS [log_count]
FROM [plugin_test].[plugin_test_logs]
```

Result: PASS

Representative output:

- `columns = ["log_count"]`
- `rows = [{"log_count": 3}]`
- `row_count = 1`

What this proved:

- schema-qualified table access works
- SQL Server fixture schema is reachable by the formal adapter path

## Output structure check

Result: PASS

All four real executions returned the required keys:

- `columns`
- `rows`
- `row_count`
- `truncated`
- `max_rows`

Observed output shape remained consistent across all SQL Server cases.

## SQL Server-specific conclusion

Result: PASS

Confirmed in real execution:

- `TOP` query support: PASS
- Unicode fixture read: PASS
- schema-qualified table read: PASS
- `database_type = "sqlserver"` in all real tool outputs: PASS

## Formal adapter vs fallback-path conclusion

Result: PASS

Why this is sufficient:

- current console provider schema includes `sqlserver`
- current installed provider checksum is the SQL Server candidate checksum
- runtime credential validation accepts `database_type = sqlserver`
- SQL Server-specific `TOP` query succeeds
- all returned tool payloads self-identify as `database_type = "sqlserver"`

That combination is consistent with the formal SQL Server adapter path being active, not the earlier MySQL/PostgreSQL/DM-only implementation path.

## Security boundary

- no password written into report
- no auth cookies/tokens written into report
- no provider secret written into machine evidence

Note:

- deterministic local test credentials were used during local validation
- local debugging session cookies existed transiently during Dify console API access and should not be committed anywhere

## Final decision

PASS

PASS criteria satisfied:

- Provider credential validation: PASS
- `SELECT 1`: PASS
- `SELECT TOP 5`: PASS
- Unicode fixture read: PASS
- schema-qualified read: PASS
- output structure assertion: PASS
- no secret leakage in committed evidence: PASS

Phase 8.8 is closed and the SQL Server candidate is validated through the real Dify/plugin-daemon tool execution path.
