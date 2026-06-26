# 开发环境与测试资源记录

记录时间：2026-06-21。本记录只描述当前项目环境；未改动全局 Python、Anaconda、其他项目或 Dify 容器配置。

## 开发依赖状态

| 项目 | 状态 / 版本 | 说明 |
|---|---|---|
| Python | Python 3.11.0 | 项目解释器为 `E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe`，基于 `E:\python.exe` 创建。 |
| Poetry | 未安装 | 未修改全局环境；本项目使用隔离 `.venv` 和 `requirements.txt`。 |
| Dify Plugin CLI | v0.6.1 | `E:\Dify_Plugin\dify-plugin.exe`；已完成 init、checksum 与 package。 |
| Dify Plugin SDK | 0.6.2 | 已安装至项目 `.venv`。 |
| SQLAlchemy | 2.0.51 | 用于连接、`SELECT 1` 验证及查询执行。 |
| PyMySQL | 1.2.0 | MySQL SQLAlchemy 驱动。 |
| psycopg | 3.3.4 | 已安装并保留；当前 Windows + Dify SDK/gevent 组合下不用于运行时连接。 |
| psycopg2-binary | 2.9.12 | PostgreSQL SQLAlchemy 兼容驱动，用于当前运行时实现。 |

## Docker 测试环境

`docker compose up -d` 已完成；`docker compose ps` 显示两个服务均为 **healthy**，没有端口冲突。

| 数据库 | 服务 | 主机端口 | 库名 | 表 | 验证结果 |
|---|---|---:|---|---|---|
| MySQL 8.4 | `mysql` | 3307 | `db_query_test` | `students` | 初始化脚本成功，`SELECT COUNT(*)` 返回 5，`SELECT * ... LIMIT 5` 返回 5 行。 |
| PostgreSQL 16 | `postgres` | 5433 | `db_query_test` | `students` | 初始化脚本成功，`SELECT COUNT(*)` 返回 5，`SELECT * ... LIMIT 5` 返回 5 行。 |

`students` 字段：`id`、`name`、`age`、`major`、`created_at`。初始化脚本位于 `sql/init_mysql.sql` 和 `sql/init_postgres.sql`。账号 `db_query_user` / 密码 `db_query_password` 仅限本地测试，不能复用于共享或生产环境。

## 已知限制

- 当前 manifest 的 runner 元数据仍为 CLI 模板生成的 Python 3.12；本机验证使用 Python 3.11。正式离线交付前必须根据目标 plugin-daemon 的 ABI 重新准备依赖 wheel。
- `psycopg` 3 binary 在当前 Windows + Dify Plugin SDK 0.6.2（gevent）环境触发 selector 冲突，因此 PostgreSQL 的实际连接采用 SQLAlchemy `postgresql+psycopg2` / `psycopg2-binary`。psycopg 3 保留为后续 Linux plugin-daemon 兼容性验证项。
- 当前未连接实际 Dify/plugin-daemon，也未验证 Workflow UI；本次通过 SDK 的 `Tool.from_credentials()` 进行了本地 Provider/Tool 端到端调用。
