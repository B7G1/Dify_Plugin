# Regression Attempt After DM8 Data Capability Closure

Date: 2026-07-06 America/Chicago

## Result

| Suite | Result |
|---|---:|
| Provider | 6 PASS / 0 FAIL / 0 SKIP |
| Tool | 27 PASS / 0 FAIL / 0 SKIP |
| Workflow | BLOCKED before execution |

`verify_all.ps1` was invoked after the DM8 evidence runner completed. It wrote:

- `provider_result.json`
- `tool_result.json`

It then stopped at `verify_workflow.ps1` because the current process did not contain:

- `DIFY_WORKFLOW_API_URL`
- `DIFY_WORKFLOW_API_KEY`

The workflow gate is intentionally fail-closed and does not skip or infer a pass.

Historical full regression remains available at `reports/verification/2026-07-01/summary.json`: 45 PASS / 0 FAIL / 0 SKIP.
