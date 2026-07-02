# 项目目录与归档约定

## 当前目录职责

| 路径 | 作用 | 归档建议 |
|---|---|---|
| `provider/` | Provider YAML 与 Python：凭据表单、连接验证、授权边界 | 保持为插件运行时代码 |
| `tools/` | Tool YAML 与 Python：一次调用的参数、业务执行与输出 | 保持为插件运行时代码 |
| `utils/` | 数据库、校验、异常与数据转换公共模块 | 保持为插件运行时代码 |
| `_assets/` | 插件图标等静态资源 | 保持在根目录，供 manifest 引用 |
| `wheels/` | 离线 Python 依赖 wheel | 生产交付前生成并纳入包；当前目录可在准备 wheels 时创建 |
| `sql/` | MySQL/PostgreSQL 测试库初始化脚本 | 开发测试资源，不属于插件 runtime |
| `docs/reports/` | 分日研究报告与验收记录 | Day1/Day2 等正式归档位置 |
| `docs/analysis/` | 协议探针、Provider 架构、数据库方言等专题分析 | 后续新增分析文档放置处 |
| `docs/screenshots/` | Console、Provider、Workflow 和错误页面证据 | 仅保存脱敏截图 |
| `docs/logs/` | 脱敏后的 daemon/API/worker 日志片段 | 大日志不要散落在根目录 |
| `docs/references/` | 官方资料、CLI 模板对照、版本兼容性引用 | 保存链接、摘录与版本说明 |

## 根目录文件处理建议

根目录中没有散落的 `.txt`、`.log` 或 `.json` 文件；主要 Markdown 文件为 `README.md`、`GUIDE.md`、`PRIVACY.md`。其中 `README.md`、`PRIVACY.md`、`manifest.yaml`、`requirements.txt`、`main.py`、`provider/`、`tools/`、`utils/`、`_assets/` 是插件标准交付内容，建议保持原位。

`GUIDE.md` 是模板开发说明，建议在确认不再被 manifest、README 或团队流程直接引用后，复制或移动至 `docs/references/cli_template_guide.md`。本轮不移动它，避免影响现有模板结构和打包对照。

下列已有资料建议后续归档（本轮仅给出建议，不移动原文件）：

- `docs/plugin_daemon_logs_before.txt`：迁入 `docs/logs/`。
- `docs/plugin_daemon_inspect_before.json`：迁入 `docs/logs/` 或 `docs/analysis/`，并继续保持脱敏。
- `docs/api_decode_identifier_patch.diff`：迁入 `docs/analysis/`，作为本地运行时兼容性 patch 审计证据。
- `docs/dev_environment.md`：可复制整理为 `docs/reports/day1_environment_setup.md`，保留原文件作为环境操作说明。
- `docs/dify_runtime_recovery.md`、`docs/dify_workflow_validation.md`：保留在 `docs/` 作为持续维护的运行时记录；阶段性结论在 `docs/reports/` 中汇总。

## 交付前检查

生产 `.difypkg` 应只包含 manifest、入口代码、Provider/Tool、utils、assets、privacy、requirements 与经过验证的 `wheels/`。测试 SQL、Docker Compose、运行日志、截图、报告、旧 `.difypkg` 与本地虚拟环境应由 `.difyignore` 排除。每次打包后应解包核对文件清单和依赖 wheel 数量。
