# Five-Minute Demo Script

## Opening

“这是 `db_query_extended` v1.0。它让 Dify Workflow 通过统一 Tool 安全读取 MySQL、PostgreSQL 和 DM8，并把数据库差异限制在 Adapter 层。”

Show the overall architecture. Point out the fixed chain: Workflow → read-only Tool → Adapter Registry → database → normalized JSON.

## Plugin

Open the Dify Plugin page in fullscreen.

“当前安装的是 0.1.1。Provider 管理连接配置，Tool 对所有数据库保持同一输入输出契约。”

Do not open the credential form. Show only installed/enabled status.

## Provider

Trigger credential validation using the already configured DM8 Provider, then close the form immediately after success.

“凭据验证是真实连接探测，但密码、主机和用户名不会进入日志或演示画面。”

## Workflow and query

Open the published three-node Workflow and run:

```sql
SELECT 1;
```

Show the Result tab.

“Start 节点接收 SQL，Tool 执行共享安全校验和 DM8 Adapter，Output 节点返回统一 JSON。这里数据库类型是 DM，返回一行，执行成功。”

## API

Use a prepared terminal whose key was already injected invisibly. Run the safe API smoke command or the Workflow-only verifier.

“同一条发布 Workflow 也通过 API 使用。Key 只存在于进程环境，演示结束立即清理。”

## Automated verification

Run or show the completed `verify_all.ps1` result:

“Provider 6 项、Tool 27 项、Workflow 12 项，总计 45 PASS，0 FAIL，0 SKIP。危险 SQL 拦截和 Unicode 都在真实验收范围内。”

## Dashboard and close

Open the v1.0 Dashboard.

“Dashboard 把发布资料、恢复基线、架构和机器证据串在一起。这个版本的价值不是只跑通一次，而是冷启动后身份和数据保持不变，并能用同一套回归继续开发。”

Close with the Phase 10 boundary: KingbaseES and other databases are future work, not v1.0 claims.
