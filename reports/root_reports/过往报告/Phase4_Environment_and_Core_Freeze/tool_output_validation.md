# Tool output validation

已验证的真实输出来自 Workflow `SELECT 1`：

- 类型：Dify plugin `json` message；
- 结构：`columns`、`max_rows`、`row_count`、`rows`、`truncated`；
- 数据：`row_count=1`，`rows=[{"?column?":1}]`；
- API 将其记录为 `on_tool_execution`，无 Runtime Error；
- 该 JSON 结构可作为后续 Workflow 节点的结构化 Tool 输出消费。

`plugin_test_users` 的 Workflow 输出未能取得，因为该次节点输入是 `null` 并失败；因此不能宣称多行结果格式已完成验收。
