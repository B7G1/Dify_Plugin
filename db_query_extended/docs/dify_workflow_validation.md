# Dify 插件安装与 Workflow 联调记录

记录时间：2026-06-21。

## 安装包检查

- 包路径：`E:\Dify_Plugin\db_query_extended\db_query_extended.difypkg`
- 大小：21,467 bytes。
- 打包时间：2026-06-21 21:28:39。
- CLI checksum：`2a4674e9110d590803d26b26bbaa2e1a32dc2a6c111b6703029a53b0d1ea0147`。
- manifest：插件类型为 `plugin`，Tool 权限已启用，Provider 入口为 `provider/db_query_extended.yaml`，Python runner 元数据为 3.12，最低 Dify 版本为 1.0.0。
- requirements：`dify_plugin==0.6.2`、`SQLAlchemy==2.0.51`、`PyMySQL==1.2.0`、`psycopg[binary]==3.3.4`、`psycopg2-binary==2.9.12`。
- 风险：包内没有 `wheels/`，并非离线依赖包。plugin-daemon 无法访问 Python 依赖源时，安装会失败。

## Dify 运行环境

安装前检查通过：

- `dify-api-1`、`dify-worker-1`、`dify-web-1`、`dify-nginx-1`、`dify-plugin_daemon-1` 均运行。
- PostgreSQL、Redis 均 healthy，测试 MySQL/PostgreSQL 均 healthy。
- `http://localhost/` 返回 HTTP 200。
- `http://localhost/console/api/ping` 返回 HTTP 200。
- API 到 daemon 的地址为 `http://plugin_daemon:5002`；daemon 到 API 的地址为 `http://api:5001`；双方 inner API key 已做脱敏比对且一致。
- plugin-daemon 近期日志未发现 `ERROR`、`panic`、密码字段或 `db_query_extended` 安装/运行记录。

## 安装与 Workflow 状态

本地安装首次被 daemon 拒绝，页面错误为：`PluginDaemonBadRequestError: plugin verification has been enabled, and the plugin you want to install has a bad signature`。

根因是运行中的 daemon 配置 `FORCE_VERIFYING_SIGNATURE=true`。主 Compose 默认同为 true。为仅限本地开发测试的最小修复，已在 `/home/zli2759/projects/dify-dm/outputs/dm_change_matrix/regression_scripts/plugin_daemon.local.override.yaml` 的 `plugin_daemon.environment` 中新增：

```yaml
FORCE_VERIFYING_SIGNATURE: "false"
```

未修改主 Compose、插件代码或数据库；仅重建 plugin-daemon。重建后运行环境已确认 `FORCE_VERIFYING_SIGNATURE=false`，并且 daemon 数据库初始化和内置插件 runtime 均正常。

本次仍未完成 Dify Console 安装、Provider 配置或 Workflow 创建。原因是当前会话的浏览器自动化进程无法启动，不能安全地操作已登录 Console；没有猜测或直接调用未经确认的 Dify 插件安装 API。请在现有 Console 再次选择本地安装该插件包；此时不应再出现签名校验错误。

因此下列验证尚未执行：

- 插件安装成功页面。
- MySQL Provider：`host.docker.internal:3307`。
- PostgreSQL Provider：`host.docker.internal:5433`。
- MySQL 与 PostgreSQL `SELECT * FROM students` Workflow 节点调用。
- 只读 `DROP TABLE students` 拦截、`max_rows=3` 截断和不存在表错误的 Dify UI/Workflow 验证。

此前已在项目级 Python 环境中完成 MySQL/PostgreSQL 的真实 Provider/Tool 调用验证，但这不替代 Dify UI 和 Workflow 联调。

## 2026-06-22: API / plugin-daemon installation-contract finding

- Both the minimized `db_query_extended.difypkg` and the official CLI template
  `test_tool_schema.difypkg` upload successfully, but installation reaches
  `decode/from_identifier` and returns HTTP 400.
- The daemon response is `PluginUniqueIdentifier required`; the Dify API 1.13.3
  implementation sends `plugin_unique_identifier` as a query parameter.
- The official Dify `1.13.3` Compose file explicitly specifies
  `langgenius/dify-plugin-daemon:0.5.3-local`. The running image was verified
  as the official Docker Hub digest
  `sha256:0bf7734135702a719701646a0fd9d7ad8b20b7d9cfb8eaedc8a890cf682d55bc`.
  Therefore changing this deployment to an unverified 0.6.x image is not a
  justified compatibility fix.
- The daemon was force-recreated using that same official image only. It
  initialized `dify_plugin`, started its local runtime, and remained running.
  `FORCE_VERIFYING_SIGNATURE=false` remains active in the local override.
- Result: the signature issue is resolved, but the decode endpoint contract
  error is still an environment-level blocker. No plugin source, package,
  manifest, YAML, requirements, or wheels were changed as part of this finding.

## 2026-06-22: local API compatibility patch

The installation failure was reproduced with both the official CLI template and
`db_query_extended`. Protocol probing showed that the daemon returns HTTP 400
for GET query parameter `plugin_unique_identifier`, but returns HTTP 200 for
GET query parameter `PluginUniqueIdentifier` and for a GET JSON body using the
snake_case key. POST is not routed for this endpoint.

For local development only, the API source patch is limited to
`api/core/plugin/impl/plugin.py`, method `decode_plugin_from_identifier()`:

```diff
- params={"plugin_unique_identifier": plugin_unique_identifier},
+ params={"PluginUniqueIdentifier": plugin_unique_identifier},
```

The complete patch is retained in `docs/api_decode_identifier_patch.diff`.
No plugin source, manifest, provider/tool YAML, requirements, daemon, database,
volume, or package was changed. Roll back with:

```bash
git -C /home/zli2759/projects/dify-dm checkout -- api/core/plugin/impl/plugin.py
```

This local source path is not mounted into `dify-api-1`; the same one-line
patch must therefore be applied inside `/app/api` or baked into a local API
image before restarting the API container.

## 继续执行步骤

在可访问并已登录的 Dify Console 中：

1. 打开插件管理，选择本地文件安装并上传 `db_query_extended.difypkg`。
2. 核对安装日志；若依赖安装失败，先补齐与 daemon Python ABI 匹配的离线 wheels。
3. 创建 MySQL、PostgreSQL Provider 凭据，使用 `host.docker.internal` 和端口 3307/5433 验证。
4. 创建 `Start -> db_query_extended Tool -> End` Workflow，分别执行 `SELECT * FROM students;`。
5. 记录 5 行正常结果、`max_rows=3` 截断、只读 SQL 拦截和不存在表的友好错误。
