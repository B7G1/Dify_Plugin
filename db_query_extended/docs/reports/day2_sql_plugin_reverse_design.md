# Day2：Dify SQL Query Plugin 逆向设计与运行时联调研究报告

日期：2026-06-22  
项目：`db_query_extended`  
范围：Dify 本地插件安装链路、离线依赖、Tool Provider 架构、声明数据与 Workflow 集成。  
边界：本报告是事实记录与技术分析，不包含 DM、KingbaseES 扩展，也不将运行时兼容性问题归咎于插件业务代码。

## 摘要

Day2 的核心成果不是增加一个新的数据库方言，而是把 Dify Tool Plugin 从“可打包的代码目录”推进到“可被平台识别、安装、启动并在 Workflow 中展示的运行时单元”。排查中先后出现了两类容易被误判为插件实现问题的故障：第一类是 API 与 plugin-daemon 在 `decode/from_identifier` 接口上的参数绑定不兼容；第二类是 plugin runtime 在线解析 Python 依赖时超时并被 daemon 终止。两类问题都使用官方 CLI 生成的 `test_tool_schema` 得到了复现，因此可以排除 `db_query_extended` 的 manifest、Provider YAML、Tool YAML 和 SQL 查询逻辑是首要原因。

最终，安装链路已恢复，`db_query_extended` 可以完成打包、上传、安装、runtime 启动并进入 Workflow；界面能够展示“扩展数据库查询 / 只读 SQL 查询”及 `sql`、`max_rows`、`timeout`、`readonly` 参数。这一结果说明工具注册、声明生成、运行时加载和 Workflow 工具枚举链路已打通。剩余的 `ToolProviderNotFoundError` 属于 Provider 默认凭据/授权页面生成和绑定层问题，应在下一阶段独立研究，不能与安装问题混为一谈。

## 一、安装失败的现象与问题边界

### 1.1 现象

首次通过 Dify Console 上传 `db_query_extended.difypkg` 时，包上传成功、插件信息可被读取，但点击安装后页面仅显示 `Internal Server Error`。这类错误的危险之处在于：页面看上去像是插件本身格式错误，实际却可能发生在 Console、API、plugin-daemon、数据库声明、依赖安装和 runtime 启动中的任意一层。

为避免在插件代码中盲目修改 YAML 或 requirements，使用 Dify CLI 原生模板创建并打包 `test_tool_schema.difypkg` 作为对照。官方模板出现完全相同的页面错误，说明问题不依赖于 SQL 查询业务、数据库连接参数、Provider 实现或 Tool 实现。后续证据进一步表明，两种包均完成了上传和 declaration 写入，失败发生在 API 调用 daemon 的 decode 接口时。

### 1.2 安装链路的分层观察

安装操作按以下顺序进入运行时：

```text
Console 上传包
  -> plugin-daemon upload/package
  -> installation/fetch/batch
  -> decode/from_identifier
  -> install/identifiers
  -> 创建 Python 环境并安装 requirements
  -> 启动 plugin runtime
  -> 记录插件与安装状态
```

在早期失败中，前两步均返回 HTTP 200，而 `decode/from_identifier` 返回 HTTP 400。该位置非常关键：daemon 已能够读取插件包和 declaration，但 API 尚不能把可安装包正确解码为安装请求；因此没有理由通过重写 Provider/Tool YAML 来修复它。

## 二、`decode/from_identifier` 参数契约问题

### 2.1 API 侧证据

本地 Dify API 源码中的调用位于：

```text
/home/zli2759/projects/dify-dm/api/core/plugin/impl/plugin.py
```

原调用逻辑为：

```python
return self._request_with_plugin_daemon_response(
    "GET",
    f"plugin/{tenant_id}/management/decode/from_identifier",
    PluginDecodeResponse,
    params={"plugin_unique_identifier": plugin_unique_identifier},
)
```

`base.py` 的请求封装会自动加入 daemon inner API 鉴权头：

```python
prepared_headers["X-Api-Key"] = dify_config.PLUGIN_DAEMON_KEY
```

因此问题不是缺失 API key、租户 ID 或路由地址，而是 API 把 identifier 放入 query string 时采用的字段名。日志中可见真实请求为：

```text
GET .../management/decode/from_identifier?
plugin_unique_identifier=li_zijun%2Ftest_tool_schema...
HTTP/1.1 400 Bad Request
```

daemon 返回体没有被 Console 原样显示，直连 daemon 后获得的原始错误为：

