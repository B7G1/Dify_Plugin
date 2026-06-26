# 项目文档 Documentation

这里是 `db_query_extended` 的人读报告体系。

适合用来理解：

- 做了什么；
- 为什么这样做；
- 遇到了什么问题；
- 问题怎么解决；
- 下一步应该做什么。

机器证据、日志、JSON 输出、Docker 输出和 API 返回放在 `reports/verification/`。

## 阶段索引

| 阶段 | 状态 | 入口 |
| --- | --- | --- |
| Phase 1 | 已完成 | [环境搭建与项目研究](Phase1_Project_Setup/README.md) |
| Phase 2 | 已完成 | [插件开发](Phase2_Plugin_Development/README.md) |
| Phase 3 | 已完成 | [平台联调](Phase3_Platform_Integration/README.md) |
| Phase 4 | 已完成 | [Plugin Core Freeze](Phase4_Core_Freeze/README.md) |
| Phase 5 | 待开始 | [DM Adapter](Phase5_DM_Adapter/README.md) |
| Phase 6 | 未来范围 | [KingbaseES Adapter](Phase6_KingbaseES_Adapter/README.md) |

## 推荐阅读路径

1. 打开 `reports/html_reports/2026-06-24/project_dashboard.html`。
2. 阅读本 Documentation 索引。
3. 重点阅读 Phase 3 和 Phase 4，理解当前已验证基线。
4. 打开 `reports/html_reports/2026-06-26_interactive_step_map/project_map.html`，查看 Step 13 到 Step 24 的具体代码和文件变化。
5. 只有需要查验证证据时，再进入 `reports/verification/`。

