# Dify Runtime 恢复记录

记录时间：2026-06-21。

## Compose 位置与配置

正在运行的 `dify-plugin_daemon-1` 容器的 Compose 标签指向：

- 工作目录：`/home/zli2759/projects/dify-dm/docker`
- 主文件：`/home/zli2759/projects/dify-dm/docker/docker-compose.yaml`
- 本地覆盖：`/home/zli2759/projects/dify-dm/outputs/dm_change_matrix/regression_scripts/plugin_daemon.local.override.yaml`

启动前检查发现 `docker/.env.example`，未发现 `docker/.env` 或 `docker-compose.override.yaml`。主 Compose 定义了 `api`、`worker`、`web`、`plugin_daemon`、`db_postgres`、`redis`、`weaviate` 等服务；当前活动覆盖文件为 plugin-daemon 指定 PostgreSQL 配置。

## plugin-daemon 原始问题与修复

daemon 配置为 `DB_HOST=db_postgres`、`DB_PORT=5432`、`DB_USERNAME=postgres`、`DB_DATABASE=dify_plugin`。PostgreSQL 原先仅有主业务库 `dify`，没有 `dify_plugin`，导致 daemon 因数据库不存在而 restart loop。

已执行最小修复：

```sql
CREATE DATABASE dify_plugin;
```

重启 daemon 后，日志确认：

- `dify plugin db initialized`
- `persistence initialized`
- 内置插件 `local runtime ready`

`dify_plugin` 已初始化 `plugins`、`plugin_installations`、`tool_installations`、`install_tasks` 等插件表。daemon 当前 `running`、`restart_count=0`，但镜像未定义 Docker healthcheck。

## 当前服务状态

| 服务 | 状态 |
|---|---|
| plugin-daemon | 运行稳定，5002/5003 已暴露 |
| PostgreSQL | healthy |
| Redis | healthy |
| Weaviate | running |
| api | 未创建 / 未运行 |
| worker | 未创建 / 未运行 |
| web | 未创建 / 未运行 |

## WSL 与 Docker Desktop 恢复状态

后续复查确认 Windows WSL 已恢复：默认发行版为 Ubuntu、版本为 WSL2，Ubuntu 与 `docker-desktop` 均处于 Running 状态。Docker Desktop 的 `desktop-linux` context 为当前 context，Docker Engine 可访问，原有 Dify 容器与测试容器仍完整存在。

因此没有执行 `wsl --shutdown`、重启 Docker Desktop、重装 Ubuntu 或任何删除性操作。

## 恢复尝试与当前阻塞

已从正确 Compose 目录执行完整 `docker compose up -d`，并在 WSL 恢复后再次尝试启动 `api worker web nginx`。命令均在镜像拉取或初始化阶段超过两分钟，随后未出现 api、worker、web 或 nginx 容器。

Compose 文件确认 API/Worker 使用 `langgenius/dify-api:1.13.3`，Web 使用 `langgenius/dify-web:1.13.3`，Nginx 使用 `nginx:latest`。首次拉取耗时较长，但 registry DNS 与 TLS 访问正常：容器内解析 `registry-1.docker.io` 成功，访问 `/v2/` 返回预期的 `401 Unauthorized`。API 镜像随后可用，Web 镜像单独拉取在约一分钟内完成；因此采用路线 A（继续使用官方镜像），未修改 Docker Desktop 镜像源、代理或 DNS。

源码同时具备 `api/Dockerfile` 与 `web/Dockerfile`，本地构建路线可行但本次无需启用。

第一次启动时因未指定既有 Compose 项目名，产生了 `docker-*` 临时服务；该组服务无法解析 `db_postgres` / `plugin_daemon`。为不删除任何容器或 volume，仅停止了这组临时容器。随后使用项目名 `dify` 启动服务，使其加入原有 Dify 网络。

## Dify 服务恢复结果

以下服务已在 `dify` 项目下运行：

- `dify-api-1`：运行，监听容器端口 5001。
- `dify-worker-1`：运行，Celery 日志显示 `ready`。
- `dify-web-1`：运行，Next.js 日志显示 `Ready`。
- `dify-nginx-1`：运行，主机端口 80 / 443 已暴露。
- `dify-plugin_daemon-1`：持续运行，`restart_count=0`。
- `dify-db_postgres-1` 与 `dify-redis-1`：healthy；Weaviate 运行。

Console 根路径 `http://localhost/` 返回 HTTP 200。`/health` 连接被 Nginx 关闭，`/console/api/health` 与 `/api/health` 返回 404；该版本可用的 API 连通性探针为 `http://localhost/console/api/ping`，返回 HTTP 200。

API 与 plugin-daemon 的配置已做脱敏核验：API daemon URL 为 `http://plugin_daemon:5002`，daemon inner API URL 为 `http://api:5001`，双方 inner API key 均存在且匹配。

## 2026-06-22 image compatibility verification

The official `langgenius/dify` tag `1.13.3` Compose file specifies
`langgenius/dify-plugin-daemon:0.5.3-local`; no `PLUGIN_DAEMON_VERSION`
variable is present. The local daemon image was already the official Docker Hub
image (digest `sha256:0bf7734135702a719701646a0fd9d7ad8b20b7d9cfb8eaedc8a890cf682d55bc`).
It was recreated without deleting the `dify_plugin` database or the plugin
storage volume. Startup completed with `dify plugin db initialized` and local
runtime readiness messages. The remaining installation blocker is the
`decode/from_identifier` request-contract failure, not a stale local image.

## 插件安装与 Workflow 联调条件

plugin-daemon、API、Worker、Web、Nginx 均已恢复，Console 与 API ping 正常，已具备通过 Dify Console/API进行插件安装和 Workflow 联调的运行环境条件。

插件包还未附带离线 wheels；若 daemon 无法访问 Python 依赖源，安装前需补齐离线依赖。当前仅完成安装前检查，尚未安装 `db_query_extended.difypkg`。

安装包与 Dify Console/Workflow 联调的详细记录见 `docs/dify_workflow_validation.md`。安装前静态检查、服务状态和 API ping 均通过；当前未完成 Console 操作是因为本会话的浏览器自动化进程无法启动，未使用未经确认的安装 API 作为替代。
