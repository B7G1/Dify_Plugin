# ADR-0001: Freeze MySQL/PostgreSQL Baseline Before Domestic Adapters

- Status: Accepted
- Date: 2026-06-29
- Decision owners: db_query_extended maintainers

## Context

MySQL/PostgreSQL 已完成 Adapter 重构和完整 Workflow API 自动化，结果为 35 PASS / 0 FAIL / 0 SKIP。下一阶段将引入 DM8、KingbaseES 等驱动、dialect 和会话差异。如果没有不可变 Release 基线，后续回归无法区分国产数据库适配问题与既有核心退化。

## Decision

1. 将当前版本标记为 `0.1.0`，作为首个稳定 MySQL/PostgreSQL 基线。
2. 冻结 Tool、Provider、JSON Schema、SQL 安全策略、Adapter 接口、`NullPool` 和 `engine.dispose()` 生命周期。
3. 以 `verify_all.ps1` 的 FAIL=0、SKIP=0 作为 Release 和后续 Adapter 合并门禁。
4. Release 目录保存插件包、SHA-256、验证 JSON 和文档快照，不覆盖更新。
5. Phase 7 国产数据库实现必须通过新增 Adapter 扩展；不得在 Tool 主逻辑或 `database.py` 恢复数据库类型分支。

## Consequences

### Positive

- 后续退化可以与 `0.1.0` 做明确比较。
- 每种新数据库共享同一端到端验收框架。
- Release 交付内容、证据和决策可独立审计。

### Trade-offs

- Provider 支持类型仍需在功能阶段显式开放，不是只新增文件即可完成全部产品配置。
- 当前包为本地 unsigned artifact，生产分发流程尚未冻结。
- 连接池、证书和生产高可用仍是未来 ADR 范围。
