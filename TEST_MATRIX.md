# Database Acceptance Matrix

Status values: `PASS` means accepted evidence exists; `PLANNED` means no support claim.

| Database | Provider | Workflow | API | Unicode | Security | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MySQL 8.4 | PASS | PASS | PASS | PASS | PASS | PASS — v1.0 supported baseline |
| PostgreSQL 16 | PASS | PASS | PASS | PASS | PASS | PASS — v1.0 supported baseline |
| DM8 | PASS | PASS | PASS | PASS | PASS | PASS — real 2026-07-01 acceptance |
| KingbaseES | PLANNED | PLANNED | PLANNED | PLANNED | PLANNED | Phase 10 candidate |
| Oracle | PLANNED | PLANNED | PLANNED | PLANNED | PLANNED | roadmap |
| SQL Server | PLANNED | PLANNED | PLANNED | PLANNED | PLANNED | roadmap |
| SQLite | PLANNED | PLANNED | PLANNED | PLANNED | PLANNED | roadmap |

## Minimum acceptance for a new row

- Provider: valid and invalid credentials, missing fields, network/driver error mapping.
- Workflow: scalar query, multi-row query, truncation, timestamp/numeric/vendor types.
- API: published Workflow, HTTP success/error contract, stable JSON schema.
- Unicode: input, identifier where supported, text result, JSON round-trip.
- Security: read-only allowlist plus DML, DDL, multi-statement, comments/obfuscation, and vendor-specific dangerous constructs.
- Regression: all previous PASS rows remain PASS; release allows no unexplained SKIP.

Machine evidence belongs in a dated `reports/verification/` directory. This matrix is an index, not a substitute for JSON results.
