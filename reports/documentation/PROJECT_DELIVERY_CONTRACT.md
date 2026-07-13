# Dify Multi-Database Plugin — Final Delivery Contract

- Status: ACTIVE / NORMATIVE / PROJECT-WIDE
- Effective date: 2026-07-13
- Last updated: 2026-07-13
- Scope: `db_query_extended` final delivery and all phase-closure decisions
- Maintainer: Project delivery governance
- Change policy: Update this file in place and preserve its Git history. Do not create versioned copies.

## 1. Purpose

本文件是 `db_query_extended` 项目的长期、规范性最终交付要求。

它不是某一个 Phase 的验收报告，也不能被单次 Provider、Tool、Workflow、打包或安装 PASS 所取代。所有后续 Phase 规划、验收、报告、发布判断和项目收尾都必须先读取本文件。

## 2. Final Deliverable 1 — Offline Installable Plugins

最终必须形成 DM8 与 KingbaseES 两套可离线安装并经过真实验证的插件交付物。每套交付物必须包含：

- 最终 `.difypkg`；
- 完整离线 wheels 和原生运行库；
- 固定版本的依赖清单；
- wheel、原生库和最终包的 SHA-256；
- 第三方许可证及 notice；
- 驱动来源和 provenance；
- Python、Linux、CPU 架构和 Dify/plugin-daemon 兼容信息；
- 无网络、`--no-index`、空环境安装证据；
- 真实 Dify 上传、安装、升级和 checksum 激活证据；
- 安装后 Provider 验证；
- 安装后 Tool 验证；
- Workflow API 验证；
- 真实数据库 fixture、Unicode、NULL、numeric、date、timestamp、schema、聚合、排序和行数契约验证；
- SQL 安全拦截；
- 错误信息和凭据脱敏；
- 失败后的连接清理；
- 回滚包、旧 checksum 和回滚步骤；
- 最终端到端证据链。

核心最终数据库：

```text
DM8
KingbaseES
```

SQL Server 的定位：

```text
OPTIONAL COMPATIBILITY GATE
```

SQL Server 用于证明适配架构和兼容流水线，但不替代 DM8 或 KingbaseES 的最终核心交付。

以下结果均不能单独等同于最终交付完成：

- Adapter import PASS；
- Driver import PASS；
- Provider PASS；
- Tool PASS；
- Offline dependency closure PASS；
- Candidate package PASS；
- Installed plugin PASS；
- Workflow PASS；
- 某一次回归矩阵 PASS。

只有规定的全部环节形成连续、可复核的证据链后，才能声明该数据库最终交付完成。

## 3. Final Deliverable 2 — Development Process Documentation

必须形成一份面向技术人员和技术领导的完整开发过程说明。文档必须从原始插件模板和最初环境开始，记录：

- 初始模板来源和结构；
- 最初需求和范围；
- 环境和版本；
- 目录演进；
- Provider、Tool、公共 utility、Adapter、dialect 和 formatter 的架构演进；
- 每个关键 Phase 的目标和验收边界；
- 实际执行命令；
- 创建、修改和删除的文件；
- 关键代码变化；
- 技术决策及其理由；
- blocker 和错误现象；
- 根因分析；
- 诊断命令；
- 尝试过但放弃的路线；
- 最终解决方案；
- 回归和证据；
- Git commit、branch、checksum 和 hash；
- 环境故障及恢复过程；
- 数据库持久化问题；
- Dify/plugin-daemon 兼容问题；
- 驱动、原生库和许可证问题；
- 离线打包与安装过程；
- 回滚方法；
- 最终发布边界。

开发历史必须保留失败过程和废弃路线，不能只留下修复后的最终代码。

报告管理要求：

- 人类可读报告和机器证据分开；
- verification JSON 与 logs 分开；
- 按日期、Phase 和数据库分类；
- canonical report 路径明确；
- `REPORT_MAP.md` 或等效索引持续更新；
- 日志和证据必须脱敏；
- 不得把临时 harness 或本地凭据误列为正式产品文件。

## 4. Final Deliverable 3 — From-Zero Reproduction Tutorial

必须形成一份可以独立执行的从零复现教程。

读者假设：

```text
只拥有原始插件模板、教程和合法取得的数据库/驱动介质。
```

教程不能假设读者已经拥有当前工作目录、现有容器、现有插件安装、现有数据库 fixture 或当前开发者的本地环境。教程必须明确说明：

