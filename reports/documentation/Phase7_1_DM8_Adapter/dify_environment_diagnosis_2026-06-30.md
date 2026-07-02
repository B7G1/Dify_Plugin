# Dify 本地环境持久化诊断报告

诊断时间：2026-06-30 01:18-01:40（America/Chicago）  
范围：Dify 主业务数据库、插件数据库、Compose 项目与持久化挂载  
结论状态：旧 Console 数据未恢复；2026-06-30 新稳定基线与 DM8 Workflow API 验收均已通过；Phase 7.1 PASS

## 结论摘要

`http://localhost/install` 反复要求创建管理员，不是 `db_query_extended` 代码导致。当前对外服务连接的 `dify` 主库虽然已完成表结构迁移，但 `accounts=0`、`tenants=0`，因此 Web 正确地进入首次安装流程。

当前 PostgreSQL 容器中的 `PGDATA=/var/lib/postgresql/data/pgdata` 在 2026-06-30 01:17 新建。现有 Docker 容器和 named volume 中未找到另一份 Dify PostgreSQL 数据目录。可确认的直接原因是：当前 `dify-db_postgres-1` 挂载到的是一份新初始化的数据目录，原管理员和租户数据不在当前有效挂载中。

导致该状态的上层原因高度疑似为 Compose 项目和启动上下文混用：现场同时存在 `dify` 与 `docker` 两个由同一主 Compose 文件创建的项目；PostgreSQL 容器标签中的工作目录和数据源使用 `\\wsl.localhost\Ubuntu\...`，其他 Dify 服务多使用 `/home/zli2759/...`。主 Compose 又使用相对 bind mount `./volumes/db/data`，且没有 `.env` 固定 `COMPOSE_PROJECT_NAME`。这些因素使不同入口启动时更容易得到不同的项目名或不同的路径解析结果。

目前没有证据证明是初始化 SQL 主动清空了管理员。更符合现场证据的解释是：旧数据目录未被当前容器挂载，或 bind mount 对应目录曾缺失/被重建，从而触发 PostgreSQL 在 01:17 初始化新 `pgdata`。由于没有旧数据卷变更日志或备份记录，无法进一步断言旧目录是被删除、移动，还是因路径上下文变化而失联。

## 现场容器与项目

当前 Compose 项目：

| 项目 | 状态 | 用途 |
|---|---|---|
| `dify` | 11 个服务运行，1 个一次性服务退出 | 当前对外 Dify 环境 |
| `docker` | 8 个服务已停止 | 误用默认项目名产生的重复 Dify 环境 |
| `dify-plugin-local-test-db` | 2 个服务运行 | MySQL/PostgreSQL 插件测试库，不属于 Dify 主库 |
| `db_query_extended` | 2 个旧测试服务退出 | 旧版插件测试容器 |

`docker-*` 项目已停止，但没有删除容器或 volume。`dify-plugin-local-test-db` 保留运行，因为它承载插件回归所需的 MySQL/PostgreSQL 测试数据。

## localhost 实际服务链路

当前唯一绑定宿主机 80/443 的容器是 `dify-nginx-1`：

```text
localhost:80/443
  -> dify-nginx-1 (Compose project: dify)
  -> dify-api-1 / dify-web-1
  -> db_postgres (dify_default network)
  -> dify-db_postgres-1
```

`dify-api-1` 与 `dify-db_postgres-1` 均连接 `dify_default`。API 的有效数据库配置为：

```text
DB_TYPE=postgresql
DB_HOST=db_postgres
DB_PORT=5432
DB_DATABASE=dify
DB_USERNAME=postgres
```

插件守护进程的有效配置为：

```text
DB_HOST=db_postgres
DB_PORT=5432
DB_DATABASE=dify_plugin
DB_DEFAULT_DATABASE=dify_plugin
```

## PostgreSQL 挂载与数据状态

`dify-db_postgres-1` 使用 bind mount，不是 named volume：

```text
Source:      \\wsl.localhost\Ubuntu\home\zli2759\projects\dify-dm\docker\volumes\db\data
Destination: /var/lib/postgresql/data
PGDATA:      /var/lib/postgresql/data/pgdata
```

数据库检查结果：

| 检查项 | 结果 |
|---|---|
| `dify` 数据库 | 存在 |
| `dify_plugin` 数据库 | 首次检查缺失；补建后存在 |
| `dify` public 表 | 117 张 |
| `dify.accounts` | 0 行 |
| `dify.tenants` | 0 行 |
| `dify_plugin` public 表 | 13 张 |
| 当前 `PG_VERSION` | PostgreSQL 15，目录创建于 2026-06-30 01:17 |

