# Release Notes: db_query_extended 0.1.0

`0.1.0` 是 MySQL/PostgreSQL 只读数据库插件的首个稳定交付版本，也是 Phase 7 国产数据库 Adapter 开发的回归基线。

## Highlights

- MySQL/PostgreSQL Provider 与 Tool 已完成真实数据库验证。
- 数据库内核采用 Adapter 架构，核心执行器无数据库类型分支。
- Dify Workflow API 支持动态 `sql`、`max_rows` 输入和稳定 `result` 输出。
- Provider、Tool、Workflow、JSON Schema 和 SQL 安全可通过一个命令回归。

## Quality Gate

```text
Provider     4 PASS
Tool        20 PASS
Workflow    11 PASS
Total       35 PASS / 0 FAIL / 0 SKIP
```

正向覆盖 SELECT 1、LIMIT、COUNT、WHERE、JOIN 和截断；负向覆盖 DROP、UPDATE、DELETE、ALTER 和 CREATE。

## Compatibility

- Dify：1.13.3（当前验证环境）
- plugin-daemon：0.5.3-local
- Python runner：3.12
- dify_plugin：0.6.2
- SQLAlchemy：2.0.51
- MySQL：8.4 / PyMySQL 1.2.0
- PostgreSQL：16 / psycopg2-binary 2.9.12

## Known Constraints

- Release 包未进行正式签名。
- 本地开发上传需要关闭 plugin-daemon 强制签名验证。
- `NullPool` 和每次调用后 `engine.dispose()` 是当前明确设计，不代表生产连接池方案。
- 不包含 DM8、KingbaseES、Oracle、SQL Server。
- Word 技术复原文档因环境缺少 LibreOffice，只有结构检查，没有页面渲染 QA。

## Upgrade Notes

从历史 `0.0.1` 升级时，Dify 可能重置 Workflow Tool 节点参数。重新绑定 `Start.sql`、`Start.max_rows` 和 End `result` 后重新发布，再执行 `verify_all.ps1`。
