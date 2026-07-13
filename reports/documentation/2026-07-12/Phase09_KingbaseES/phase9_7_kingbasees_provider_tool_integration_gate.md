# Phase 9.7 — KingbaseES Provider and Tool Integration Gate

- Date: 2026-07-12
- Phase: Phase 9.7
- Status: PASS
- Database: KingbaseES
- Scope: Provider credential schema/lifecycle, real Provider validation, formal Tool invocation, read-only identity, output contract, and targeted regression
- Source commit: `842fdca`
- Runtime: `dify-plugin_daemon-1`, Python 3.12.3, SQLAlchemy 2.0.51, ksycopg2 2.9.1, KingbaseES V009R001C010
- Canonical path: `reports/documentation/2026-07-12/Phase09_KingbaseES/phase9_7_kingbasees_provider_tool_integration_gate.md`
- Machine evidence: `reports/verification/2026-07-12/kingbasees_phase9_7_*.json`
- Logs: `reports/logs/2026-07-12/Phase09_KingbaseES/kingbasees_phase9_7_*.log` and `phase9_7_runtime_loading.log`
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / REDACTED

## Decision

`PASS`

The verified conclusions are limited to `KINGBASEES_PROVIDER_PASS` and `KINGBASEES_TOOL_PASS`. Workflow, installed plugin, offline dependency closure, `.difypkg`, and final delivery remain not tested.

## Baseline and Scope Protection

- branch: `feature/kingbasees-adapter`;
- Phase 9.6 implementation: `bff16f4`;
- Phase 9.6 metadata correction: `6193358`;
- Phase 9.7 implementation baseline after that correction: `6193358`;
- Phase 9.7 source commit: `842fdca`;
- 43 pre-existing modified/untracked status entries were captured before work and treated as protected user work;
- preserved containers and volume were not deleted, rebuilt, or pruned.

## Existing Architecture Audit

The Provider YAML already contained a preview `kingbasees` option. `SUPPORTED_DATABASE_TYPES` and dynamic `get_database_adapter()` lookup also already recognized `kingbasees`. Provider validation called the common connection utility, and Tool execution already followed:

```text
Tool runtime credentials
-> validate_connection_config
-> common ReadOnlyValidator
-> execute_read_only_query
-> dynamic KingbaseESAdapter lookup
-> kingbasees.ksycopg2
-> ksycopg2
-> common formatter
-> success_response
```

Therefore no KingbaseES branch was added to Tool code and no central Adapter registry was changed.

SQL Server remains the existing optional compatibility path. Its Provider option was preserved in its original position and was not promoted into the MySQL/PostgreSQL/DM8 core matrix.

## Minimal Product Changes

### Provider schema

- retained the canonical value `kingbasees`;
- changed the visible label from `KingbaseES (Preview)` to `KingbaseES`;
- reused host, port, database, username, password, schema, connection timeout, and SSL mode fields;
- kept schema optional;
- retained the shared timeout and SSL UI instead of creating KingbaseES-only fields;
- required KingbaseES port explicitly at runtime.

The previous `54321` default came from the local Docker published-port mapping, not an established product default. It was removed from `DEFAULT_PORTS`; Provider help now labels it only as the local test mapping.

`ssl_mode` remains the Provider field and is converted by `KingbaseESAdapter` to the ksycopg2 `sslmode` connect argument, as verified in Phase 9.6.

### Provider lifecycle root fix

Observed symptom: Provider validation created a real Engine and executed `SELECT 1`, but did not call Adapter session/schema configuration.

Expected behavior: Provider validation must exercise the same schema/session boundary as Tool execution.

Root cause: `verify_database_connection()` omitted `adapter.configure_session()`.

Fix: the common verification function now opens a transaction, configures the selected Adapter session, executes `SELECT 1`, closes the connection, and disposes the Engine in the existing `finally` block.

KingbaseES `set_config(search_path)` accepts an unknown schema without necessarily failing. The KingbaseES Adapter therefore checks `information_schema.schemata` before setting a non-empty schema. This is scoped to KingbaseES and did not change PostgreSQL Adapter behavior.

### Tool

No Tool execution branch was required. Only stale MySQL/PostgreSQL-only description text was generalized. All KingbaseES behavior continues to reside in validation, Adapter, and dialect layers.

## Repeatable Read-only Fixture

The dedicated gate performs idempotent initialization in the preserved `kingbase` database:

- schema: `phase97_fixture`;
- table: `phase97_fixture.sample_data`;
- role: `phase97_readonly`;
- 12 deterministic rows covering integer, text, Chinese Unicode, NULL, NUMERIC, DATE, and TIMESTAMP;
- role grants: schema USAGE and table SELECT only;
- schema CREATE is explicitly revoked from the role and PUBLIC;
- the role password is generated per run, passed only through environment variables, and never written to Git or evidence.

