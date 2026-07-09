# db_query_extended：DM 凭据校验诊断（2026-06-23）

## 范围与约束

- 仅做只读检查：未修改插件源码、`provider.yaml`、`provider.py`、依赖、wheels、Dify 业务数据或现有插件安装。
- 平台采用今天最小重建的空业务库；旧业务库在恢复时已重新初始化，未找到可回滚 volume。
- 本报告不记录数据库密码；凭据表仅检查是否存在加密字段。

## 结论

当前已安装的 `li_zijun/db_query_extended:0.0.1` **只支持 MySQL 和 PostgreSQL**，不支持 DM / Dameng / 达梦。

因此，若“前往修复”表单所指向的目标是当前 Dify 自身的 DM 业务库（端口 `5236`），失败分类是：

> **2. 插件声明只支持 MySQL/PostgreSQL，但用户试图填 DM 目标参数。**

daemon 到该 DM 地址的 TCP/5236 已验证可达，故不是网络不可达（选项 5）。代码和已安装声明均没有 DM 分支、`dmPython` 或 DM 动态库，故不是“代码已支持而声明未同步”（选项 3），也不是“声明支持但运行时缺库”（选项 4）。

若改填一个真正的 MySQL 或 PostgreSQL 目标，仍需使用该目标的正确账号、密码和库名；当前日志中的通用“无法连接数据库”不能单独排除错误的 MySQL/PostgreSQL 连接参数（选项 1），但它不能把 DM 变成受支持的数据库类型。

## A. 当前 Provider 表单支持的数据库类型

检查命令：

```powershell
Get-Content -Raw E:\Dify_Plugin\db_query_extended\provider\db_query_extended.yaml
Get-Content -Raw E:\Dify_Plugin\db_query_extended\utils\validation.py
```

结果：

```yaml
credentials_for_provider:
  database_type:
    type: select
    default: mysql
    options:
      - value: mysql
      - value: postgresql
```

```python
SUPPORTED_DATABASE_TYPES = {"mysql", "postgresql"}
DEFAULT_PORTS = {"mysql": 3306, "postgresql": 5432}
```

`rg -n -i "dameng|达梦|dmPython|dm8"` 在插件 Python/YAML/requirements 中没有匹配。`requirements.txt` 仅包含 `PyMySQL` 与 `psycopg2-binary` 等依赖；没有 `dmPython`。

## B. validate_credentials 实现与连接 URI

检查命令：

```powershell
Get-Content -Raw E:\Dify_Plugin\db_query_extended\provider\db_query_extended.py
Get-Content -Raw E:\Dify_Plugin\db_query_extended\utils\database.py
```

调用链：

```text
DbQueryExtendedProvider._validate_credentials
  -> validate_connection_config(credentials)
  -> verify_database_connection(config)
  -> create_database_engine(config)
  -> SELECT 1
```

实际 SQLAlchemy 方言只有：

```python
mysql       -> mysql+pymysql
postgresql  -> postgresql+psycopg2
```

没有 `dm` / `dameng` 分支。`verify_database_connection` 会在 `SELECT 1` 失败时返回统一消息：

```text
Unable to connect to the database. Check database type, host, port,
database name, and credentials.
```

这解释了为何把 DM 地址伪装成 PostgreSQL/MySQL 参数时，前端只会得到通用连接失败，而不是更明确的“DM 不受支持”。

## C. 已安装声明与 Dify 记录

检查命令：

```bash
docker exec dify-db_postgres-1 psql -U postgres -d dify_plugin -t -A -c \
  "SELECT declaration FROM plugin_declarations WHERE plugin_id='li_zijun/db_query_extended' ORDER BY updated_at DESC LIMIT 1;"
docker exec dify-db_postgres-1 psql -U postgres -d dify_plugin -c \
  "SELECT tenant_id,provider,plugin_id,plugin_unique_identifier FROM tool_installations WHERE plugin_id='li_zijun/db_query_extended';"
docker exec dify-db_postgres-1 psql -U postgres -d dify -c \
  "SELECT tenant_id,provider,name,is_default,credential_type,encrypted_credentials IS NOT NULL AS has_credentials FROM tool_builtin_providers WHERE provider='li_zijun/db_query_extended/db_query_extended';"
```

