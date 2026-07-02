# Phase 5.5: Workflow Automation Completion

状态：已完成（2026-06-29）

## 为什么补齐这一阶段

Phase 5 完成 Adapter 架构冻结后，Provider 和 Tool 已能自动回归，但 Workflow API 仍依赖人工验证。DM8、KingbaseES 或后续 Release 若只验证数据库层，无法覆盖 Dify Start 输入、Tool 节点、Provider 凭据、End 输出和公开 API 的完整链路。因此在国产数据库开发前补齐 Workflow 自动化，形成稳定的一键发布基线。

## 自动化结构

```text
verify_all.ps1
      │
      ▼
verify_provider.ps1
      │
      ▼
verify_tool.ps1
      │
      ▼
verify_workflow.ps1
      │
      ▼
summary.json
```

共享执行器为 `db_query_extended/verification/verification_runner.py`。PowerShell 脚本负责入口、环境检查、报告路径和失败传播，Python 负责数据库调用、Workflow HTTP 请求、JSON Schema 及 PASS/FAIL 判定。

## 覆盖范围

- Provider：MySQL/PostgreSQL 凭据归一化、连接及 Adapter 契约。
- Tool：双数据库 SELECT、LIMIT、COUNT、WHERE、JOIN、`max_rows` 截断、formatter 和 SQL 安全。
- Workflow API：SELECT 1、LIMIT 5、COUNT、WHERE、JOIN、截断。
- Workflow 安全：DROP、UPDATE、DELETE、ALTER、CREATE 必须被拒绝。
- 报告：Provider、Tool、Workflow 和总汇总分别保存。

## 最终结果

| Suite | PASS | FAIL | SKIP |
| --- | ---: | ---: | ---: |
| Provider | 4 | 0 | 0 |
| Tool | 20 | 0 | 0 |
| Workflow API | 11 | 0 | 0 |
| 合计 | 35 | 0 | 0 |

证据目录：[`../../verification/2026-06-29/`](../../verification/2026-06-29/README.md)

## 执行方式

```powershell
Set-Location E:\Dify_Plugin\db_query_extended
$env:DIFY_WORKFLOW_API_URL = "http://localhost/v1/workflows/run"
$env:DIFY_WORKFLOW_API_KEY = "<app key>"
.\verification\verify_all.ps1
```

Key 在 Dify Workflow 应用的“访问 API”页面创建，只进入当前进程环境，不写入脚本或报告。`verify_workflow.ps1` 缺少 URL/Key 时直接 FAIL，不允许 SKIP。

## 实施中解决的问题

- Dify 1.13.3 不接受 Provider credential schema 的 `number` 类型；`port` 与 `connection_timeout` 改为 `text-input`，运行时仍由 `validation.py` 转为整数。
- 插件重装会使 Workflow Tool 节点恢复默认参数；重新绑定 `Start.sql`、`Start.max_rows`，并将 Tool `json` 映射到 End `result` 后重新发布。
- 本地 unsigned 插件要求 plugin-daemon 使用 `FORCE_VERIFYING_SIGNATURE=false` 的开发 override。

本阶段未新增 DM8/KingbaseES 驱动或数据库类型，也未修改 Adapter 实现。
