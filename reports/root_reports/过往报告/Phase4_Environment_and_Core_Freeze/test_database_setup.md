# Test database setup validation

本轮未创建或修改测试表，因为它已存在。

真实容器命令结果：

```sql
SELECT 1 AS connectivity;
-- connectivity = 1

SELECT * FROM plugin_test_users LIMIT 5;
-- 1 alice alice@example.test
-- 2 bob   bob@example.test
-- 3 carol carol@example.test
-- 4 dave  dave@example.test
-- 5 eve   eve@example.test
```

结论：PostgreSQL 连接、表、数据和查询权限均正常。
