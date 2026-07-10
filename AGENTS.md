# Dify Plugin 长期开发目标与记录原则

## 适用范围

本仓库是 `Multi-Database Compatibility Engineering for a Dify Plugin Runtime`，不只是数据库查询插件。

继续正常数据库兼容开发，但从现在开始按最终三类交付目标保存开发轨迹和复现信息。本文件不是立即执行 final delivery 的任务：不要仅因本文件暂停当前开发、整理最终 deliverables、重构 `reports/`、编写完整教程或复制文件到新的交付目录。

后续任务先解决当前真实技术目标，同时留下足以支持最终交付的最小必要记录。不要为了记录而创建没有复用价值的脚本、抽象或目录。

## 最终三类交付目标

### Final Output 1 — Offline-installable database plugin package

最终核心数据库交付目标是 DM8 和 KingbaseES。SQL Server 主要保留为兼容工程和验证流水线案例。

离线交付必须能够证明完整链路：

```text
source
-> requirements
-> compatible wheels
-> offline dependency closure
-> plugin package
-> plugin-daemon install
-> Provider validation
-> Tool execution
-> Workflow execution
```

最终应保留：

- plugin source 和 requirements；
- Linux x86_64 / Python 3.12 compatible wheels；
- database Python driver 和 SQLAlchemy dialect dependency；
- environment preparation files；
- package build command、`.difypkg` 和 SHA-256；
- installation instructions、validation scripts 和 minimum machine evidence。

当前不创建最终交付目录。后续凡涉及 driver、wheel、runtime、packaging 或 plugin installation，必须记录足够信息以便最终闭合离线依赖与安装证据链。

### Final Output 2 — Development Process Document

最终文档是工程历史、架构演进、技术决策记录、blocker/incident review 和兼容方法论，不是操作教程。仓库记录最终必须能够还原：

1. 初始模板、目录结构及 Provider / Tool / database utility 的初始职责；
2. 初始数据库支持范围；
3. Adapter abstraction 的动机、interface 演进，以及 Database / Dialect / Driver / SQLAlchemy / Adapter 的关系；
4. MySQL / PostgreSQL baseline，以及 DM8、KingbaseES 适配过程；
5. SQL Server compatibility pipeline 案例；
6. driver selection、offline wheel、plugin-daemon runtime 与普通 Python runtime 的差异；
7. Provider / Tool / Workflow 分层验证的原因；
8. blocker、错误判断、abandoned path、root cause、fix 和 evidence；
9. 最终形成的数据库兼容工程方法。

当前不编写完整文档。每个开发任务结束时检查：未来能否仅根据仓库记录还原本步；不能时，补充最小必要记录。

### Final Output 3 — Build-from-Template Tutorial

最终教程面向具备基础 Python、Docker、PowerShell 能力的技术人员。读者只拿到最初 Dify plugin template，不依赖本项目历史或 `reports/`，也应能开发并验收最终插件。

教程最终必须明确环境和版本、软件、目录、命令、文件增删改、代码变化及原因、预期输出和 PASS 判断、故障检查、测试数据库、driver、wheels、offline dependency closure、`.difypkg` 构建、Dify 安装、Provider 配置、Tool / Workflow 执行与最终验收。

当前不编写完整教程。每个开发任务只保存未来教程实际需要的准确复现信息。

## 数据库兼容证据链

后续数据库兼容工作沿用：

```text
Database Target
-> Driver Feasibility
-> Runtime Dependency
-> Real Connection
-> Adapter
-> Offline Packaging
-> Plugin Runtime
-> Provider
-> Tool
-> Workflow
-> Regression / Release Gate
```

某一层 PASS 不得越级表述为数据库兼容完成。真实运行、静态编译、mock、preview adapter 和完整支持必须明确区分。

## 每轮开发的最小记录检查

只记录本轮实际产生且未来有价值的内容；不要机械生成空模板。

### Command Trace

关键复现命令记录：working directory、shell、exact command、required environment variables、运行目的和 expected result。不得只写 `ran probe successfully`。

### File Change Trace

产品代码变更记录：file path、原职责、变更后职责、变更原因、新旧文件状态、删除的旧逻辑及 shared behavior 是否改变。关键架构变化应给出 `BEFORE` / `AFTER`，不要让未来只能从 Git diff 猜设计意图。

