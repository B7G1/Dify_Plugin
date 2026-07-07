# Encoding Path Audit

## Adapter / driver status

| Database | Driver | Unicode handling | User charset required? | Notes |
| --- | --- | --- | --- | --- |
| MySQL | `mysql+pymysql` / PyMySQL | PyMySQL returns Python `str`; fixture table uses `utf8mb4`. | No for current gate. | `charset` is optional in credentials. If supplied, adapter passes it to PyMySQL `connect_args`. |
| PostgreSQL | `postgresql+psycopg2` | psycopg2 returns Python `str`; PostgreSQL client/server encoding handles Unicode. | No. | Adapter passes `sslmode` and optional `search_path`, not `client_encoding`. |
| DM8 | `dmPython` + `dmSQLAlchemy` | Adapter sets `local_code=1` in connect args; stored multilingual data passed exact equality. | No frontend field required. | Machine evidence: `reports/verification/2026-07-07/multilingual_dm_result.json`. |
| SQL Server | Not product-supported yet | N/A | N/A | Local environment gate exists only. |
| KingbaseES | BLOCKED | N/A | N/A | License/driver/runtime gate not closed. |

## Code findings

- `build_database_url` delegates to `utils.adapters.*`.
- `build_connect_args` delegates to each adapter.
- MySQL adapter only passes `charset` if configured; no hardcoded forced charset.
- PostgreSQL adapter does not hardcode `client_encoding`.
- DM8 adapter hardcodes `local_code=1`.
- Formatter preserves Python `str` as-is.
- Formatter only decodes `bytes`/`bytearray` as UTF-8 with replacement; normal text DB columns are not manually decoded.
- Verification/report writers use `json.dumps(..., ensure_ascii=False)` where machine evidence is generated.
- Workflow API payload is encoded as UTF-8 and response decoded as UTF-8.

## Boundary distinction

| Layer | Current assessment |
| --- | --- |
| Terminal display encoding | Can corrupt console/log display only; not proof of plugin data corruption. |
| SQL file encoding | Fixture files must be UTF-8; DM8 import is now proven by exact stored-data retrieval after local administrator setup. |
| Database storage encoding | Verified by stored-table retrieval for MySQL, PostgreSQL, and DM8. |
| Driver/client encoding | MySQL, PostgreSQL, and DM8 passed exact stored-data retrieval. |
| Python Unicode string | Formatter preserves `str` values directly. |
| JSON serialization | Evidence uses `ensure_ascii=False`; Dify tool JSON preserves Unicode strings. |
| Browser rendering | DM8 machine gate is PASS; frontend screenshot file set is complete and project-owner manual visual review is PASS. Independent machine-vision verification was not performed. |

## DM8 administrator boundary

The DM8 fixture setup required an interactive local administrator action:

```sql
GRANT CREATE TABLE TO "PLUGIN_TEST_OWNER";
```

This was performed using `DIFY_TEST` through `C:\dmdbms\bin\disql.exe`. The administrator password is not recorded. `DIFY_TEST` is not used by the adapter, provider, tool, or workflow path; normal plugin execution remains under `PLUGIN_TEST_USER`.

## Conclusion

No plugin-side `.encode()` / `.decode()` repair path is used for normal text values. The Phase 7.2 multilingual stored-data gate is PASS for all currently supported and executable adapters: MySQL, PostgreSQL, and DM8.
