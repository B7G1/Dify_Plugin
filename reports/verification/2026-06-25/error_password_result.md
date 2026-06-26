# Wrong Password Error Path Verification — 2026-06-25

Status: PASS

## Scenario

The PostgreSQL credential password was intentionally changed to an incorrect value to trigger credential validation failure.

## Observed UI error

```text
PluginInvokeError:
ToolProviderCredentialValidationError:
Failed to connect to the database.
Check database type, host, port, database name, and credentials.
```

## Conclusion

- The plugin detects connection failure.
- The failure is wrapped as a readable user-facing message.
- Python traceback was not exposed to the Dify UI user.
