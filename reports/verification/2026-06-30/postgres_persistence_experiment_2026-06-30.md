# PostgreSQL 最小持久化实验（2026-06-30）

结论：**FAIL — 当前 Dify Console PostgreSQL 不能经受正常 stop/start。**

## 实验约束

- 未执行 `down`、`down -v`、容器删除、Volume 删除或数据目录删除。
- 停止应用使用与固定入口相同的 Compose 文件执行 `stop`。
- 启动只调用 `db_query_extended/verification/start_dify.ps1`。
- 未安装插件、未配置 Provider、未重建 Workflow。

## 停止前

```text
container_id=3dfc16b5f4e4de94a2e6f7b4dde8ee201a8f5b1e3763e3219b1f005d786de8db
mount_source=\\wsl.localhost\Ubuntu\home\zli2759\projects\dify-dm\docker\volumes\db\data
system_identifier=7657358257309876271
accounts=1
tenants=1
plugins=0
plugin_installations=0
```

## 停止/启动发现

固定入口的有效 Compose 配置只包含 10 个应用服务，不包含 `db_postgres` 和 `weaviate`。这两个容器来自已消失的临时文件：

```text
/tmp/dify-day5-runtime/docker-compose.middleware.yaml
```

WSL/Docker Desktop 重启后 `/tmp` 文件消失，数据库和向量库成为 orphan。`compose stop` 不会停止它们，`start_dify.ps1` 也不能启动它们。

为完成有效实验，仅停止并重新启动原 `dify-db_postgres-1` 容器；容器未删除或重建。

## 启动后

```text
container_id=3dfc16b5f4e4de94a2e6f7b4dde8ee201a8f5b1e3763e3219b1f005d786de8db
mount_source=\\wsl.localhost\Ubuntu\home\zli2759\projects\dify-dm\docker\volumes\db\data
system_identifier=7648851954774859813
accounts_table=missing
```

容器 ID 和 mount source 字符串均未变化，但 PostgreSQL system identifier 发生变化，证明容器重新连接到另一套数据目录，不是应用删除账户行。

进一步对比：

- 停止前 UNC mount 在容器内位于设备 `32`，PGDATA 时间为 2026-07-01 01:00。
- WSL Linux 路径直接挂载位于设备 `2128`，集群创建于 2026-06-08。
- 重启后容器连接到 system identifier `7648851954774859813`，与 WSL Linux 路径集群一致。

## 根因

1. PostgreSQL 没有被稳定 Compose 文件管理，依赖重启后消失的 `/tmp` middleware Compose。
2. 既有数据库容器使用 WSL UNC bind source；Docker Desktop 重启/容器重启时，该字符串可能解析到不同后端文件系统。
3. `dify_preflight.ps1` 过去只比较 mount source 字符串，没有验证 PostgreSQL system identifier，因此未能发现底层数据目录漂移。

## 当前门禁

在 PostgreSQL 迁移到受 `start_dify.ps1` 管理的固定 named volume（或经验证稳定的单一 Linux bind mount），并完成至少一次 stop/start 与 Docker Desktop/WSL 重启验证前：

- 不得重新安装插件；
- 不得重建 DM8 Provider、Workflow 或 API Key；
- 不得标记 `Environment Ready`。

