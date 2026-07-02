# Phase 7 KingbaseES Adapter

Phase 7 尚未开始。

## 目标

在 DM 适配路径跑通后，再增加 KingbaseES 支持。

## 计划工作

- 确认驱动和 SQLAlchemy dialect 兼容性。
- 定义连接参数和查询行为。
- 用真实 KingbaseES 输出验证 SQL 安全和结果格式化。
- 只有在验证后才新增 Provider 字段。

## 依赖

KingbaseES 必须复用 `0.1.0` 建立的 Adapter 公共核心边界，并参考同阶段 DM8 的适配经验。