`dify_plugin` 缺失曾导致 `dify-plugin_daemon-1` restart loop。补建后 daemon 恢复，日志出现 `local runtime ready`，Console ping 返回 HTTP 200。

## Compose 配置对比

主 Compose：`/home/zli2759/projects/dify-dm/docker/docker-compose.yaml`

- 未发现同目录 `.env`，只有 `.env.example`。
- 未固定 `COMPOSE_PROJECT_NAME`。
- 主库默认名为 `dify`。
- 插件库默认名为 `dify_plugin`。
- Postgres 使用相对路径 `./volumes/db/data:/var/lib/postgresql/data`。
- `PGDATA` 默认为 `/var/lib/postgresql/data/pgdata`。

plugin daemon override：`/home/zli2759/projects/dify-dm/outputs/dm_change_matrix/regression_scripts/plugin_daemon.local.override.yaml`

- 数据库主机为 `db_postgres`。
- 数据库名和默认数据库均为 `dify_plugin`。
- 本地开发环境关闭插件签名强制校验。

项目目录内另外发现 TiDB Compose 和插件运行时缓存中的 Compose；它们没有绑定 localhost 80/443，也不是当前 Dify 主 PostgreSQL 来源。工作区的 `local_test_db/docker-compose.yml` 仅承载插件测试库。

## 第二个阻塞：应用存储权限

当前 `/app/api/storage` 初始所有者为 `root:root`，API 进程以 `uid=1001(dify)` 运行。管理员初始化请求在生成租户 RSA 私钥时失败：

```text
opendal.exceptions.PermissionDenied
path: privkeys/<tenant-id>/private.pem
```

因此即便在 `/install` 填写管理员，事务也会回滚，`accounts` 仍为 0。`init_permissions` 因检测到旧的初始化标志而输出 `Permissions already initialized. Exiting.`，没有修复新建/替换后的空 storage 目录。现场已将该目录所有权修正为 `1001:1001` 并验证可写，但尚未再次提交管理员初始化。

## 根因分级

1. 已证实直接原因：当前有效 `dify` 库没有管理员和租户数据，因此 `/install` 必然出现。
2. 已证实持久化异常：当前 `pgdata` 于 01:17 新初始化，原业务数据不在当前挂载中。
3. 高度疑似上层原因：同一 Compose 文件曾分别以 `dify` 和默认 `docker` 项目名启动，并混用 Linux 路径与 WSL UNC 路径；相对 bind mount 增加了路径解析漂移风险。
4. 已证实的恢复阻塞：应用 storage 权限错误使管理员重新初始化失败。
5. 未发现证据：没有证据表明 `db_query_extended`、DM8 Adapter、MySQL/PostgreSQL 测试库或 Dify 初始化 SQL主动删除了主库账号。

## 固定方案

### 立即执行

1. 所有 Dify 命令统一使用 `docker compose -p dify`，并固定主 Compose 与 plugin daemon override。
2. 保持 `docker-*` 项目停止；不删除其容器和 volume，直到确认不再需要取证。
3. 使用 `verification/start_dify.ps1` 作为唯一启动入口。
4. 启动前运行 `verification/dify_preflight.ps1`，检查重复项目、Postgres 挂载、`dify`、`dify_plugin`、管理员记录和 API storage 可写性。
5. 在恢复管理员后重启整套 `dify`，验证 `/plugins` 不再跳转 `/install`。

### 持久化加固

1. 先对当前 Postgres 执行 `pg_dumpall`，并复制 `volumes/db/data` 目录快照；任何迁移前必须完成备份和可读性检查。
2. 在 `.env` 中固定 `COMPOSE_PROJECT_NAME=dify`，避免默认目录名生成 `docker` 项目。
3. 将 Postgres 数据路径改为明确的绝对 WSL 路径，或迁移到命名为 `dify_postgres_data` 的 named volume。二者选择其一，不混用。
4. 将应用 storage 的所有权/可写性纳入启动前检查，避免数据库恢复后管理员初始化仍失败。
5. 保存 `docker compose config`、容器列表、数据库清单和挂载清单作为每次启动证据。

### 删除风险

本次未执行 `docker compose down -v`、`docker volume rm`、容器删除或数据目录删除。后续如需清理 `docker-*` 容器，应先导出其 inspect 信息、确认没有独占挂载，并完成 PostgreSQL 与应用 storage 备份。仅停止重复项目是可逆操作，不等同于删除数据。

## 验收门禁

环境固定只有在以下条件全部满足后才能标记 PASS：