```json
{
  "code": -400,
  "message": "{\"message\":\"Key: 'PluginUniqueIdentifier' Error:Field validation for 'PluginUniqueIdentifier' failed on the 'required' tag\"}",
  "data": null
}
```

### 2.2 A-F 协议探针与结论

为确认接口实际接受的格式，从 API 容器中使用同一个 `X-Api-Key` 与同一插件 identifier 测试了多种请求：

| 探针 | 请求方式 | 结果 |
|---|---|---|
| A | GET query `plugin_unique_identifier` | 400，字段 required |
| B | GET query `PluginUniqueIdentifier` | 200，返回完整 manifest |
| C | GET query `pluginUniqueIdentifier` | 400 |
| D | GET JSON body `plugin_unique_identifier` | 200 |
| E | POST JSON snake_case | 404，route not found |
| F | POST JSON PascalCase | 404，route not found |

这组实验将问题从“版本可能不兼容”的猜测变为可重复的接口事实：此 daemon 的 GET query binder 实际接受 `PluginUniqueIdentifier`，而不是 API 发出的 snake_case query key。二进制字符串中也可找到 `decode/from_identifier`、`PluginUniqueIdentifier`、`json:\"plugin_unique_identifier\"` 等证据；最终以实际 HTTP 行为作为判定依据。

### 2.3 最小本地兼容性 patch

本地开发环境的最小修复仅修改 decode 调用这一处：

```diff
- params={"plugin_unique_identifier": plugin_unique_identifier},
+ params={"PluginUniqueIdentifier": plugin_unique_identifier},
```

审计 diff 保存于 `docs/api_decode_identifier_patch.diff`。API 容器未挂载本地 `api/` 源码，因此同一行 patch 临时应用到 `/app/api/core/plugin/impl/plugin.py` 并重启 `dify-api-1`。之后 daemon 日志变为：

```text
GET .../decode/from_identifier?PluginUniqueIdentifier=...
status=200
```

该 patch 仅用于本地兼容性验证，长期应通过升级经过验证的成套 Dify/API/daemon 版本或向上游提交兼容性修复解决。回滚方式是恢复 API 镜像或在本地源码中撤销该一行变更；它不涉及插件代码、数据库、volume 或 `.difypkg`。

## 三、runtime 依赖初始化与 wheels 离线机制

### 3.1 在线安装失败的现象

decode 修复后，官方模板终于进入真实安装阶段。daemon 日志明确显示：

```text
detected dependency file ... requirements.txt
installing plugin dependencies method="uv pip install"
failed to install dependencies: signal: killed
failed to init environment
```

模板 requirements 仅包含：

```text
dify_plugin>=0.4.0,<0.7.0
```

这说明即使一个最小官方模板，也会在 runtime 创建虚拟环境后解析并下载 SDK 及其传递依赖。资源诊断显示 plugin-daemon 未配置内存或 CPU 限制，Docker 容器可用内存约 11.68 GiB，WSL 可用内存约 9.1 GiB，`dmesg` 未出现 OOM 记录。因此 `signal: killed` 不能简单解释为内存不足。

日志和进程证据表明 uv 在执行：

```text
/usr/local/bin/uv pip install -i https://pypi.org/simple -r requirements.txt -vvv
```

它成功连接 `pypi.org` 与 `files.pythonhosted.org`，但在线解析与下载耗时超过 daemon 的环境初始化窗口，随后被 daemon 终止。安装任务表出现 `Task timed out but not properly terminated`，反映的是子进程在超时回收时未被及时正确收束，并非 worker 执行错误。

### 3.2 运行时缓解措施

为避免本地 Docker/WSL 环境中初次在线解析造成误杀，在本地 `plugin_daemon` override 中采取了可回滚措施：

```yaml
PYTHON_ENV_INIT_TIMEOUT: "900"
PLUGIN_PYTHON_ENV_INIT_TIMEOUT: "900"
PIP_MIRROR_URL: "https://pypi.org/simple"
UV_CONCURRENT_DOWNLOADS: "1"
UV_CONCURRENT_BUILDS: "1"
UV_CONCURRENT_INSTALLS: "1"
UV_HTTP_TIMEOUT: "300"
PIP_DEFAULT_TIMEOUT: "300"
```

其中 daemon 二进制与 Compose 均已验证读取 `PYTHON_ENV_INIT_TIMEOUT`、`PIP_MIRROR_URL`；`PLUGIN_PYTHON_ENV_INIT_TIMEOUT` 用于与主 Compose 映射保持一致。单并发设置是本地保守运行策略，目的不是掩盖问题，而是减少初次安装时的并发下载、解压和缓存竞争。

