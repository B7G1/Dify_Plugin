# DM8 Data Capability Evidence Closure

状态：**COMPLETE — 14 项数据能力均已有完整 JSON evidence**  
执行日期：2026-07-06（America/Chicago）  
证据文件：[`../../verification/2026-07-06/dm8_data_capability_closure/evidence.json`](../../verification/2026-07-06/dm8_data_capability_closure/evidence.json)  
SHA-256：`2A2D07BFAC12065230C0680C1B5EF87DFCE59D53598B1967A4F8CE3443D463D3`

## Regression Result

本次没有修改 Provider / Tool / Adapter 核心逻辑，只新增 verification/evidence runner。

| Suite | 本次结果 | Evidence |
|---|---:|---|
| Provider | 6 PASS / 0 FAIL / 0 SKIP | `../../verification/2026-07-06/regression_after_dm8_data_capability/provider_result.json` |
| Tool | 27 PASS / 0 FAIL / 0 SKIP | `../../verification/2026-07-06/regression_after_dm8_data_capability/tool_result.json` |
| Workflow | 未完成 | 当前 Codex 进程缺少 `DIFY_WORKFLOW_API_URL` 和 `DIFY_WORKFLOW_API_KEY`，`verify_all.ps1` 在 Workflow gate 停止 |

历史完整回归口径仍保留为：[`../../verification/2026-07-01/summary.json`](../../verification/2026-07-01/summary.json)，45 PASS / 0 FAIL / 0 SKIP。  
本次 regression 只能声明 Provider + Tool 无回归；不能伪造当前进程的 Workflow PASS。

## DM8 Data Capability Result

| # | Capability | 状态 | 独立复核点 |
|---:|---|---|---|
| 1 | SELECT * 字段值 | PASS | `columns` 完整；前 5 行字段值保存；第 5 行 `EMAIL=null`, `SALARY=null` |
| 2 | WHERE 过滤 | PASS | `STATUS='completed'` 返回 14 行，所有行状态均为 completed |
| 3 | ORDER BY / max_rows 前三行 ID | PASS | `rows[0..2].ID = [1, 2, 3]`, `truncated=true`, `max_rows=3` |
| 4 | LIMIT | PASS | LIMIT 5 返回 5 行，未截断 |
| 5 | COUNT(*) 实际值 | PASS | `USER_COUNT=12` |
| 6 | GROUP BY 分组平均值 | PASS | Engineering `19237.5`, Product `16000.25`, Support `12800` |
| 7 | JOIN | PASS | 用户名、产品名、金额均保存，返回 10 行 |
| 8 | 中文字符 | PASS | `UNICODE_TEXT="中文测试"` |
| 9 | NULL 到 JSON null | PASS | `EMAIL` / `SALARY` 的 Python `None` 归档为 JSON `null` |
| 10 | JSON 类型/文本 JSON 序列化 | PASS | `JSON_TEXT` 可解析为 `{"source":"dm8","ok":true,"count":12}` |
| 11 | CLOB/TEXT 读取 | PASS | `EVENT_MESSAGE="Workflow integration smoke test."` |
| 12 | 参数安全 Unicode 等价查询 | PASS | Unicode 字段值精确保留 |
| 13 | 多行数组结构 | PASS | `rows` 为对象数组，返回 10 行 |
| 14 | 空结果 | PASS | `rows=[]`, `row_count=0`, `truncated=false` |

统计：14 PASS / 0 PARTIAL / 0 NOT EVIDENCED / 0 FAIL。

## Evidence Contract

每个 capability artifact 均包含：

- `capability_id`
- `capability_name`
- `sql`
- `execution_layer`
- `workflow_run_id`
- `columns`
- `rows`
- `row_count`
- `truncated`
- `max_rows`
- `assertion`
- `generated_at`

`execution_layer` 当前为 `tool_json`；`workflow_run_id` 对本专项不适用，保留为 `null`。

## Closure Decision

DM8 Data Retrieval Validation 可以从 **PARTIAL PASS** 升级为 **COMPLETE**，范围限定为：DM8 14 项数据能力的完整 JSON evidence closure。

发布/回归口径仍需区分：历史 45 PASS 完整回归仍有效；本次当前进程重跑完整 regression 时，Workflow 因缺少 API 环境变量未完成。