The gate uses the administrative identity only for fixture preparation. Provider and Tool acceptance use `phase97_readonly`.

## Provider Verification

All 17 cases passed:

- valid fixture schema, `public`, and empty schema;
- explicit port and connection timeout;
- real special-character password lifecycle;
- missing host, port, database, username, and password;
- invalid port;
- wrong password;
- nonexistent user;
- unreachable endpoint;
- nonexistent database;
- nonexistent schema;
- unsupported `kingbase` database type.

The formal `DbQueryExtendedProvider._validate_credentials()` was invoked in the real plugin-daemon runtime. Its path was the common database utility, formal KingbaseES Adapter, plugin-owned dialect, ksycopg2, and real KingbaseES server. Provider Engine disposal was observed 10 times across real connection attempts.

Public failures contained neither submitted passwords nor credentialed URLs. Wrong credentials and unreachable endpoints retained a controlled connection diagnostic; invalid schema returned the existing generic safe validation message.

## Tool Verification

The formal `DbQueryExtendedTool._invoke()` was instantiated with a real Dify SDK `ToolRuntime` and executed in `dify-plugin_daemon-1`. All 13 Tool cases passed:

- `SELECT 1` returned `probe=1`;
- the real fixture returned 12 ordered rows;
- the stored Chinese value was read from the fixture, not from a SQL literal;
- NULL remained null;
- NUMERIC `2.50` serialized as `"2.50"`;
- DATE and TIMESTAMP serialized as stable strings;
- schema-qualified fixture read returned count 12;
- default `max_rows=100` was preserved;
- `max_rows=5` returned five rows with `truncated=true`;
- empty result, alias, aggregate (`84.00`), and ORDER BY content were verified;
- bad authentication and unreachable endpoint returned redacted Tool JSON errors.

Every successful response retained the formal keys:

```text
success
database_type
execution_time_ms
columns
rows
row_count
truncated
max_rows
generated_at
warning
error
```

`database_type` was `kingbasees`. Tool Engine disposal was observed after successes and failures.

## Read-only Security

The unchanged common SQL validator rejected all tested INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, TRUNCATE, multi-statement, comment-based bypass, write CTE, and CALL attempts before execution.

Defense in depth was separately proven at the database layer:

- direct INSERT as `phase97_readonly` failed with `InsufficientPrivilege`;
- direct CREATE TABLE in `phase97_fixture` failed with insufficient privilege.

Database permission failure is supplementary evidence and does not replace the common validator.

## Targeted Regression

All five targeted regression cases passed:

- Provider options remained exactly MySQL, PostgreSQL, DM8, SQL Server, KingbaseES;
- real PostgreSQL Provider validation passed against `dify-db_postgres-1`;
- formal PostgreSQL Tool `SELECT 1` returned `probe=1`;
- common validator allowed SELECT and rejected DML;
- common formatter retained its existing five-key base result contract.

Workflow regression was intentionally not run because Workflow is outside Phase 9.7.

## Runtime Dependency Boundary

The gate used:

```text
PYTHONPATH=/tmp/kingbasees_phase95/site:/tmp/kingbasees_phase97/plugin
```

The first directory supplies the previously verified candidate ksycopg2 2.9.1 and SQLAlchemy 2.0.51 runtime overlay. The driver SHA-256 remains:

`59D2D19439FA0D8AE66A7972EF9EF1FE461E84389D50BC3E90C59ABB4962287A`

This is `CANDIDATE_RUNTIME_DEPENDENCY_OVERLAY`, not `INSTALLED_PLUGIN_DEPENDENCY_CLOSURE`. No wheel, requirements, manifest, release directory, or `.difypkg` was changed.

## Commands Executed

Working directory: `E:\Dify_Plugin`; shell: PowerShell.

```powershell
git status --short
git log -15 --oneline
git branch --show-current
docker ps -a
docker inspect dify-plugin-phase94-kingbase
docker inspect dify-plugin_daemon-1

docker cp db_query_extended/utils dify-plugin_daemon-1:/tmp/kingbasees_phase97/plugin/
docker cp db_query_extended/provider dify-plugin_daemon-1:/tmp/kingbasees_phase97/plugin/
docker cp db_query_extended/tools dify-plugin_daemon-1:/tmp/kingbasees_phase97/plugin/
docker cp db_query_extended/verification/kingbasees_phase9_7_gate.py `
  dify-plugin_daemon-1:/tmp/kingbasees_phase97/plugin/verification/kingbasees_phase9_7_gate.py

