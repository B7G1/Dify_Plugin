# db_query_extended v1.0.0 Release Notes

Release date: 2026-07-02  
Product version: `v1.0.0`  
Plugin package version: `0.1.1`  
Project status: **RELEASED**  
Technical baseline: **FROZEN**

## Positioning

v1.0.0 is the first released maintainable baseline of the read-only database query plugin. It freezes the verified Provider → Tool → Adapter → Workflow → Workflow API chain and is the sole base for later database adapters.

## Delivered

- A Dify Provider with validated database credentials.
- A read-only SQL Tool with row limits, timeout handling, JSON-safe output, and dangerous SQL rejection.
- A shared adapter boundary with MySQL, PostgreSQL, and DM8 implementations.
- A published three-node DM8 acceptance Workflow and API validation path.
- Fixed `dify` Compose startup with persistent PostgreSQL and Weaviate named volumes.
- Repeatable Provider, Tool, and Workflow verification driven by `verify_all.ps1`.

## Supported databases

| Database | Status | Scope |
| --- | --- | --- |
| MySQL 8.4 | Supported | local adapter and regression verification |
| PostgreSQL 16 | Supported | local adapter and regression verification |
| DM8 | Supported | real Provider, Workflow, Unicode, API, and dangerous-SQL acceptance |

## Real acceptance

- Provider: 6 PASS
- Tool: 27 PASS
- Workflow: 12 PASS
- Total: **45 PASS / 0 FAIL / 0 SKIP**
- Cold boot, persistent PostgreSQL identity, plugin runtime, and Workflow API were rechecked on 2026-07-01.

API keys, passwords, and tokens are excluded from the release material.
