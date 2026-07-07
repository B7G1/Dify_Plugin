# Phase 7 DM8 Adapter

状态：**PASS（Phase 7.1，2026-06-30）**。

最终验收报告：[`../../Phase7_1_DM8_Adapter/README.md`](../../Phase7_1_DM8_Adapter/README.md)。

## 目标

在已经冻结的公共核心之上，新增 DM 数据库适配层。

## 已完成工作

- 确认 Python 驱动与 SQLAlchemy dialect 方案。
- 定义 DM 连接 URI 和 connect_args。
- 验证 DM 下 SELECT / WITH 只读查询行为。
- 完成 DM Provider 表单、只读凭据与运行时配置。
- 新增 DM 专用验证数据、脚本和证据归档。
- 完成 Workflow API `12 PASS / 0 FAIL / 0 SKIP`。

验收范围现按导师反馈分层：Environment & Compatibility 为 **PASS**；Data Capability 为 **PARTIAL PASS**。现有证据已证明真实表数据的 WHERE、JOIN、LIMIT、多行、截断、Unicode 和参数绑定链路，但尚未形成全部 14 项的字段级证据闭环。详见 [`../../Phase7_1_DM8_Adapter/data_retrieval_validation.md`](../../Phase7_1_DM8_Adapter/data_retrieval_validation.md)。

## 依赖

DM8 必须复用 `0.1.0` 已冻结的 Adapter 边界，不应重写 Tool 编排、通用结果格式化或共享只读校验，除非出现经过验证的 DM8 特有差异。
