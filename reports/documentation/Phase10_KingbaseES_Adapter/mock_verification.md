# KingbaseES Mock Verification

Date: 2026-07-02  
Evidence level: **MOCK_ONLY**

## Result

```text
11 MOCK_PASS
0 FAIL
1 BLOCKED
```

The blocked entry is the real `ksycopg2` + Kingbase SQLAlchemy dialect runtime. It is intentionally BLOCKED and is not counted as a mock failure or a real PASS.

## Covered offline contracts

1. KingbaseES credential normalization and default port 54321;
2. dynamic Adapter discovery;
3. `kingbase+ksycopg2` URL and password redaction;
4. connection timeout and SSL arguments;
5. engine options after a mocked runtime gate;
6. parameterized statement timeout;
7. parameterized schema/search_path;
8. empty-schema behavior;
9. existing MySQL/PostgreSQL/DM8 URL drivers and default ports unchanged;
10. unchanged shared SQL Security representative cases;
11. Provider Preview/schema declaration.

## Not covered

- driver import or native `.so` loading;
- real database connection;
- actual KingbaseES timeout/search_path behavior;
- Provider Credential Validation in Dify;
- Workflow UI, published Workflow, or Workflow API;
- package installation;
- full 45-check regression.

Evidence: `reports/verification/2026-07-02/phase10_kingbasees/mock_result.json`.

