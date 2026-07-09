# Workflow test: SELECT 1

真实执行时间：2026-06-23 09:22:09Z（daemon/API 日志）

- Workflow 节点：`只读 SQL 查询` / `db_query_extended`。
- 输入：`{"sql":"SELECT 1;"}`。
- UI 状态：`SUCCESS`，运行时间 `0.825s`。
- daemon：`POST .../dispatch/tool/invoke`，HTTP 200，`645ms`。
- API Tool 输出：

```json
{
  "type": "json",
  "message": {
    "json_object": {
      "columns": ["?column?"],
      "max_rows": 100,
      "row_count": 1,
      "rows": [{"?column?": 1}],
      "truncated": false
    },
    "suppress_output": false
  }
}
```

结论：真实 Workflow 路径、Provider 凭据、daemon 调度、PostgreSQL 连接及 JSON Tool 输出均通过。
