# Day 3：db_query_extended 基础结构与入口报告

## 修改目标

完善插件元数据、Provider 连接表单、Tool 输入输出契约与 SDK 入口日志；不将数据库凭据、连接或 SQL 执行写入 `main.py`。

## 修改文件

- `db_query_extended/manifest.yaml`
- `db_query_extended/provider/db_query_extended.yaml`
- `db_query_extended/tools/db_query_extended.yaml`
- `db_query_extended/main.py`
- `db_query_extended/utils/validation.py`
- `db_query_extended/utils/database.py`
- `db_query_extended/tools/db_query_extended.py`
- 工作区及插件 README、`INDEX.md`

后面三个 Python 文件只做 YAML 参数契约同步：`connection_timeout` 与 `timeout_seconds` 的新名称已接入，并保留旧名称的读取兼容，防止配置表单与运行时实现脱节。

## manifest.yaml

名称为 `db_query_extended`，作者为 `li_zijun`，最小 Dify 版本为 `1.0.0`。英文描述已更新为“面向本地数据库测试和后续扩展的 MySQL 与 PostgreSQL 只读 SQL 查询工具”。

官方模板的顶层 `type` 保持为 `plugin`，不能改为 `tool`；工具能力由 `resource.permission.tool.enabled` 和 `plugins.tools` 声明。这是 CLI 模板的结构约定。

## Provider 表单

`provider/db_query_extended.yaml` 定义：

| 字段 | 类型 / 默认值 | 用途 |
| --- | --- | --- |
| `database_type` | select，`mysql` | MySQL 或 PostgreSQL |
| `host` | text-input，`localhost` | 数据库地址 |
| `port` | number | MySQL 通常为 3306，PostgreSQL 通常为 5432 |
| `database` | text-input，`plugin_test` | 数据库名 |
| `username` | text-input | 用户名 |
| `password` | secret-input | 密码，不以明文日志输出 |
| `connection_timeout` | number，10 | 连接超时秒数 |
| `ssl_mode` | select，`disable` | `disable`、`prefer`、`require`；本地默认禁用 |

PostgreSQL 已将 SSL 模式传给驱动；MySQL 的安全连接参数将在后续随证书配置一并实现，当前不伪造 SSL 已启用状态。

## Tool 表单与输出契约

`tools/db_query_extended.yaml` 定义 `sql`、`max_rows`（默认 100，范围 1–1000）、`timeout_seconds`（默认 30，范围 1–120）、`readonly` 与 `output_format`。只允许单条 `SELECT`、`WITH`、`SHOW`、`DESC`、`DESCRIBE`、`EXPLAIN`；拒绝 DDL、DML、权限语句和多语句。

当前唯一可执行输出格式是 JSON，结构为 `columns`、`row_count`、`rows`、`truncated`、`max_rows` 与数据库类型上下文。表单展示 `markdown` 为后续展示层扩展；运行时会明确拒绝该值，避免静默返回错误格式。

## main.py 入口逻辑

入口保留 `Plugin(DifyPluginEnv(...))` 的 SDK 初始化方式。工具注册由 `manifest.yaml` 的 `plugins.tools` 完成；`main.py` 只初始化日志、启动 SDK 运行时、记录启动异常并重新抛出异常，不包含凭据、数据库连接或 SQL。

## 验收命令与结果

| 命令 | 结果 | PASS |
| --- | --- | --- |
| `python -m compileall -q main.py provider tools utils` | 成功 | 是 |
| 参数契约与只读 SQL 拒绝测试 | 成功 | 是 |
| 数据访问层对 Day 2 MySQL / PostgreSQL 的 `SELECT` | 两库均成功返回 5 行，并正确标识截断 | 是 |
| `dify-plugin.exe plugin validate` | 当前 CLI v0.6.1 没有 `validate` 子命令 | 不适用 |
| `dify-plugin.exe plugin checksum .` | 成功；`0264a622a838be909e1999ae2ec893bd378c22f2641e1937d3976430517cb1cc` | 是 |
| `dify-plugin.exe plugin package . --output_path ..\\archive\\db_query_extended-day3.difypkg` | 成功 | 是 |

首次将 `--output_path` 传为目录 `..\\archive` 时打包失败；CLI 要求文件路径。改为明确的 `.difypkg` 文件路径后成功，无代码修复需要。

## 当前未实现内容与下一步

- Markdown 响应渲染尚未实现；当前显式拒绝该输出格式。
- MySQL 证书/CA 的 SSL 连接参数尚未实现。
- 尚未执行 Dify Workflow UI 联调。
- 后续应在真实 Dify plugin-daemon 中导入本次归档包，并覆盖 Provider 连接失败、超时、SQL 语法错误及结果截断场景。

## 目录检查

本次报告存放于 `reports/`，归档包存放于 `archive/`；数据库产物仍在 `local_test_db/`。未移动既有根目录的历史源码、插件包及报告目录，因为它们存在未提交变更且引用关系尚未确认。
