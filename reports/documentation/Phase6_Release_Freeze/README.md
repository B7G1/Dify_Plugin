# Phase 6: Release Freeze 与交付资料整理

状态：已完成（2026-06-29）

## 目标

基于 Phase 5.5 的 35 PASS / 0 FAIL / 0 SKIP，将 MySQL/PostgreSQL 稳定实现冻结为 `db_query_extended 0.1.0`，建立可安装、可校验、可追溯、可复验的 Release 基线。

## 冻结内容

- manifest/meta 版本：`0.1.0`。
- Adapter 契约、数据库生命周期和错误映射。
- Tool/Provider 调用方式与 JSON Schema。
- SQL 只读策略。
- `verify_all.ps1` 质量门禁：FAIL=0、SKIP=0。

## 交付资料

- Release README 与安装/校验步骤。
- 根级 CHANGELOG。
- 版本 Release Notes。
- ADR-0001 冻结决策。
- `.difypkg` 安装包及 SHA-256。
- Provider/Tool/Workflow/Summary 四份验证证据快照。

入口：[`../../../release/db_query_extended/0.1.0/`](../../../release/db_query_extended/0.1.0/README.md)

## 后续阶段约束

Phase 7 DM8/KingbaseES 适配从 `0.1.0` 基线扩展。任何新 Adapter 合并前必须重新执行完整门禁，并证明 MySQL/PostgreSQL 无回归。
