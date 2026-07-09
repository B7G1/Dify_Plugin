# KingbaseES 本地测试环境

状态：**BLOCKED — 配置已准备，尚无可运行的厂商镜像/安装包/license。**

本目录完全独立于现有 MySQL、PostgreSQL 和 DM8 测试环境。不要把 KingbaseES 服务加入 `local_test_db/docker-compose.yml`，也不要修改既有容器或数据卷。

## 已准备

- 独立 Compose 文件；
- PostgreSQL 兼容模式、UTF-8、默认端口 `54321` 的环境变量设计；
- `plugin_test` 数据库和 `plugin_test` schema 初始化 SQL；
- 只读账号 `plugin_readonly`；
- `plugin_test_users` 表和确定性测试数据；
- `SELECT 1`、LIMIT、COUNT、版本、字符集和 search path 验证脚本；
- 不依赖插件业务代码的环境预检脚本。

## 当前阻塞

本机 Docker 中没有 KingbaseES 镜像或容器，工作区中没有 KingbaseES 安装包、镜像 tar 或 license。官方 Docker 文档要求先取得厂商镜像 tar 并使用 `docker load` 导入；Docker 部署仍受 KingbaseES license 控制。

因此 `docker-compose.yml` 不包含任何猜测的公共镜像名。必须显式设置 `KINGBASE_IMAGE`，否则 Compose 会直接报错退出。

## 需要人工提供

1. 合法取得的 KingbaseES V9/V8 Linux amd64 Docker 镜像 tar；
2. 镜像的精确版本、SHA-256 和 PostgreSQL 兼容模式支持说明；
3. 适用于该镜像的 license 或厂商明确的开发测试授权；
4. 镜像要求的启动参数、license 挂载位置和 `ksql` 实际路径；
5. 本机测试专用管理员密码，通过当前 PowerShell 进程环境变量提供。

## 准备方式

导入厂商镜像后记录真实名称：

```powershell
docker load -i '<vendor-kingbase-image.tar>'
docker images --digests

$env:KINGBASE_IMAGE = '<repository>:<tag>'
$env:KINGBASE_ADMIN_PASSWORD = '<local-test-admin-password>'
Set-Location E:\Dify_Plugin\local_test_db\kingbase
docker compose config
```

确认厂商镜像的环境变量与本 Compose 一致后才允许启动：

```powershell
docker compose up -d
docker compose ps
```

不要执行 `down -v`，除非明确批准删除 KingbaseES 本地测试数据。

## 初始化

厂商镜像没有统一的 `/docker-entrypoint-initdb.d` 契约，因此 SQL 只读挂载到容器 `/opt/phase10-init`，不会假装自动执行。

确认 `ksql` 路径后，以管理员身份依次执行：

1. `init/01_create_database_and_role.sql`，连接默认管理数据库；
2. `init/02_schema_and_data.sql`，连接 `plugin_test` 数据库；
3. `verification/verify.sql`，使用 `plugin_readonly` 连接。

所有管理员密码和 license 路径只能通过本地环境或厂商安全流程注入，不得写入仓库。

## 计划连接参数

| 参数 | 值 |
| --- | --- |
| host | `localhost` |
| port | `54321` |
| database | `plugin_test` |
| schema | `plugin_test` |
| username | `plugin_readonly` |
| password | `plugin_readonly_123`（仅限本机测试） |
| driver | `ksycopg2 2.9.1` 候选；真实 import 尚未完成 |
| SQLAlchemy URL | `kingbase+ksycopg2://...`（官方形式，2.0.51 兼容性待实测） |

在 `verification/verify.ps1` 输出全部 PASS 前，上述参数只能标记为 **PLANNED**，不能宣称环境可用。

## 参考

- [KingbaseES 官方 Docker 部署手册](https://help.kingbase.com.cn/v9/install-updata/install-docker/index.html)
- [官方镜像导入与运行说明](https://help.kingbase.com.cn/v8/install-updata/install-docker/install-docker-1.html)
- [KingbaseES License 管理说明](https://bbs.kingbase.com.cn/kingbase-html/v8/install-updata/license-information/license-information-4.html)
