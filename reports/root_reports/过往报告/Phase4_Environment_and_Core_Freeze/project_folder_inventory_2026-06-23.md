# E:\Dify_Plugin 工程文件夹盘点（2026-06-23）

本盘点只读取现状并提出用途判断；**未移动、删除、重命名或压缩任何文件**。路径和类型以 2026-06-23 的目录枚举为准。

| 路径 | 类型 | 用途判断 | 保留 | 建议移动 | 建议目标位置 | 风险说明 |
|---|---|---|---|---|---|---|
| `.git/` | Git 元数据目录 | 当前工作区版本历史 | 是 | 否 | 原位 | 不能手工移动或删除。 |
| `.agents/` | 工具工作目录 | 当前协作工具状态 | 是 | 否 | 原位 | 用途由工具管理，暂不整理。 |
| `analysis/junjiem-db_query_0.0.11/` | 分析目录 | 上游/离线插件分析材料 | 是 | 是（待确认） | `analysis/junjiem-db_query_0.0.11/`（保持实际名称即可） | 当前已符合分析归档语义；先检查内部相对链接。 |
| `db_query_extended/` | 插件源码目录 | 当前本地插件开发源码 | 是 | 是（待确认） | `plugins/db_query_extended/` | 移动会影响 `.difypkg` 构建上下文、README 与本地命令。 |
| `db_query_extended_interactive_map/` | 地图项目目录 | 交互式复现地图外层目录 | 是 | 是（待确认） | `interactive_maps/db_query_extended_interactive_map/` | 内层同名目录存在，迁移前应先处理层级设计与链接。 |
| `env_check/` | 环境检查目录 | Python / 依赖检查脚本或输出 | 是 | 是（待确认） | `logs/environment_checks/` 或 `tools/env_check/` | 先区分可执行脚本与一次性日志。 |
| `test_tool_schema/` | 测试/样例插件目录 | Tool schema 测试材料 | 是 | 是（待确认） | `tests/test_tool_schema/` 或 `plugins/samples/test_tool_schema/` | 若仍用于 Dify 安装测试，不能当作纯日志。 |
| `最新报告/` | 当前报告目录 | 2026-06-23 报告、日志快照、研究资料 | 是 | 是（待确认） | 保留根目录，按主题建立子目录 | 多份 Markdown/HTML 可能互相引用。 |
| `过往报告/` | 历史报告目录 | 前期调研与流程记录 | 是 | 是（待确认） | `archive/reports/` | 迁移前需检查 `README.md` 中的相对链接。 |
| `db_query_extended.difypkg` | 插件包 | 当前插件安装/分发包 | 是 | 是（待确认） | `packages/db_query_extended/` | Dify 控制台手动安装路径会改变。 |
| `junjiem-db_query_0.0.11-offline.difypkg` | 离线插件包 | 上游/对照插件包 | 是 | 是（待确认） | `packages/reference/` | 分析报告可能引用当前根目录文件名。 |
| `test_tool_schema.difypkg` | 测试插件包 | Tool schema 验证包 | 是 | 是（待确认） | `packages/tests/` | 需与 `test_tool_schema/` 同步迁移。 |
| `dify-plugin.exe` | Windows CLI 二进制 | Dify Plugin CLI | 是 | 是（待确认） | `tools/dify-plugin/windows-amd64/` | `.gitignore` 当前专门列出该文件；脚本/PATH 可能引用根目录。 |
| `dify-plugin-windows-amd64.exe` | Windows CLI 二进制 | CLI 的同类命名副本 | 暂保留 | 是（待确认） | `tools/dify-plugin/windows-amd64/` | 两个 55 MB 文件可能重复，未做哈希比对，不能删除。 |
| `.gitignore` | Git 配置文件 | 忽略 CLI、编辑器/系统噪声 | 是 | 否 | 原位 | 已有未提交修改，不能覆盖。 |
| `.Rhistory` | 空文件 | R 会话遗留 | 否（可确认后归档/删除） | 是（待确认） | `archive/local-state/` 或删除 | 不影响插件；本轮禁止删除。 |
| `最新报告/.Rhistory` | 空文件 | R 会话遗留 | 否（可确认后归档/删除） | 是（待确认） | `archive/local-state/` 或删除 | 同上。 |
| `最新报告/baseline_day1_2026-06-23.md` | Day 1 基线报告 | 可比对的环境/插件/测试数据库基线 | 是 | 否 | 当前报告目录 | 应成为后续报告的稳定引用入口。 |
| `最新报告/baseline_day1_2026-06-23.html`、`README.html` | HTML 导出物 | Markdown 报告的可视化导出 | 是 | 是（待确认） | `最新报告/exports/` | 大文件；迁移前确认报告内静态资源是否内联。 |
| `最新报告/logs/` | 日志目录 | 环境快照与诊断输出 | 是 | 否 | 当前报告目录 | 已具有合理位置。 |
| `最新报告/01_*`、`02_*`、`03_*` | 研究报告目录 | 技术调研、反向设计、DM/Kingbase 设计 | 是 | 否（先保持） | 当前报告目录下按编号分类 | 已有编号结构，先勿机械改名。 |
| `db_query_extended_interactive_map/db_query_extended_interactive_map/` | 静态网页项目 | 本次更新的交互式复现地图 | 是 | 否（外层迁移前） | 保持相对 `assets/`、`data/` 结构 | `index.html` 依赖 `assets/*` 和 `data/*.json` 相对路径。 |

## 已发现的重复/可疑项（仅标注）

1. 根目录两个 Dify Plugin CLI EXE 尺寸均为 55,001,600 bytes，**可能**是同一二进制的不同文件名；尚未计算哈希，不能判定或删除。
2. 地图目录有外层和内层同名目录，阅读和迁移时容易漏层；这不是立即需要修复的问题。
3. 根目录与 `最新报告/` 各有一个空 `.Rhistory`，均为低风险遗留，但本轮未处理。

## Git 记录（仅检查）

- 当前分支：`main`
- 远端：`origin https://github.com/B7G1/Dify_Plugin.git`（fetch / push）
- 工作区不是干净状态：已有 `.gitignore` 修改、旧本地化流程文件及其静态资源被标记删除，以及多个未跟踪目录/包。它们早于本次盘点，不能归因于本报告。
- 本轮没有 `git add`、commit 或 push。