1. 冷启动和计算机重启后，只有 `dify-*` Dify 主服务运行。
2. `dify_preflight.ps1` 全部通过。
3. `dify.accounts >= 1`，`dify_plugin` 存在。
4. `plugin_daemon` restart count 在观察窗口内不增长。
5. `/plugins` 可打开且不跳转 `/install`。
6. `db_query_extended` 可见或使用已校验的新包重新安装成功。

当时在这些条件完成前，DM8 Provider、Tool 和 Workflow API 验收继续暂停；该暂停已在 2026-06-30 新稳定基线通过后解除，最终状态见文末恢复验收结论。

## 2026-06-30 新稳定基线验收（已通过）

本次明确接受旧 Dify Console 数据丢失：旧管理员、租户及其他 Console 业务数据未恢复。本次建立的是 **2026-06-30 新稳定基线**，不是旧数据恢复，也不是一次性临时修复。

- 唯一启动入口：`db_query_extended/verification/start_dify.ps1`。
- 唯一主 Compose 项目：`dify`；重复的 `docker-*` 项目保持停止，未加入当前服务链路，未删除其容器或卷。
- PostgreSQL 固定路径：`\\wsl.localhost\Ubuntu\home\zli2759\projects\dify-dm\docker\volumes\db\data`。
- 存储权限基线：固定入口加载 `dify.baseline.override.yaml`；每次启动均幂等执行 `chown -R 1001:1001 /app/api/storage`，不再因旧 `.init_permissions` 标记跳过修复。
- 新管理员：`admin@localhost.local`（用户名 `admin`）创建成功，页面由 `/install` 跳转到 `/apps`。
- `dify_preflight.ps1` 验收：`dify.accounts=1`、`dify.tenants=1`、`dify_plugin` 存在、API storage 可写。
- `plugin_daemon`：运行状态稳定；5 秒观察窗口前后 restart count 均为 `17`，未处于 restart loop。
- `/install` 复验：再次打开后直接重定向 `/apps`，不再要求创建管理员。

结论：Dify Console 的 2026-06-30 新稳定基线验收通过。自此仅恢复 DM8 Workflow API 验收；在验收结果明确前不提前继续功能开发。

## DM8 Workflow API 恢复验收

在 Console 新稳定基线上重新安装 `db_query_extended 0.1.1`、配置 DM8 只读凭据、重建并发布 `Start -> Tool -> End` Workflow 后，执行 `verify_workflow.ps1`：

- 结果：`12 PASS / 0 FAIL / 0 SKIP`。
- 覆盖：基础查询、LIMIT、COUNT、WHERE、JOIN、`max_rows` 截断、Unicode UTF-8，以及 DROP/UPDATE/DELETE/ALTER/CREATE 只读拦截。
- 证据：`reports/verification/2026-06-30/workflow_dm8_result.json`。
- API Key 未写入仓库或报告。

结论：DM8 Workflow API 真实链路恢复验收通过。

## 当日晚间重启复核

再次启动时发现固定 Console 主库中的 `accounts`、`tenants` 和 `dify_plugin` 再次缺失，说明 Console 数据持久化问题仍需继续追踪。恢复过程中确认 WSL bind storage 在主机显示 `1001:1001`，但在 Docker Desktop 容器内映射为 `root:root`，会再次导致管理员事务回滚。

本次未删除任何容器、Volume 或数据目录。安全修复为将 app storage 切换到固定命名卷 `dify_app_storage`，由 `init_permissions` 设置 `1001:1001`；增强后的 `dify_preflight.ps1` 会检查命名卷、实际可写性、Console ping 和 setup 状态。

管理员和 `dify_plugin` 已重新建立，核心预检通过；但旧插件安装、Provider 凭据、DM8 Workflow 和 API Key 未恢复。完整启动状态见 `reports/verification/2026-06-30/environment_startup_report_2026-06-30.md`。

### 最小持久化实验结论

随后执行严格 stop/start 实验，发现同一 `dify-db_postgres-1` 容器 ID 和相同 UNC mount source 字符串在重启前后连接到不同 PostgreSQL system identifier：`7657358257309876271 -> 7648851954774859813`，重启后 `accounts` 表不存在。

同时确认固定入口的有效 Compose 配置不包含 `db_postgres` 与 `weaviate`；两者来自重启后已消失的 `/tmp/dify-day5-runtime/docker-compose.middleware.yaml`，属于 orphan 容器。根因因此升级为已证实：临时 Compose 依赖与 WSL UNC bind 后端漂移共同导致关机/重启后 Console 数据未持久保存。实验细节见 `reports/verification/2026-06-30/postgres_persistence_experiment_2026-06-30.md`。
