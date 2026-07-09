# 05｜本地插件开发环境与 PostgreSQL 联调（2026-06-23）

## 1. 今日目标

在不实现 DM 支持、不改插件源码、不重置 Dify 数据的前提下：

1. 核验 Python 3.11、Poetry、插件 SDK 与数据库驱动；
2. 核验 Dify 源码/服务状态；
3. 搭建或复用独立 PostgreSQL 测试库，并接入 Dify 网络；
4. 用 `db_query_extended` 完成 PostgreSQL Provider 校验；
5. 尝试最小 Workflow 联调。

## 2. 已完成项

- Dify 最小重建平台仍可用；`dify-nginx-1`、`dify-api-1`、`dify-web-1`、`dify-worker-1`、`dify-plugin_daemon-1`、`dify-redis-1`、`dify-db_postgres-1` 均为运行状态。
- `db_query_extended 0.0.1` 保持已安装；未卸载、未重装、未修改源码。
- 复用已有 `db-query-extended-postgres` 容器，启动后接入 `dify_default` 网络，别名为 `plugin-test-postgres`。
- 在独立测试库创建 `plugin_test_users`，写入 5 条测试数据。
- daemon 到 `plugin-test-postgres:5432` 的 TCP 连接成功。
- 已通过 Dify Provider 表单保存并成功校验 PostgreSQL 测试凭据；浏览器显示“操作成功”，API 与 daemon 均记录 `dispatch/tool/validate_credentials` HTTP 200。
- 创建了测试 Workflow 应用：`db_query_extended PostgreSQL 联调`（ID：`4e187e74-b491-403f-8414-0280088442cb`）。

未执行的动作：未实现 DM；未修改 `provider.yaml`、`provider.py`、requirements、wheels；未清空 Dify 数据/volume；未执行 `docker compose down -v`。

## 3. Python 3.11 / pip / Poetry / SDK / 驱动

### Windows 基础 Python

命令：

```powershell
py -3.11 -c "import sys; print(sys.executable); print(sys.version)"
py -3.11 -m pip --version
```

结果：

```text
Python: E:\python.exe
Version: 3.11.0
Base pip: No module named pip
```

结论：Windows 基础 Python 3.11 可用，但基础解释器未安装 pip。该项不阻塞当前插件，因为项目虚拟环境已有可用 pip 和依赖；本次未向基础解释器安装 pip，避免改变全局环境。

### Poetry

命令：

```powershell
poetry --version
```

结果：

```text
Poetry (version 2.4.1)
```

`db_query_extended` 当前是 `requirements.txt + .venv` 项目，并没有 `pyproject.toml`；`poetry env info` 因此返回“could not find a pyproject.toml”。Poetry 本身已安装，但当前项目未采用 Poetry 项目管理。这不阻塞 Dify 插件本地开发。

### 项目虚拟环境与导入

解释器：

```text
E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe
Python 3.11.0
```

导入验证：

```text
dify_plugin=0.6.2
SQLAlchemy=2.0.51
PyMySQL=1.2.0
psycopg2-binary=2.9.12
```

命令退出码为 0。Python 进程退出时出现 gevent logging finalization 警告；它不影响 import 成功或插件 runtime。

## 4. Dify 源码与服务状态

源码目录：

```text
/home/zli2759/projects/dify-dm
```

分支：

```text
dm-adaptation
```

工作树已有用户改动（本次未触碰）：

```text
M api/core/plugin/impl/plugin.py
?? outputs/
```

核心服务状态：

```text
dify-nginx-1           Up (80/443)
dify-api-1             Up
dify-web-1             Up
dify-worker-1          Up
dify-plugin_daemon-1   Up (5002/5003)
dify-redis-1           Up (healthy)
dify-db_postgres-1     Up (healthy)
```

另有历史遗留 `docker-*` 容器，其中 `docker-api-1` 仍是失败循环的第二套环境；本次未停止或修改它们，以避免扩大变更。

## 5. PostgreSQL 测试库

### 容器与网络

复用容器：

```text
db-query-extended-postgres
image: postgres:16
host mapping: 5433 -> 5432
network alias in dify_default: plugin-test-postgres
```

执行：

