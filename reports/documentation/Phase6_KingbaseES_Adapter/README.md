# Phase 6 KingbaseES Adapter

Phase 6 属于未来范围。

## 目标

在 DM 适配路径跑通后，再增加 KingbaseES 支持。

## 计划工作

- 确认驱动和 SQLAlchemy dialect 兼容性。
- 定义连接参数和查询行为。
- 用真实 KingbaseES 输出验证 SQL 安全和结果格式化。
- 只有在验证后才新增 Provider 字段。

## 依赖

Phase 6 应复用 Phase 4 建立的公共核心边界，并参考 Phase 5 的适配经验。
