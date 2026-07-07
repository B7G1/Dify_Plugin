# Phase 10 — KingbaseES Implementation Plan

## Entry gate

Do not begin business-code changes until all items are recorded:

1. exact KingbaseES version/build and PostgreSQL compatibility mode;
2. Linux `amd64` deployment source and default port;
3. UTF-8 server/client encoding plan;
4. official `ksycopg2` artifact for plugin-daemon Python 3.12;
5. official KingbaseES SQLAlchemy dialect compatible with SQLAlchemy 2.0.51;
6. native client-library loading procedure;
7. driver, dialect, and native-library redistribution decision;
8. clean plugin-daemon import and `SELECT 1` spike outside the release package.

## Step 1 — Environment and evidence fixture

- Provision an isolated KingbaseES instance; do not change the accepted Dify PostgreSQL volumes.
- Create a dedicated database, schema, object owner, and read-only test user.
- Grant the runtime user only connect, schema usage, and select permissions.
- Load deterministic rows for Unicode, emoji, timestamps, exact numerics, nulls, booleans, binary, JSON/JSONB, and truncation.
- Record server version, compatibility mode, encoding, architecture, and checksum/source of driver artifacts without credentials.

Exit: native driver imports in plugin-daemon Python 3.12 and a standalone read-only connection succeeds.

## Step 2 — Adapter

- Add `utils/adapters/kingbasees.py` implementing the unchanged `DatabaseAdapter` contract.
- Build the URL with `URL.create("kingbase+ksycopg2", ...)`.
- Map connection timeout and verified SSL arguments only.
- Implement transaction-local schema/search-path and statement-timeout setup after real probes.
- Reuse shared query execution and formatting.
- Do not copy PostgreSQL Adapter code wholesale or alias KingbaseES to PostgreSQL.

Exit: unit-level URL/connect-argument/session tests pass without touching frozen adapters or formatter/security code.

## Step 3 — Provider configuration

- Add `kingbasees` as a new Provider database type.
- Add default port `54321` and accurate bilingual help text.
- Reuse existing host, port, username, password, database, timeout, SSL, and optional schema concepts.
- Extend connection validation additively; existing identifiers and defaults remain unchanged.
- Validate correct, wrong-password, missing-field, unavailable-host, and driver-load paths without logging secrets.

Exit: real Provider Credential Validation passes and negative cases return controlled messages.

## Step 4 — Requirements and runtime

- Pin exact offline versions of `ksycopg2`, the KingbaseES dialect, and required native libraries.
- Keep existing dependency versions unchanged unless an isolated compatibility review proves that impossible.
- Document library search paths needed by plugin-daemon.
- Perform a clean Linux amd64 install test before packaging.
- Do not commit or distribute vendor binaries until licensing is approved.

Exit: clean runtime imports all dependencies and executes `SELECT 1` using the final dependency set.

## Step 5 — Additive verification

- Add a dedicated KingbaseES runner; do not rewrite `verify_all.ps1` or its v1.0 totals.
- Cover Provider, URL/connect arguments, schema isolation, timeout, scalar/multi-row queries, truncation, Unicode, time, numeric, null, boolean, binary, JSON, controlled SQL errors, and connection cleanup.
- Add the full KingbaseES dangerous-SQL matrix while leaving shared SQL Security unchanged.
- Write evidence to a new dated directory with no password, API key, or full connection URL.
- Freeze the additive test inventory before final execution.

Exit: additive suite reaches at least `24 PASS / 0 FAIL / 0 SKIP` and inherited regression remains `45/0/0`.

## Step 6 — Workflow and API acceptance

- Create a KingbaseES Provider credential in Dify using the read-only account.
- Create a separate Workflow with the frozen Start(`sql`, `max_rows`) → Tool → End(`result`) contract.
- Run `SELECT 1`, Chinese/emoji, timestamp, numeric/JSON, multi-row/truncation, timeout/error, and dangerous-SQL cases.
- Publish the Workflow and invoke its API for the same contract.
- Supply the Workflow API key only through the current process environment; never write it to scripts, evidence, reports, or Git.

Exit: UI and API results preserve the existing JSON contract and all expected cases pass.

## Step 7 — Full regression

- Run the untouched v1.0 `verify_all.ps1` against MySQL, PostgreSQL, and DM8.
- Require exactly `45 PASS / 0 FAIL / 0 SKIP`.
- Run the KingbaseES suite separately and combine summaries only in a new Phase 10 report.
- Any inherited failure stops Phase 10 acceptance; fix only the responsible additive layer.

Exit: inherited `45/0/0`, additive KingbaseES at least `24/0/0`, combined at least `69/0/0`.

## Step 8 — Documentation and release preparation

- Update `TEST_MATRIX.md` only after real evidence.
- Add Phase 10 technical, executive, verification, compatibility, limitation, and migration notes.
- Update Dashboard and release indexes without rewriting v1.0 evidence.
- Record exact versions, checksums, license decision, recovery steps, and known limitations.
- Package only after human review authorizes the release candidate.

## Stop conditions

Pause implementation and request review if:

- Python 3.12 or SQLAlchemy 2.0.51 is unsupported by the available official artifacts;
- the driver requires replacing a frozen dependency;
- schema or timeout support requires modifying the base Adapter contract;
- a KingbaseES SQL bypass requires shared SQL Security changes;
- vendor binaries cannot legally be redistributed;
- any v1.0 regression produces FAIL or SKIP.

## Current decision

Design is complete. Proceed to code implementation only after the entry-gate driver/runtime/licensing probe is documented as PASS.