### 3.3 离线 wheels 的生产结论

在线安装可用于开发试验，但不适合作为生产插件交付的确定性依赖机制。Day2 确认推荐的插件发布模式为：

```text
requirements.txt
wheels/
```

requirements 应在离线交付场景中指向本地 wheels，例如：

```text
--no-index
--find-links=./wheels
```

验证中，初始 `test_tool_schema` 包不含 wheels；重新准备离线依赖后，包内包含 37 个 wheel，daemon 能够完成离线 runtime 安装。这个结果将依赖解析从不可控的外部网络操作转为可审计、可复现的包内容。后续所有生产插件，包括 DM 与 KingbaseES 扩展，都应固定依赖版本、生成与 daemon Python/平台匹配的 wheels，并在交付前解包核验。

## 四、Tool Provider 与 Tool 的逆向架构分析

### 4.1 分层职责

Dify Tool Plugin 不是把所有逻辑放进单个 `_invoke()`。逆向安装、声明与 Console 展示链路后，可以确认其分层模型如下：

| 层 | 核心职责 | 本项目对应内容 |
|---|---|---|
| Provider | 凭据表单、授权、连接验证、持久化配置 | 数据库类型、地址、端口、账号、密码、库名、超时 |
| Tool | 一次工具调用及业务执行 | 单次只读 SQL 请求与结果返回 |
| Runtime | 加载插件、维护凭据上下文、调度工具 | Python 虚拟环境与 Dify SDK runtime |

Provider 的 `_validate_credentials()` 应负责验证数据库连接是否可用，不承担 SQL 执行。Tool 的 `_invoke()` 应负责实际的单次查询、只读限制、行数限制、超时与结果转换。两层通过 `self.runtime.credentials` 共享已配置的连接信息。这个边界保证同一 Provider 可以承载多个查询类 Tool，也避免每次 Tool 调用重新暴露或重复配置凭据。

### 4.2 对 SQL 查询插件的意义

`db_query_extended` 的 Provider 表单已经声明 `database_type`、`host`、`port`、`username`、`password`、`database`、`connect_timeout` 等字段，并为 schema、charset 等扩展项预留位置。Tool 参数以 `sql`、`max_rows`、`timeout`、`readonly` 形成一次执行的输入边界。Workflow 中能显示“扩展数据库查询 / 只读 SQL 查询”及全部参数，证明 Tool 注册和声明解析正确。

这个设计也为后续数据库方言扩展建立了稳定边界：MySQL/PostgreSQL 的连接驱动和 SQL 方言适配应位于 Provider/公共数据库工具层；DM、KingbaseES 只能在确认驱动、连接串、错误码和只读策略后以同一接口扩展，而不是破坏 Tool 的调用模型。

## 五、`plugin_declarations` 结构与声明证据

plugin-daemon 的 `dify_plugin.plugin_declarations` 表是插件包被解析后的声明记录，不是安装成功记录。表主要字段包括：

```text
id
created_at
updated_at
plugin_unique_identifier
plugin_id
declaration
```

查询结果同时包含官方模板和 `db_query_extended` 的多个 checksum 版本，说明上传包已被 daemon 成功解析并写入 declaration。`declaration` JSON 中可以看到 `credentials_schema`，其中包含：

```text
database_type, host, port, username, password, database, connect_timeout
```

这项证据非常重要：它排除了“Provider YAML 未被解析”或“凭据字段未生成”的假设。安装成功后出现的 `ToolProviderNotFoundError: no default provider for li_zijun/db_query_extended/db_query_extended`，因此应被定位在 Provider 凭据实例、默认 Provider 选择或 Console 授权页面触发机制，而不是 declaration 生成阶段。

## 六、阶段结论与下一步边界

Day2 完成了插件交付链路的关键反向设计：包可打包和解包、daemon 可写入 declaration、API/daemon decode 契约已被定位并用本地 patch 绕过、离线 wheels 机制已验证、runtime 可启动、Tool 能注册到 Workflow。对 SQL 插件而言，这比单独验证某条 SELECT 更基础，因为它证明插件能进入 Dify 的真实产品链路。

下一阶段只处理 Provider Credential 的生成与默认选择：确认 Console “前往修复”如何创建 Provider credential、配置如何传入 `self.runtime.credentials`、为什么默认 provider 未找到，以及在 MySQL/PostgreSQL 上执行受控的 `SELECT * FROM students`。在此之前不新增 DM/KingbaseES 代码，不把运行时环境问题混入数据库方言实现，也不把临时 API patch 当作生产发布方案。
