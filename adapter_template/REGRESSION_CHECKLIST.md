# New Adapter Regression Checklist

- [ ] Database version and driver/license are documented.
- [ ] Provider accepts valid credentials and rejects invalid/missing values safely.
- [ ] Passwords and connection URLs never appear in logs or reports.
- [ ] Shared read-only validation remains unchanged or is strengthened for all adapters.
- [ ] Scalar, Unicode, timestamp, decimal, binary, null, and vendor-specific types serialize correctly.
- [ ] `max_rows`, truncation, timeout, cleanup, and error mapping are verified.
- [ ] DML, DDL, multi-statement, obfuscated, and vendor-dangerous SQL are rejected.
- [ ] Published Workflow and real API return the stable JSON contract.
- [ ] Existing MySQL, PostgreSQL, and DM8 suites retain zero FAIL/SKIP.
- [ ] `TEST_MATRIX.md`, compatibility, limitations, release notes, and Dashboard are updated.
- [ ] Clean package install and checksum are recorded.