docker exec --env PYTHONPATH=/tmp/kingbasees_phase95/site:/tmp/kingbasees_phase97/plugin `
  --env KINGBASE_HOST=host.docker.internal --env KINGBASE_PORT=54321 `
  --env KINGBASE_DATABASE=kingbase --env KINGBASE_USERNAME=<runtime-admin> `
  --env KINGBASE_PASSWORD=<runtime-secret> --env KINGBASE_READONLY_PASSWORD=<ephemeral-secret> `
  --env POSTGRES_HOST=dify-db_postgres-1 --env POSTGRES_PORT=5432 `
  --env POSTGRES_DATABASE=<runtime-db> --env POSTGRES_USERNAME=<runtime-user> `
  --env POSTGRES_PASSWORD=<runtime-secret> dify-plugin_daemon-1 `
  /usr/bin/python3 /tmp/kingbasees_phase97/plugin/verification/kingbasees_phase9_7_gate.py `
  --output-dir /tmp/kingbasees_phase97/output `
  --log-dir /tmp/kingbasees_phase97/logs
```

Expected result: all four generated JSON suites report `PASS`. Environment values shown as placeholders were passed transiently and not logged.

## Files Changed

Product:

- `db_query_extended/provider/db_query_extended.yaml`;
- `db_query_extended/tools/db_query_extended.yaml`;
- `db_query_extended/tools/db_query_extended.py` documentation only;
- `db_query_extended/utils/validation.py`;
- `db_query_extended/utils/database.py`;
- `db_query_extended/utils/adapters/kingbasees.py` minimal schema-existence fix.

Verification and reporting:

- `db_query_extended/verification/kingbasees_phase9_7_gate.py`;
- this canonical report;
- four machine evidence JSON files;
- four redacted suite logs plus one runtime-loading log;
- one Phase 9.7 REPORT_MAP entry.

## Decisions and Rejected Paths

- Chosen `kingbasees` because it is the existing Adapter module and canonical Provider value.
- Reused every public credential field; no parallel KingbaseES form was created.
- Required an explicit port because the local `54321` mapping is not a portable product default.
- Kept schema optional; non-empty KingbaseES schemas are existence-checked and applied as transaction-local search path.
- Reused dynamic Adapter lookup; rejected a Tool database-type branch.
- Fixed Provider session configuration once in the common utility; rejected copied PostgreSQL Provider logic.
- Used an independently permissioned read-only identity; rejected administrator-only Tool acceptance.
- Kept the common validator as the first defense; rejected database permission failure as a validator substitute.
- Retained the runtime overlay boundary; rejected an installed-plugin claim.
- Deferred wheel inclusion and redistribution review to Phase 9.8.

## Blocker Trace

No Phase 9.7 acceptance blocker remains.

The only implementation issue found was the missing Provider session/schema lifecycle call. Evidence localized it to `verify_database_connection`; the minimal common fix and KingbaseES schema-existence check passed real KingbaseES and real PostgreSQL regression.

## Reproduction Trace

Prerequisites:

- checkout at or after `842fdca`;
- running preserved `dify-plugin-phase94-kingbase` and `dify-plugin_daemon-1`;
- running `dify-db_postgres-1` for targeted regression;
- `/tmp/kingbasees_phase95/site` containing the verified candidate dependency overlay;
- transient KingbaseES admin, generated read-only, and PostgreSQL credentials.

Copy the current Provider, Tool, utils, and gate script to `/tmp/kingbasees_phase97/plugin`, then run the command above. The gate idempotently prepares the fixture and emits four JSON suites. Any non-PASS case identifies Provider validation, Tool content/contract, SQL/database permission, or PostgreSQL/common regression failure separately.

## Tutorial Relevance

- Provider fields and formal Tool invocation: `TUTORIAL_REQUIRED`;
- explicit KingbaseES port and optional schema behavior: `TUTORIAL_REQUIRED`;
- read-only fixture/identity setup: `TUTORIAL_REFERENCE`;
- missing Provider session configuration incident: `DEVELOPMENT_HISTORY_ONLY`;
- JSON and logs: `EVIDENCE_ONLY`;
- `/tmp/kingbasees_phase95` and `/tmp/kingbasees_phase97`: `TEMPORARY`.

## Final Boundary and Next Step

All Phase 9.7 acceptance criteria passed. This changes the final plugin source and is reproducible from the committed gate and evidence, but it is not installed-plugin or offline-package proof.

Proceed to Phase 9.8 — KingbaseES Offline Driver Packaging and Installed Plugin Gate. Workflow API and final end-to-end acceptance remain later independent gates.
