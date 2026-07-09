# Workflow test: plugin_test_users

真实执行时间：2026-06-23 09:24:35Z。

计划 SQL：

```sql
SELECT * FROM plugin_test_users LIMIT 5;
```

结果：`FAIL`，UI 运行时间 `0.267s`。

UI 错误：

```text
ValueError: SQL execution failed. Check SQL syntax and referenced database objects.
```

API 日志证据：节点输入被记录为 `null`；随后 daemon 收到 `dispatch/tool/invoke` HTTP 200，但 API 流处理记录 `PluginInvokeError`。因此本次失败不能证明表不存在、权限错误或连接失败；已知直接 psql 查询该表成功。

受控重试未执行：浏览器自动化安全策略阻止继续向 `http://localhost` 填写/运行，未使用任何绕过方式。
