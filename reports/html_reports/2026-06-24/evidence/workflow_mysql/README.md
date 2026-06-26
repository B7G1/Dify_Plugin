# MySQL Workflow Evidence

Status: PASS

Workflow:

```text
Start / User Input
→ Read-only SQL Query
→ Output
```

SQL:

```sql
SELECT * FROM plugin_test_users LIMIT 5;
```

Primary archive: `reports/verification/2026-06-25/workflow_mysql_result.json`.
