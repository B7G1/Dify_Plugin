# 本地测试数据库

本目录提供 Dify SQL Query Plugin 的统一数据库测试环境。MySQL 8.4 与 PostgreSQL 16 已自动化；DM8 环境准备见 [`dm8/README.md`](dm8/README.md)。三库使用一致的业务数据。

## 快速恢复（首次约 3 分钟）

要求：Docker Desktop 已启动，且本机的 `3306` 与 `5432` 端口未被占用。

```powershell
Set-Location E:\Dify_Plugin\local_test_db
docker compose up -d
docker compose ps
```

等待两个服务状态为 `healthy` 后执行验收：

```powershell
.\verification\verify.ps1
```

重建为全新的确定性数据集（会删除本地测试数据卷）：

```powershell
docker compose down -v
docker compose up -d
```

停止环境但保留数据：`docker compose down`。

## 连接信息

| 数据库 | Host | Port | Database | User | Password |
| --- | --- | ---: | --- | --- | --- |
| MySQL | `localhost` | 3306 | `plugin_test` | `plugin_test_user` | `plugin_test_password` |
| PostgreSQL | `localhost` | 5432 | `plugin_test` | `plugin_test_user` | `plugin_test_password` |

这些凭据仅允许用于本机容器测试，不能用于生产或共享环境。

详细结构、数据说明和验收记录见 [database_setup_report.md](database_setup_report.md)。