```bash
docker start db-query-extended-postgres
docker network connect --alias plugin-test-postgres dify_default db-query-extended-postgres
docker exec dify-plugin_daemon-1 sh -lc \
  "timeout 5 bash -c '</dev/tcp/plugin-test-postgres/5432' && echo POSTGRES_TCP_REACHABLE"
```

结果：

```text
POSTGRES_TCP_REACHABLE
```

### 测试数据

库已有配置：

```text
database: db_query_test
username: db_query_user
password: db_query_password
```

幂等建表/灌数后：

```sql
SELECT * FROM plugin_test_users ORDER BY id;
```

返回 5 行：`alice`、`bob`、`carol`、`dave`、`eve`。

直接 PostgreSQL 验证：

```sql
SELECT 1 AS connection_ok;                 -- 1
SELECT * FROM plugin_test_users LIMIT 5;   -- 5 rows
```

MySQL：已有 `db-query-extended-mysql` 测试容器，但当前处于停止状态。本日保底 PostgreSQL 联调已完成，未启动 MySQL，避免增加不必要的运行状态。

## 6. db_query_extended Provider 校验

在 Dify 的“前往修复 / API Key 授权配置”表单中，实际填写的 PostgreSQL 测试配置：

| 字段 | 值 |
| --- | --- |
| database_type | `postgresql` |
| host | `plugin-test-postgres` |
| port | `5432` |
| database | `db_query_test` |
| username | `db_query_user` |
| password | `db_query_password`（仅本地测试库） |
| schema | `public` |
| charset | 留空 |
| connect_timeout | `10` |

结果：Dify 页面显示“操作成功”。日志证据：

```text
API -> POST /plugin/<tenant>/dispatch/tool/validate_credentials  HTTP 200
daemon -> POST /plugin/<tenant>/dispatch/tool/validate_credentials  HTTP 200 (170 ms)
```

业务库的 `tool_builtin_providers` 现有两条记录：早先失败记录 `difyai123456` 以及新的 `plugin-test-postgres`；两条的 `encrypted_credentials` 均存在。当前两条记录的 `is_default` 都为 `false`，但 Dify UI 将可用凭据展示为“默认”。因此本版本不能把该列单独作为 Provider 成功/失败判断；本次成功以页面“操作成功”和 API/daemon 校验链路为准。

## 7. Workflow 调用结果

已创建最小 Workflow 应用并进入画布。由于当前浏览器自动化表面没有暴露画布节点的可定位控件，且画布截图请求超时，未继续依靠猜测坐标添加 Tool 节点；因此下面两条**尚未从 Workflow 节点实际执行**：

```sql
SELECT 1;
SELECT * FROM plugin_test_users LIMIT 5;
```

工具 Python 实现已核对：`tools/db_query_extended.py` 会调用 `execute_read_only_query`，并非仅静态参数校验。也就是说，手动在该 Workflow 中添加“只读 SQL 查询”工具后，上述 SQL 应触发 PostgreSQL 实际读取；Provider 凭据与网络前置条件已满足。

## 8. 未完成项

1. Windows 基础 Python 3.11 的 pip 未安装；项目 `.venv` 的 pip/依赖可用，当前不构成阻塞。
2. 项目未采用 Poetry（无 `pyproject.toml`）；Poetry 已安装但未接管项目环境。
3. MySQL 测试库未重新启动和联网。
4. Workflow Tool 节点尚未添加/运行，因画布自动化元素不可定位而暂停。
5. 未实现 DM 支持，符合今日范围。

## 9. 下一步计划

1. 在已创建的 Workflow 画布中，手动添加 `db_query_extended / 只读 SQL 查询` 节点，选择 `plugin-test-postgres` 凭据。
2. 分别运行 `SELECT 1;` 与 `SELECT * FROM plugin_test_users LIMIT 5;`，观察输出和 `dify-api-1` / `dify-plugin_daemon-1` 日志。
3. 若需覆盖 MySQL，再启动已有 MySQL 测试容器、连接 `dify_default`、创建同名测试表并重复 Provider 校验。
4. 仅在未来明确需要 DM 时，另开任务设计驱动、声明、离线 wheels 与重装方案；本日不实现。
