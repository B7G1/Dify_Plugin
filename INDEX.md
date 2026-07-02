# 工作区索引

| 类别 | 位置 | 说明 |
| --- | --- | --- |
| Project Cockpit | [reports/html_reports/2026-06-24/project_dashboard.html](reports/html_reports/2026-06-24/project_dashboard.html) | 项目统一入口，包含时间线、文档、验证、资产、知识库和恢复命令。 |
| 交互式步骤地图 | [reports/html_reports/2026-06-26_interactive_step_map/project_map.html](reports/html_reports/2026-06-26_interactive_step_map/project_map.html) | 从旧 Step 12 之后续写 Step 13 到 Step 24，展示每一步代码和文件变化。 |
| Documentation 总入口 | [reports/documentation/README.md](reports/documentation/README.md) | 给人读的阶段文档。新人从这里理解项目过程。 |
| Verification 总入口 | [reports/verification/README.md](reports/verification/README.md) | 给机器和验收看的证据、日志、JSON 和自动化输出。 |
| Phase 1 文档 | [reports/documentation/Phase1_Project_Setup/README.md](reports/documentation/Phase1_Project_Setup/README.md) | 环境搭建与项目研究。 |
| Phase 2 文档 | [reports/documentation/Phase2_Plugin_Development/README.md](reports/documentation/Phase2_Plugin_Development/README.md) | 插件开发与本地验证。 |
| Phase 3 文档 | [reports/documentation/Phase3_Platform_Integration/README.md](reports/documentation/Phase3_Platform_Integration/README.md) | Dify 平台联调过程。 |
| Phase 4 文档 | [reports/documentation/Phase4_Core_Freeze/README.md](reports/documentation/Phase4_Core_Freeze/README.md) | 插件核心冻结与报告体系整理。 |
| Phase 5 文档 | [reports/documentation/Phase5_Database_Adapter_Freeze/README.md](reports/documentation/Phase5_Database_Adapter_Freeze/README.md) | 数据库 Adapter 架构冻结。 |
| Phase 5.5 文档 | [reports/documentation/Phase5_5_Workflow_Automation_Completion/README.md](reports/documentation/Phase5_5_Workflow_Automation_Completion/README.md) | Workflow API 自动化验收。 |
| Phase 6 文档 | [reports/documentation/Phase6_Release_Freeze/README.md](reports/documentation/Phase6_Release_Freeze/README.md) | 0.1.0 Release Freeze 与交付资料。 |
| Phase 7 文档 | [reports/documentation/Phase7_Domestic_Database_Adapters/README.md](reports/documentation/Phase7_Domestic_Database_Adapters/README.md) | DM8/KingbaseES Adapter 规划入口。 |
| Phase 7.1 最终报告 | [reports/documentation/Phase7_1_DM8_Adapter/README.md](reports/documentation/Phase7_1_DM8_Adapter/README.md) | DM8 Workflow API：12 PASS / 0 FAIL / 0 SKIP。 |
| Release 0.1.0 | [release/db_query_extended/0.1.0/README.md](release/db_query_extended/0.1.0/README.md) | 插件包、校验值、Release Notes、ADR 与验证证据。 |
| 2026-06-25 验证证据 | [reports/verification/2026-06-25/README.md](reports/verification/2026-06-25/README.md) | Console、plugin-daemon、Workflow UI/API、错误密码路径和最终矩阵证据。 |
| 2026-06-26 验证证据 | [reports/verification/2026-06-26/README.md](reports/verification/2026-06-26/README.md) | Plugin Core Freeze 验证输出和矩阵。 |
| Cockpit 数据副本 | [reports/html_reports/2026-06-24/data/cockpit-data.json](reports/html_reports/2026-06-24/data/cockpit-data.json) | 项目驾驶舱的机器可读数据副本。 |
| 插件源码 | [db_query_extended/](db_query_extended/README.md) | Dify 插件实现。 |
| 数据库核心 | [db_query_extended/utils/database.py](db_query_extended/utils/database.py) | Adapter 调度、Engine 生命周期、异常映射和查询执行。 |
| 数据库 Adapter | [db_query_extended/utils/adapters/](db_query_extended/utils/adapters/) | MySQL/PostgreSQL 驱动与会话差异。 |
| 格式化核心 | [db_query_extended/utils/formatter.py](db_query_extended/utils/formatter.py) | 稳定 JSON 输出和 JSON-safe 转换。 |
| SQL 校验器 | [db_query_extended/utils/sql_validator.py](db_query_extended/utils/sql_validator.py) | SQL-aware 只读校验。 |
| Tool 入口 | [db_query_extended/tools/db_query_extended.py](db_query_extended/tools/db_query_extended.py) | Dify Tool 执行入口。 |
| Provider 入口 | [db_query_extended/provider/db_query_extended.py](db_query_extended/provider/db_query_extended.py) | 凭据验证入口。 |
| 插件验证脚本 | [db_query_extended/verify_plugin.ps1](db_query_extended/verify_plugin.ps1) | Provider、SQL 安全、格式化、数据库矩阵和可选 Workflow API 验证。 |
| 一键完整回归 | [db_query_extended/verification/verify_all.ps1](db_query_extended/verification/verify_all.ps1) | Provider → Tool → Workflow → Summary，要求 FAIL=0 且 SKIP=0。 |
| 本地测试数据库 | [local_test_db/](local_test_db/README.md) | MySQL 8.4 / PostgreSQL 16 可复现测试环境。 |
| 本地数据库验证 | [local_test_db/verification/verify.ps1](local_test_db/verification/verify.ps1) | 启动并检查数据库，执行验收 SQL。 |
| 验证 SQL | [local_test_db/verification/verification.sql](local_test_db/verification/verification.sql) | MySQL / PostgreSQL 共用验收 SQL。 |
| 历史 HTML 快照 | [reports/html_reports/2026-06-23/project_map.html](reports/html_reports/2026-06-23/project_map.html) | 2026-06-23 旧版项目地图，只读归档。 |
| 插件包归档 | [archive/](archive/) | `.difypkg` 产物和历史归档。 |
| 分析资料 | [analysis/](analysis/) | 历史分析与调研材料。 |
| 文档资料 | [docs/](docs/) | 支撑文档。 |
