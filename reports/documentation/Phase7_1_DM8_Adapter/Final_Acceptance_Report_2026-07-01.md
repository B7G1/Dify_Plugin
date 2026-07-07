# Final Acceptance Report — 2026-07-01

## Decision

| Area | Result | Evidence |
| --- | --- | --- |
| Environment | PASS | Fixed `dify` Compose project restarted through `start_dify.ps1` |
| Persistence | PASS | PostgreSQL system identifier remained `7657369583221227555`; named volumes unchanged |
| Workflow | PASS | Fresh `SELECT 1`, Unicode, and timestamp runs succeeded after cold boot |
| API | PASS | All three Workflow API calls returned HTTP 200 with correct JSON |
| Plugin | PASS | `db_query_extended` 0.1.1 persisted; runtime and tool endpoints were available |
| Cold Boot | PASS | Entire Dify stack was stopped, zero project containers remained, then the stack recovered healthy |
| Verification | PASS | `45 PASS / 0 FAIL / 0 SKIP` |
| Dify UI screenshot evidence | PASS | Current v1.0 screenshots received final manual owner approval for public display |
| Environment & Compatibility | PASS | Dify services, DM8 driver/ORM, Provider, Plugin, Workflow and API operated together |
| DM8 Data Capability | PARTIAL PASS | Real table reads, WHERE, JOIN, LIMIT, multi-row, truncation and Unicode passed; full 14-case value-level evidence is incomplete |

## Cold-boot facts

- Startup used only `E:\Dify_Plugin\db_query_extended\verification\start_dify.ps1`.
- PostgreSQL databases `dify` and `dify_plugin` remained present.
- PostgreSQL uses `dify_postgres_data_v1`; Weaviate uses `dify_weaviate_data_v1`.
- `plugin_daemon` remained running with restart count 0.
- Plugin installation `li_zijun/db_query_extended` version `0.1.1` and Workflow `ec11fbde-d77c-4818-bcdf-b2b483dffe3d` remained in the Console database.

## Fresh functional verification

After the cold boot, the published Workflow was invoked through the real Workflow API:

| SQL | HTTP | Workflow | Result |
| --- | ---: | --- | --- |
| `SELECT 1;` | 200 | SUCCESS | one DM8 row, JSON value `1` |
| `SELECT '中文测试';` | 200 | SUCCESS | Unicode preserved in JSON |
| `SELECT CURRENT_TIMESTAMP;` | 200 | SUCCESS | one timestamp row in JSON |

The Provider record `DM8 Local Readonly` persisted. Successful post-boot Workflow execution through the provider is runtime evidence that the stored credential remains usable. Secrets were transient and are not recorded here.

These three cold-boot checks prove post-restart connectivity and scalar value transport. They are not, by themselves, evidence for table filtering, relational joins, NULL, CLOB, grouping or empty-result behavior.

## DM8 data retrieval evidence

The broader Workflow suite did execute real DM8 table queries:

| Capability | Evidence | Decision |
|---|---|---|
| WHERE | completed-order query returned the deterministic 14 rows | PASS |
| JOIN | users/orders join returned 10 rows | PASS |
| LIMIT | user query returned 5 rows | PASS |
| Multi-row/truncation | ordered user query returned 3 rows and `truncated=true` | PASS |
| Unicode | returned JSON value was asserted equal to `中文测试` | PASS |
| Parameter binding | dmPython/SQLAlchemy/Tool JSON preserved the bound Unicode value | PASS |

Most archived Workflow entries contain only row-count excerpts rather than complete desensitized `columns/rows` payloads. GROUP BY, NULL-to-JSON, DM8 JSON type, CLOB and empty-result cases lack final Workflow/API/UI artifacts. Therefore the original automated acceptance remains PASS, while the dedicated data-capability decision is **PARTIAL PASS**. See [`data_retrieval_validation.md`](data_retrieval_validation.md).

## Automated acceptance

The real `verify_all.ps1` execution completed successfully:

- Provider: 6 PASS / 0 FAIL / 0 SKIP
- Tool: 27 PASS / 0 FAIL / 0 SKIP
- Workflow: 12 PASS / 0 FAIL / 0 SKIP
- Total: **45 PASS / 0 FAIL / 0 SKIP**

Machine-readable evidence is in `reports/verification/2026-07-01/final_cold_boot/`.

## Screenshot evidence closure

The initial automated browser capture path was unavailable, but the required current v1.0 screenshots were later supplied and manually reviewed. The owner confirmed that they truthfully represent the baseline and contain no disqualifying sensitive disclosure or obstruction. Screenshot Review is PASS.

## Final status

```text
Environment Ready
YES
```

Technical compatibility acceptance, screenshot review, and formal baseline sealing are complete. Public Release is READY under the original v1.0 scope. A separate value-level DM8 data-capability evidence pass is still required before claiming complete coverage of all 14 retrieval scenarios.
