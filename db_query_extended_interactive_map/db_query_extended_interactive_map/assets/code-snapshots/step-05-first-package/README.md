# db_query_extended

MySQL 与 PostgreSQL 的 Dify Tool Plugin。当前支持 Provider 真实连通性校验与单次只读 SQL 查询，适用于后续 Workflow 节点集成。

## 当前支持范围

- MySQL：SQLAlchemy + PyMySQL
- PostgreSQL：SQLAlchemy + psycopg2-binary（当前 Dify SDK/gevent 的 Windows 兼容路线）
- Provider：参数校验、真实驱动连接、`SELECT 1`
- Tool：单条只读 SQL、行数限制、查询超时、JSON 结果
- 结果：`columns`、`row_count`、`rows`、`truncated`、`max_rows`

不支持写操作、DM、KingbaseES、Oracle、SQL Server，也尚未完成 Dify Workflow UI 联调。

## 本地测试数据库

Docker Desktop 可用时，在本目录执行：

```powershell
docker compose up -d
docker compose ps
```

MySQL：`127.0.0.1:3307`；PostgreSQL：`127.0.0.1:5433`。两库名称均为 `db_query_test`，并初始化 `students` 表及 5 条学生数据。

本地开发凭据仅用于测试：`db_query_user` / `db_query_password`，不得用于生产或共享环境。

详细环境、依赖和限制见 [docs/dev_environment.md](docs/dev_environment.md)；实现说明见 [docs/plugin_skeleton.md](docs/plugin_skeleton.md)。
