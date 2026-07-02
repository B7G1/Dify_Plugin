# db_query_extended

MySQL 与 PostgreSQL 的 Dify Tool Plugin。`0.1.0` 是完成 Adapter 架构冻结和 Workflow API 自动化后的首个稳定交付基线。

## 当前支持范围

- MySQL：SQLAlchemy + PyMySQL
- PostgreSQL：SQLAlchemy + psycopg2-binary（当前 Dify SDK/gevent 的 Windows 兼容路线）
- Provider：参数校验、真实驱动连接、`SELECT 1`
- Tool：单条只读 SQL、行数限制、查询超时、JSON 结果
- 结果：稳定 JSON Schema，包含 `columns`、`row_count`、`rows`、`truncated`、`max_rows` 和错误结构
- 自动化：`verification/verify_all.ps1` 一键验证 Provider、Tool、Workflow API、JSON Schema 和 SQL 安全

不支持写操作、DM8、KingbaseES、Oracle 或 SQL Server。DM8/KingbaseES 属于 Phase 7，不包含在 `0.1.0`。

## Release 0.1.0

- 冻结日期：2026-06-29
- 验证结果：35 PASS / 0 FAIL / 0 SKIP
- Release 目录：[`../release/db_query_extended/0.1.0/`](../release/db_query_extended/0.1.0/README.md)
- 变更历史：[`../CHANGELOG.md`](../CHANGELOG.md)

## 标准本地测试数据库

Day 2 的标准环境位于工作区根目录的 `local_test_db/`，使用 MySQL 8.4 和 PostgreSQL 16，数据库均为 `plugin_test`。Docker Desktop 可用时执行：

```powershell
Set-Location E:\Dify_Plugin\local_test_db
.\verification\verify.ps1
```

MySQL：`127.0.0.1:3306`；PostgreSQL：`127.0.0.1:5432`。详细连接信息、初始化数据和验收 SQL 见 [../local_test_db/README.md](../local_test_db/README.md)。本目录保留的 `docker-compose.yml` 与 `sql/` 是既有开发资料，不再作为标准联调环境。

## 稳定契约

Provider 表单负责数据库连接配置，包括数据库类型、主机、端口、数据库、用户名、密码、连接超时和 SSL 模式。Tool 只接受单条 `SELECT` 或 `WITH ... SELECT`，默认限制 100 行和 30 秒，并返回结构化 JSON。完整验证证据见 [`../reports/verification/2026-06-29/`](../reports/verification/2026-06-29/README.md)。

详细环境、依赖和限制见 [docs/dev_environment.md](docs/dev_environment.md)；实现说明见 [docs/plugin_skeleton.md](docs/plugin_skeleton.md)。
