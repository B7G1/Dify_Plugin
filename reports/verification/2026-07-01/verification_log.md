# 最终验收日志（脱敏）

1. 首次运行：Provider 4 PASS / 2 FAIL；旧端口 3307/5433 与实际 3306/5432 不符。
2. 修正端口后：Provider 6/0/0，Tool 27/0/0，Workflow 0/11/0；localhost:80 未监听。
3. 使用唯一入口 `start_dify.ps1` 恢复 `api/nginx/ssrf_proxy`，preflight 通过。
4. 首次全绿运行使用了 runner 默认目标标签 `mysql`，Workflow 为 11/0/0，但未覆盖 DM8 专属 Unicode 用例，未作为最终证据。
5. 明确设置 Workflow 类型为 `dm` 后最终运行：Provider 6/0/0，Tool 27/0/0，Workflow 12/0/0；总计 45/0/0。

日志不包含密码、认证 Cookie 或 Workflow API Key。
