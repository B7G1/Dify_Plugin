# Phase 10 — KingbaseES Test Environment Status

Date: 2026-07-02  
Status: **BLOCKED**

## 已完成

- 检查了本机 Docker 镜像和容器：没有 KingbaseES。
- 检查了工作区和常见安装位置：没有 KingbaseES 镜像 tar、安装包、客户端库或 license。
- 在 `local_test_db/kingbase/` 建立了完全独立的环境配置，没有修改 MySQL、PostgreSQL 或 DM8 配置。
- Compose 强制由 `KINGBASE_IMAGE` 注入真实厂商镜像；没有硬编码或拉取未经确认的镜像。
- 准备了 PostgreSQL 兼容模式、UTF-8、端口 54321 和独立 named volume 配置。
- 准备了 `plugin_test` 数据库、`plugin_test` schema、`plugin_readonly` 只读账号和 `plugin_test_users` 数据。
- 准备了 SELECT 1、LIMIT 5、COUNT、Unicode、时间、版本、字符集、search_path 和权限验证。
- 准备了环境预检与验证 PowerShell 脚本。

## 阻塞项

- 缺少合法取得的 KingbaseES Linux amd64 Docker 镜像或安装包。
- 缺少与目标版本匹配的开发测试 license/授权结论。
- 未确认实际镜像的启动环境变量、license 挂载位置和 `ksql` 路径。
- 无法启动服务，因此尚未记录真实数据库版本和 PostgreSQL 兼容能力。
- 无法执行初始化 SQL或三条必需查询。
- `ksycopg2`、原生客户端库和 SQLAlchemy 2.0.51 可行性仍处于 Phase 10.1 的 CONDITIONAL GO。

## 运行判定

当前不能输出“KingbaseES 可运行”。计划连接参数为：

```text
host=localhost
port=54321
database=plugin_test
schema=plugin_test
username=plugin_readonly
password=plugin_readonly_123  (local test only)
driver=ksycopg2 2.9.1 candidate; runtime import pending
```

只有在厂商镜像和许可到位、容器启动、初始化完成、`verification/verify.ps1` 真实通过后，才能把状态更新为 PASS。

## 官方依据

KingbaseES 官方 Docker 文档描述的是取得厂商镜像 tar 后通过 `docker load` 导入，而不是一个可无条件假定的公共镜像名称；部署手册同时包含 license 持久化/更换流程。官方 License 文档明确 Docker 部署也受授权控制。

- [KingbaseES Docker 部署手册](https://help.kingbase.com.cn/v9/install-updata/install-docker/index.html)
- [镜像导入和运行示例](https://help.kingbase.com.cn/v8/install-updata/install-docker/install-docker-1.html)
- [Docker 部署的 License 控制](https://bbs.kingbase.com.cn/kingbase-html/v8/install-updata/license-information/license-information-4.html)