- 支持的 Windows、WSL、Docker、Dify、Python 和 CPU 架构；
- 软件安装顺序；
- 下载来源；
- license 和官方介质边界；
- 仓库放置位置；
- 目录结构；
- 每一步应进入哪个目录；
- 每一步执行什么 PowerShell、WSL、Docker 或 Python 命令；
- 每一步创建什么文件；
- 每一步修改什么代码；
- 应删除或替换哪些模板内容；
- Provider YAML 如何配置；
- Tool YAML 如何配置；
- Adapter 和 dialect 如何实现；
- 数据库如何启动和初始化；
- 测试账号和只读权限如何建立；
- fixture 如何写入；
- 如何启动 Dify；
- 如何通过浏览器进入 Dify；
- 如何安装插件；
- Provider 表单每个字段如何填写；
- 如何创建 Workflow；
- 如何取得和配置 Workflow API key；
- 如何执行 Provider、Tool 和 Workflow 验证；
- 如何完成离线 wheel 收集；
- 如何运行无网络闭环；
- 如何构建 `.difypkg`；
- 如何计算 checksum；
- 如何安装和升级同版本不同 checksum 的插件；
- 如何验证安装后的真实 runtime；
- 如何检查日志；
- 如何判断失败属于数据库、驱动、插件、Dify、daemon、Workflow 还是环境问题；
- 如何回滚；
- 如何形成最终证据。

每个重要步骤都需要包括：

```text
目的
前置条件
工作目录
完整命令
预期输出
PASS 条件
FAIL 含义
排查方法
产生的文件
证据路径
```

教程必须能够让另一位具备技术能力的人从原始模板独立复现当前最终成果。

## 5. Current Project State

截至 2026-07-12：

### KingbaseES Phase 9.8

状态：

```text
PASS
```

已证明：

```text
KINGBASEES_OFFLINE_DEPENDENCY_CLOSURE_PASS
KINGBASEES_CANDIDATE_PACKAGE_PASS
KINGBASEES_INSTALLED_PROVIDER_PASS
KINGBASEES_INSTALLED_TOOL_PASS
```

主要事实：

- `ksycopg2==2.9.1` 已固定；
- 驱动 wheel 与 `libkci.so.5` 已通过原生依赖检查；
- 44 个 wheels 已完成 network-none、no-index 离线安装闭环；
- KingbaseES candidate `.difypkg` 已构建；
- 已通过真实 Dify PluginService 和 PluginInstaller 安装、升级；
- tenant active checksum 已切换；
- 安装后 Provider 9/9 PASS；
- 安装后 Tool 14/14 PASS；
- PostgreSQL 定向回归 4/4 PASS；
- 所有数据库 Adapter 均可从安装 runtime 导入；
- Phase 9.5 overlay 未使用；
- 回滚包和旧 checksum 均保留。

尚未证明：

```text
KINGBASEES_WORKFLOW_PASS
KINGBASEES_END_TO_END_PASS
KINGBASEES_FINAL_OFFLINE_DELIVERY_PASS
FINAL_PROJECT_DELIVERY_PASS
```

下一阶段：

```text
Phase 9.9 — Installed KingbaseES Workflow API and End-to-End Gate
```

不得在 Phase 9.9 完成之前，把 Phase 9.8 描述为 KingbaseES 最终端到端交付完成。

Phase 9.8 canonical report：

`reports/documentation/2026-07-12/Phase09_KingbaseES/phase9_8_kingbasees_offline_packaging_installed_plugin_gate.md`

## 6. Phase Closure Rules

以后每个 Phase 的报告必须明确区分：

- 本 Phase 测试范围；
- 已验证的内容；
- 未验证的内容；
- 允许声明的结论；
- 禁止声明的结论；
- 是否影响最终三类交付物；
- 哪些内容必须进入开发历史；
- 哪些内容必须进入从零教程；
- 哪些内容只是机器证据；
- 下一阶段是什么。

报告结尾必须同时包含：

```text
PHASE_STATUS
ALLOWED_CONCLUSIONS
NOT_YET_PROVEN
FINAL_DELIVERY_IMPACT
NEXT_PHASE
```

## 7. Final Completion Rule

只有在以下条件全部满足后，才可以声明项目最终完成：

- DM8 最终离线包完成；
- KingbaseES 最终离线包完成；
- 两者均通过真实 Dify 安装；
- 两者均通过 Provider；
- 两者均通过 Tool；
- 两者均通过 Workflow API；
- 两者均通过真实数据端到端验证；
- 离线依赖闭环可重跑；
- checksum、hash 和回滚材料完整；
- 许可证与再分发边界已如实记录；
- 开发流程说明完成；
- 从零复现教程完成；
- 报告、证据和日志索引完整；
- 未解决事项和法律边界没有被错误标记为完成。

在此之前只能声明相应 Phase 或子门禁 PASS，不得声明：

```text
FINAL DELIVERY COMPLETE
PROJECT COMPLETE
PRODUCTION RELEASE COMPLETE
```
