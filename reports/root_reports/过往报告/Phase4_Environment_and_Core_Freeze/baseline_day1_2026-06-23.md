# Day1 Baseline Snapshot — 2026-06-23

## 目的

此快照记录 Day1 结束时已验证的工作状态，供后续环境恢复、差异比对和故障定位使用。它是**记录**，不是部署或回滚脚本。本次生成没有修改插件源码、Git 历史、Dify 数据库、volume、容器或已安装插件。

## 1. 环境版本

| 项目 | 基线值 | 验证方式 |
| --- | --- | --- |
| 项目 Python | 3.11.0 | `db_query_extended/.venv/Scripts/python.exe --version` |
| Poetry | 2.4.1 | `poetry --version` |
| dify_plugin | 0.6.2 | project venv import / pip metadata |
| SQLAlchemy | 2.0.51 | project venv import / pip metadata |
| PyMySQL | 1.2.0 | project venv import / pip metadata |
| psycopg2-binary | 2.9.12 | project venv import / pip metadata |

完整环境导出：

- [python_3_11.txt](logs/environment_snapshot/python_3_11.txt)
- [poetry.txt](logs/environment_snapshot/poetry.txt)
- [pip_freeze_plugin_venv.txt](logs/environment_snapshot/pip_freeze_plugin_venv.txt)

说明：Windows 基础 Python `E:\python.exe` 可运行 Python 3.11，但未安装基础 pip；项目开发应使用已验证的 `.venv`。

## 2. Dify 状态

### 源码与 Git 快照

```text
project path : /home/zli2759/projects/dify-dm
branch       : dm-adaptation
HEAD         : 14652f90edc3f0c72232761270ad33ca7ee2c561
```

采集命令：

```bash
git branch --show-current
git rev-parse HEAD
git status --short
```

采集时工作树状态（属于既有用户改动，未由本基线任务修改）：

```text
 M api/core/plugin/impl/plugin.py
?? outputs/
```

### 关键服务

| 容器 | 基线状态 |
| --- | --- |
| `dify-nginx-1` | Up，宿主机 80/443 |
| `dify-api-1` | Up |
| `dify-web-1` | Up |
| `dify-worker-1` | Up |
| `dify-plugin_daemon-1` | Up，宿主机 5002/5003 |
| `dify-redis-1` | Up / healthy |
| `dify-db_postgres-1` | Up / healthy |
| `dify-weaviate-1` | Up |

注意：另有 `docker-*` 第二套历史容器；它们不属于本基线已验证的 `dify-*` 平台链路，未在本任务中修改。

## 3. 插件状态

| 项目 | 基线值 |
| --- | --- |
| 插件 ID | `li_zijun/db_query_extended` |
| 版本 / 唯一标识 | `0.0.1@2a4674e9110d590803d26b26bbaa2e1a32dc2a6c111b6703029a53b0d1ea0147` |
| 安装类型 | `local` |
| Runtime 类型 | `local` |
| Provider | `db_query_extended` |
| Tool | `db_query_extended`（只读 SQL 查询） |
| 当前支持类型 | `mysql`、`postgresql` |
| 不支持类型 | DM / Dameng / 达梦、KingbaseES |

已验证：插件安装、Provider declaration、Tool installation、API 到 daemon 的 `management/tool` / `management/tools` 均正常。daemon runtime 已启动且记录 `Installed tool: db_query_extended`。

Provider 凭据：存在一条已成功校验的本地 PostgreSQL 测试凭据 `plugin-test-postgres`。业务库表的两条相关记录均显示 `is_default=false`，但 Dify UI 将可用凭据标记为“默认”；以 UI 的成功反馈、API/daemon `validate_credentials` 200 作为本基线的有效性证据。

## 4. PostgreSQL 测试数据库状态

| 项目 | 基线值 |
| --- | --- |
| 容器 | `db-query-extended-postgres` |
| 镜像 | `postgres:16` |
| 状态 | Up / healthy |
| Dify 网络 | `dify_default` |
| daemon 访问别名 | `plugin-test-postgres` |
| 容器端口 | 5432 |
| 宿主机映射 | 5433 -> 5432 |
| 测试数据库 | `db_query_test` |
| 测试表 | `plugin_test_users` |
| 测试行数 | 5 |

测试数据用户名：`alice`、`bob`、`carol`、`dave`、`eve`。

已验证：

```text
dify-plugin_daemon-1 -> plugin-test-postgres:5432 TCP: reachable
SELECT 1: success
SELECT * FROM plugin_test_users LIMIT 5: 5 rows returned
```

## 5. 已验证功能

| 功能 | 基线结果 | 证据 |
| --- | --- | --- |
| Provider Validation | PASS | Dify UI 显示“操作成功” |
| API | PASS | `dispatch/tool/validate_credentials` HTTP 200 |
| plugin daemon | PASS | 同一 dispatch HTTP 200；runtime ready |
| PostgreSQL Query | PASS（测试库直接验证） | `SELECT 1` 与 5 行查询成功 |
| Workflow Tool 实际执行 | 未完成 | 测试 Workflow 已创建，画布 Tool 节点未实际运行 |

Workflow 应用基线：

```text
name: db_query_extended PostgreSQL 联调
id:   4e187e74-b491-403f-8414-0280088442cb
```

## 6. 已知风险

### 风险 1：Dify PostgreSQL 历史数据丢失原因尚未定位

- **等级：高**
- 当前 Dify 业务库在恢复窗口被重新初始化；旧业务数据和可回滚 volume 尚未找到。
- 后续不要将当前最小重建状态误判为昨天完整业务状态。
- 建议：对 Dify bind-mount 数据目录建立定期、离线、可验证的逻辑备份和文件系统快照。

### 风险 2：db_query_extended 不支持 DM

- **等级：中**
- 当前声明、校验逻辑、SQLAlchemy URI 和离线依赖仅覆盖 MySQL/PostgreSQL。
- 不要将 DM 5236 连接参数填入 MySQL/PostgreSQL Provider。
- DM 支持需要独立设计、驱动/wheels、代码、打包与重新安装流程。

### 风险 3：Workflow Tool 实际执行尚未完成

- **等级：低**
- Provider 与 PostgreSQL 连通性已成功；但尚未在 Workflow 节点中执行 `SELECT 1` 或 `SELECT * FROM plugin_test_users LIMIT 5`。
- 下一步：在基线 Workflow 中手动添加“只读 SQL 查询”节点，选择 `plugin-test-postgres` 凭据并运行这两条 SQL。

### 风险 4：平台存在第二套 `docker-*` 容器

- **等级：中**
- 该套容器此前造成 localhost 入口/API 误指向，且 `docker-api-1` 曾处于数据库 DNS 失败循环。
- 当前正确平台入口是 `dify-nginx-1 -> dify-web-1 / dify-api-1`。
- 后续清理前应先显式确认第二套容器无业务依赖，并避免 `down -v`。

## 7. 基线使用方式

环境异常后，优先逐项比对：

```bash
# Dify source
cd /home/zli2759/projects/dify-dm
git branch --show-current
git rev-parse HEAD
git status --short

# Containers
docker ps

# Plugin runtime
docker logs dify-plugin_daemon-1 --tail 200

# Test database
docker ps --filter name=db-query-extended-postgres
docker exec -e PGPASSWORD=<test-password> db-query-extended-postgres \
  psql -U db_query_user -d db_query_test -c "SELECT count(*) FROM plugin_test_users;"
```

与本报告不一致时，先记录差异与时间，不要立即重装插件、重建数据库或执行 `docker compose down -v`。
