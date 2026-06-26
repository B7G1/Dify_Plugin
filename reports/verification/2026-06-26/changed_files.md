# 2026-06-26 Changed Files

## Plugin Code

### `db_query_extended/utils/database.py`

- Split connection creation into URL, connect-args, and engine-options helpers.
- Preserved MySQL/PostgreSQL behavior and short-lived `NullPool`.
- Moved result row normalization out to `utils/formatter.py`.
- Kept explicit `engine.dispose()` cleanup.
- Documented that `pool_timeout`, `pool_recycle`, real pooling, and automatic reconnect are not implemented.

### `db_query_extended/utils/formatter.py`

- New formatter module for the stable Tool JSON result contract.
- Handles common DB value types and fallback object conversion.
- Centralizes truncation behavior.

### `db_query_extended/utils/sql_validator.py`

- Tightened public SQL contract to `SELECT` and `WITH`.
- Added transaction-control and permission statements to blocked coverage.
- Kept SQL-aware lexical handling for comments, strings, quoted identifiers, and dollar-quoted strings.

### `db_query_extended/tools/db_query_extended.yaml`

- Updated Tool description from `SELECT/WITH/EXPLAIN` to `SELECT/WITH`.
- No provider credential fields changed.

### `db_query_extended/verification/phase2_matrix.py`

- Added formatter coverage.
- Added blocked SQL cases for `REPLACE`, `GRANT`, `REVOKE`, `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`, `SET`, `USE`, `EXPLAIN`, and comment/semicolon bypasses.

## Reports And Indexes

### `reports/verification/2026-06-26/*`

- Added daily archive and verification evidence.

### `reports/html_reports/2026-06-24/project_dashboard.html`

- Adds 2026-06-26 timeline data for Plugin Core Freeze.

### `reports/html_reports/2026-06-24/assets/dashboard.js`

- Reads multiple `cockpit-update-*` JSON scripts so daily updates can be appended without replacing history.

### `reports/html_reports/2026-06-24/data/cockpit-data.json`

- Adds 2026-06-26 summary data.

### `README.md` and `INDEX.md`

- Updated workspace entry points for the 2026-06-26 Plugin Core Freeze archive.
