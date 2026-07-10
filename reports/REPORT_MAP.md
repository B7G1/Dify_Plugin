# 报告地图

更新日期：2026-07-07  
用途：按日期、进度、分类快速找到报告、log、测试数据和可视化地图。

## 先看哪里

| 需要 | 入口 |
|---|---|
| 对外中文汇报 | `root_reports/当前状态.md` |
| 当前报告总入口 | `README.md` |
| v1.0 发布材料 | `release/v1.0/README.md` |
| Phase 7.1 DM8 最终验收 | `documentation/Phase7_1_DM8_Adapter/README.md` |
| Phase 7.1 DM8 数据能力补证 | `documentation/Phase7_1_DM8_Adapter/data_capability_evidence_closure_2026-07-06.md` |
| Phase 7.2 多语种 stored-data exact equality | `documentation/Phase7_2_Multilingual_Compatibility/README.md` |
| Phase 7.3 全适配器回归 | `documentation/Phase7_3_Full_Adapter_Regression/README.md` |
| Phase 9 KingbaseES feasibility | `documentation/Phase9_KingbaseES_Feasibility/phase9_kingbasees_official_media_runtime_feasibility.md` |
| Phase 10 KingbaseES | `documentation/Phase10_KingbaseES_Adapter/README.md` |
| Phase 11 SQL Server 环境门 | `documentation/Phase11_SQLServer_Adapter/environment_gate.md` |
| 可视化地图 / dashboard | `html_reports/` |
| 机器证据、log、测试数据 | `verification/` |

## 按分类

| 分类 | 目录 | 当前内容 |
|---|---|---|
| 当前状态 | `root_reports/当前状态.md` | 每次对话后中文更新的汇报文件 |
| 人读报告 | `documentation/` | 68 个文件，按 Phase 归档 |
| 验证证据 | `verification/` | 71 个文件，按日期归档 JSON / log / 结果 |
| 可视化地图 | `html_reports/` | 72 个文件，含项目地图、dashboard、HTML 报告 |
| 发布材料 | `release/` | v1.0 release notes、兼容性、迁移、检查表 |
| 环境快照 | `snapshots/` | 不可变环境身份记录 |
| 统计 | `statistics/` | 最终统计 |
| 架构入口 | `architecture/` | 指向根目录架构图 |
| 归档 | `archive/` | 过期或重复材料说明 |

## 按日期

| 日期 | 内容 | 位置 |
|---|---|---|
| 2026-06-25 | 工作流、插件 daemon、错误路径等早期验收 | `verification/2026-06-25/` |
| 2026-06-26 | Core Freeze 验证、交互式步骤地图 | `verification/2026-06-26/`、`html_reports/2026-06-26_interactive_step_map/` |
| 2026-06-28 | Adapter 架构冻结证据 | `verification/2026-06-28/` |
| 2026-06-29 | DM8 / Phase 7.1 草稿和部分验证 | `verification/2026-06-29/` |
| 2026-06-30 | 环境启动、Postgres 持久化、备份和恢复实验 | `verification/2026-06-30/` |
| 2026-07-01 | v1.0 最终冷启动验收和发布 dashboard | `verification/2026-07-01/`、`html_reports/2026-07-01_phase7_1_final/` |
| 2026-07-02 | KingbaseES Phase 10 mock、packaging、真实状态 | `verification/2026-07-02/phase10_kingbasees/` |
| 2026-07-09 | Phase 9 KingbaseES official media/runtime feasibility gate | `verification/2026-07-09/kingbasees_official_media_inventory.json`、`verification/2026-07-09/kingbasees_driver_runtime_probe.json` |
| 2026-07-03 | SQL Server 环境门最终 PASS 证据写入 Phase 11 文档 | `documentation/Phase11_SQLServer_Adapter/environment_gate.md` |
| 2026-07-06 | DM8 14 项数据能力完整 JSON evidence；Provider/Tool regression 重跑 | `verification/2026-07-06/dm8_data_capability_closure/`、`verification/2026-07-06/regression_after_dm8_data_capability/` |
| 2026-07-07 | Phase 7.2 多语种已存储数据 exact equality gate；MySQL / PostgreSQL / DM8 PASS | `documentation/Phase7_2_Multilingual_Compatibility/`、`verification/2026-07-07/multilingual_dm_result.json` |
| 2026-07-07 | Phase 7.3 MySQL / PostgreSQL / DM8 full adapter regression gate PASS；Phase 7.3b Workflow rerun PASS；verify_all 45/0/0 | `documentation/Phase7_3_Full_Adapter_Regression/`、`verification/2026-07-07/phase7_3b_verify_all/summary.json` |

## 按进度

| 阶段 | 状态 | 主报告 |
|---|---|---|
| Phase 1-6 | 历史完成 | `documentation/Phase1_Project_Setup/` 到 `documentation/Phase6_Release_Freeze/` |
| Phase 7 / 7.1 | DM8 验收完成；数据能力 evidence closure COMPLETE | `documentation/Phase7_1_DM8_Adapter/data_capability_evidence_closure_2026-07-06.md` |
| Phase 7.2 | Multilingual Compatibility PASS；MySQL / PostgreSQL / DM8 stored multilingual exact equality gate 全部通过 | `documentation/Phase7_2_Multilingual_Compatibility/README.md` |
| Phase 7.3 | Full Adapter Regression PASS；Provider 6/0/0，Tool 27/0/0，Workflow 12/0/0，verify_all 45/0/0 | `documentation/Phase7_3_Full_Adapter_Regression/README.md` |
| Phase 8-9.5 | v1.0 产品化和公开发布材料完成 | `documentation/Phase9_5_Public_Release/` |
| Phase 9 | KingbaseES official media/runtime feasibility blocked on official media | `documentation/Phase9_KingbaseES_Feasibility/phase9_kingbasees_official_media_runtime_feasibility.md` |
| Phase 10 | KingbaseES 适配推进中 | `documentation/Phase10_KingbaseES_Adapter/phase_status.md` |
| Phase 11 | 数据库扩展和 SQL Server 环境门推进中 | `documentation/Phase11_Database_Expansion/`、`documentation/Phase11_SQLServer_Adapter/` |

## 历史中文报告

| 目录 | 处理方式 |
|---|---|
| `root_reports/过往报告/` | 已从仓库根目录集中到 `reports/root_reports/`，作为早期中文报告归档 |
| `root_reports/最新报告/` | 已从仓库根目录集中到 `reports/root_reports/`，视为 2026-06-29 的历史“最新报告”入口 |

ponytail: 没有搬动 Quarto/HTML 资源目录；等确认所有链接都能重写时再物理迁移。

## Phase 7.2 credential boundary

`DIFY_TEST` 仅用于本地 DM8 管理员交互式授权 `GRANT CREATE TABLE TO "PLUGIN_TEST_OWNER";`，不属于 Provider / Adapter / Tool / Workflow 正常运行凭据。插件运行和验证路径仍使用只读账号 `PLUGIN_TEST_USER`。不得在报告、脚本、截图或 evidence 中记录 `DIFY_TEST` 密码。

Phase 7.2 frontend screenshot evidence is COMPLETE: FE-15 through FE-24 are present and project-owner manual visual review is PASS. Independent machine-vision verification was not performed. The machine exact-equality gate remains PASS as the primary deterministic evidence.