结果：

- 插件安装：存在，`install_type=local`、`runtime_type=local`。
- Tool installation：存在，provider 为 `db_query_extended`。
- Provider declaration：存在，长度 5,432 字节。
- 声明内 `credentials_schema.database_type.options` 只有 `mysql`、`postgresql`。
- Tool declaration：存在，工具为 `db_query_extended`（只读 SQL 查询）。
- 业务库中有一条加密 Provider 凭据记录，但 `is_default=false`；因此尚未形成可供 Workflow 使用的默认 Provider。

表单/dispatch payload 的字段由已安装声明确定：

```text
database_type, host, port, username, password, database,
schema (optional), charset (optional), connect_timeout
```

密码为 `secret-input`，业务库只存加密值；本次诊断未读取或输出密码。现有 API/daemon HTTP 日志不记录明文 credential payload。

## D. “前往修复”校验证据

已有复现日志（当前重建租户）显示：

```text
POST /plugin/<tenant>/dispatch/tool/validate_credentials  HTTP 200
```

API 接收到 daemon 的业务错误：

```text
ToolProviderCredentialValidationError:
Unable to connect to the database. Check database type, host, port,
database name, and credentials.
```

这说明：前端路由、API 转发、daemon dispatch、Provider 声明、Tool 注册均正常；失败发生在 Provider 的实际连接验证。

网络最小探针：

```bash
docker exec dify-plugin_daemon-1 sh -lc \
  "timeout 5 bash -c '</dev/tcp/172.26.224.1/5236' && echo TCP_5236_REACHABLE || echo TCP_5236_UNREACHABLE"
```

结果：

```text
TCP_5236_REACHABLE
```

即 daemon 到 DM 主机端口可达；问题不在网络层。

## “前往修复”表单现在应该填什么

仅有两条安全路径：

1. **验证当前不改代码的插件链路：** 选择 `mysql` 或 `postgresql`，填写一个真实、daemon 可访问的 MySQL/PostgreSQL 目标及其正确账号、密码、端口和数据库名。校验成功后，确认凭据记录的 `is_default` 变为 true。
2. **验证当前 Dify 的 DM 业务库：** 当前插件无法完成。不要在下拉框中把 DM 端口/用户名伪装成 PostgreSQL 或 MySQL；这只会触发本次已观察到的通用连接失败。

## 下一步最小修复动作

若目标是继续验证插件安装与“前往修复”链路：准备一个可访问的 MySQL 或 PostgreSQL 测试库，按对应类型填表并验证成功。此路径 **不需要重装插件，也不需要改任何文件**。

若目标必须是 DM：最小代码变更应独立规划，至少包括：

1. `provider/db_query_extended.yaml` 增加 `dm` 选项；
2. `utils/validation.py` 增加 `dm` 与默认端口 5236；
3. `utils/database.py` 增加 DM 驱动、SQLAlchemy 方言/连接实现、DM 适用的校验与超时处理；
4. `requirements.txt` 和离线 `wheels/` 增加兼容 Python 3.12/Linux 的 DM 驱动及其依赖；
5. 重新打包、重新安装插件，使新的 Provider declaration 进入 daemon。

在上述 DM 支持改动完成之前，**重装当前相同的 `.difypkg` 不会解决问题**；就决定性字段 `database_type` 而言，本地源码与已安装声明都只列出 MySQL/PostgreSQL。已安装声明另含 `schema`、`charset` 两个可选字段，因此若后续要对源码与当前包做严格字节级同步，应另行核对打包来源；这一差异不增加 DM 支持，也不是本次连接失败的根因。
