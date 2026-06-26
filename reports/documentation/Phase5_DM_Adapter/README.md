# Phase 5 DM Adapter

Phase 5 尚未开始。

## 目标

在已经冻结的公共核心之上，新增 DM 数据库适配层。

## 计划工作

- 确认 Python 驱动与 SQLAlchemy dialect 方案。
- 定义 DM 连接 URI 和 connect_args。
- 验证 DM 下 SELECT / WITH 只读查询行为。
- 适配行为验证通过后，再考虑 Provider 表单字段。
- 新增 DM 专用验证数据、脚本和证据归档。

## 依赖

Phase 5 应复用 Phase 4 的核心边界，不应重写 Tool 编排、通用结果格式化或共享只读校验，除非出现经过验证的 DM 特有差异。