### Architecture Decision Trace

存在多个技术方案时记录 candidate、比较维度、chosen path、rejected path 及 rejection reason；不得只记录最终选择。

### Blocker Trace

按以下结构记录：

```text
Observed symptom
Expected behavior
Initial hypothesis
Evidence collected
Root cause
Fix
Validation after fix
```

必须区分 code、driver、runtime dependency、database server、Docker、Dify、plugin-daemon、installed plugin version、checksum、Provider schema、Tool、Workflow、missing environment 和 missing evidence；不得笼统写成 `environment issue`。

### Failed / Abandoned Path Trace

记录尝试原因、失败或放弃原因、恢复条件及最终路线更合适的依据。典型案例包括 pyodbc、system ODBC dependency、mock-only validation、fallback dialect、old checksum 和 manual-only gate。

### Reproduction Trace

真实 PASS 至少记录 prerequisites、command、input、expected output、artifact 和 failure meaning。只能在当前机器神秘成功的结果不构成良好复现证据。

### Final Tutorial Relevance

在合适的任务总结或报告中，将本轮记录分类为：

- `TUTORIAL_REQUIRED`：从零教程必须包含，如 adapter、requirements、wheel packaging、Dify installation、Provider configuration；
- `TUTORIAL_REFERENCE`：教程可能引用但不逐步展开；
- `DEVELOPMENT_HISTORY_ONLY`：只进入开发过程说明，如 driver 选型或 checksum incident；
- `EVIDENCE_ONLY`：只保留为验证证据，如 machine JSON artifact；
- `TEMPORARY`：最终不保留，如 probe site-packages、cache、transient logs。

## reports 与验证脚本

`reports/` 继续承担 development memory、machine evidence 和 human-readable phase record。保留历史报告和现有 Phase 编号，不为最终教程大规模重构。新报告在相关时应包含 development、command、decision、blocker 和 reproduction trace，避免只写 `PASS` 或 `implemented X`。

继续区分 product code、formal verification、optional gate、isolated probe 和 temporary diagnostic。不要因未来教程把所有 probe 变成正式脚本；教程只保留必要验证入口，Development Process Document 可以引用 isolated probe 的诊断价值。

## 数据库角色与当前边界

### SQL Server

当前状态：`SQLSERVER_OPTIONAL_GATE_READY_NOT_MAIN_MATRIX`。

SQL Server 是 Development Process Document 的 `Database Compatibility Pipeline Case Study`，重点保留 pymssql vs pyodbc、`FAIL_IMPORT`、`MISSING_ENV`、env-file loading、offline wheel closure、candidate checksum mismatch、old Provider schema、TOP syntax path evidence，以及 optional gate vs main matrix decision。

当前不要无意义重复 SQL Server 验证。它不改变最终核心数据库交付目标为 DM8 和 KingbaseES。

### DM8

DM8 是最终核心交付数据库。当前暂不执行 DM8 regression；后续涉及 DM8 时持续记录 dmPython、dmSQLAlchemy、adapter behavior、schema、Unicode、readonly、offline wheels、plugin runtime、Workflow 和 regression，最终形成 `DM8 Offline Plugin Package`。

### KingbaseES

KingbaseES 是最终核心交付数据库，当前存在真实外部依赖不确定性。后续严格区分 official installation media、trial license、bundled trial、external `license.dat`、driver、SQLAlchemy dialect、PostgreSQL compatibility assumption、real KingbaseES server、mock 和 preview adapter。

禁止把 `PostgreSQL-compatible` 等同于 `KingbaseES runtime PASS`，也禁止把 adapter static compile 写成 KingbaseES supported。最终目标是经过真实证据链验证的 `KingbaseES Offline Plugin Package`；若 official media、driver 或 license 阻塞，按事实记录 blocker。

## 当前开发策略

继续正常数据库兼容开发，不进入 final delivery closure。下一方向优先评估 KingbaseES official media、bundled trial 和 driver runtime feasibility；如受外部依赖阻塞，转向不依赖该 blocker 的工作。

每轮结束前回答：

1. 是否改变最终插件？
2. 是否属于开发过程历史？
3. 是否需要进入最终教程？
4. 未来是否能根据当前记录复现？

