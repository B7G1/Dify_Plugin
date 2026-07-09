# 2026-06-30 开发环境启动报告

状态：**FAIL — PostgreSQL 持久化实验失败**

## 已恢复

- 唯一入口：`db_query_extended/verification/start_dify.ps1`。
- 主 Compose：仅 `dify` 运行；历史 `docker` 项目全部停止。
- 开发测试库：`dify-plugin-local-test-db` 的 MySQL/PostgreSQL 健康。
- PostgreSQL 固定路径：`\\wsl.localhost\Ubuntu\home\zli2759\projects\dify-dm\docker\volumes\db\data`。
- `dify.accounts=1`、`dify.tenants=1`、`dify_plugin` 存在。
- App storage 改用固定命名卷 `dify_app_storage`，容器内为 `1001:1001` 且 API 可写。
- plugin-daemon 在观察窗口内 restart count 不增长。
- Console ping 与 setup 状态通过；登录后 `/install` 自动跳转 `/apps`。

## 开发依赖

- Docker Engine `29.5.2`，Docker Desktop 后端运行。
- WSL2：Linux `6.6.87.2`，Python `3.12.3`。
- Windows 项目虚拟环境：Python `3.11.0`，SQLAlchemy/PyMySQL/psycopg2 可导入。
- Dify Plugin CLI：`v0.6.1`。
- MySQL 测试库：12 条用户数据。
- PostgreSQL 测试库：12 条用户数据。
- DM8：Windows 服务运行；容器到 `host.docker.internal:5236` TCP 和 `SELECT 1` 通过。
- Provider 本地回归：`6 PASS / 0 FAIL / 0 SKIP`。
- Tool 本地回归：`27 PASS / 0 FAIL / 0 SKIP`。

## 当前阻塞

本次启动发现 Console 主库再次为空，原 `db_query_extended` 安装记录、Provider 凭据、DM8 配置、Workflow 和 API Key 均未保留。管理员与 `dify_plugin` 已安全重建，但插件数据库当前为：

```text
plugins=0
plugin_installations=0
```

因此 Console 中的 Provider/Tool/DM8 Workflow 尚不可用，需要重新上传 `db_query_extended-0.1.1-dm8-linux-amd64.difypkg`、配置 DM8 只读凭据并重建 Workflow。任何 API Key 都不得写入本报告、脚本或 Git。

## Git

- 分支：`main`，相对 `origin/main` ahead 3。
- 工作区存在大量已跟踪修改、删除项和未跟踪文件；这些均未自动清理或覆盖。
- 未发现 merge 冲突索引或 `.orig`/`.rej` 冲突残留。

后续最小持久化实验进一步证明：同一 PostgreSQL 容器在 stop/start 后 system identifier 从 `7657358257309876271` 变为 `7648851954774859813`，且 `accounts` 表消失。完整证据见 [`postgres_persistence_experiment_2026-06-30.md`](postgres_persistence_experiment_2026-06-30.md)。

结论：当前 PostgreSQL 挂载不能经受重启，完整 Dify 插件开发链路尚未恢复，不标记 `Environment Ready`。
