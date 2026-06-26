# Dify Plugin 工作区

本工作区用于开发、验证和归档 `db_query_extended`：一个面向 MySQL / PostgreSQL 的 Dify 只读 SQL 查询插件。

## 当前状态

### 2026-06-26 · Plugin Core Freeze

- 已在开始 DM / KingbaseES 适配前完成公共核心整理。
- 数据库连接创建逻辑集中在 `db_query_extended/utils/database.py`。
- 查询结果格式化集中在 `db_query_extended/utils/formatter.py`。
- SQL 只读校验收紧为单条 `SELECT` 或 `WITH`。
- Provider 凭据表单保持稳定。
- 本地数据库验收：PASS。
- 插件级验证：74 PASS / 0 FAIL / 1 SKIP。
- Project Cockpit 已完成中文化。
- 交互式步骤地图已从旧 Step 12 续写到 Step 24。

### 2026-06-25 · 平台联调

- Dify Console 已恢复。
- plugin-daemon 已恢复并加载 `li_zijun/db_query_extended:0.0.1`。
- 插件已安装到当前 Workspace。
- Workflow App `Plu_Test` 已创建并发布。
- MySQL Workflow UI 验证：PASS。
- PostgreSQL Workflow UI 验证：PASS。
- Workflow API 自动化验证：PASS。
- 错误密码异常路径：PASS。
- `verify_plugin.ps1`：57 PASS / 0 FAIL / 0 SKIP。

## 主要入口

- [Project Cockpit 项目驾驶舱](reports/html_reports/2026-06-24/project_dashboard.html)
- [交互式步骤地图：Step 13 到 Step 24](reports/html_reports/2026-06-26_interactive_step_map/project_map.html)
- [Documentation 人读报告](reports/documentation/README.md)
- [Verification 验证证据](reports/verification/README.md)
- [Phase 4 Plugin Core Freeze](reports/documentation/Phase4_Core_Freeze/README.md)
- [Phase 3 平台联调](reports/documentation/Phase3_Platform_Integration/README.md)
- [本地 MySQL / PostgreSQL 测试库](local_test_db/README.md)
- [插件源码](db_query_extended/README.md)
- [工作区索引](INDEX.md)

## 报告体系

- Documentation：给人读，包含阶段概述、每日总结、架构说明和踩坑记录。
- Verification：给机器和验收看，保存 JSON、日志、transcript、Docker 输出、plugin-daemon 输出和 Workflow 输出。
- Project Cockpit：统一入口，串起 Documentation、Verification、资产、时间线、知识库和恢复命令。
- Interactive Step Map：按步骤展示“每一步改了什么代码、影响哪些文件、平台链路如何变化”。

## 后续范围

- DM Adapter。
- KingbaseES Adapter。
- 真实连接池生命周期。
- Markdown 展示输出。
- 生产环境 SSL / 证书场景。

