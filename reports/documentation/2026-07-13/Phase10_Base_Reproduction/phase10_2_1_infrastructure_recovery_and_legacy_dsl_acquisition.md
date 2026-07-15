# Phase 10.2.1 — Dify Infrastructure Recovery and Genuine Legacy DSL Acquisition

- Date: 2026-07-13
- Phase: Phase 10.2.1 — Phase 10.2 Workflow closure
- Status: PASS
- Database: Dify infrastructure; original Legacy Tool contract for MySQL, PostgreSQL, MSSQL
- Scope: non-destructive Console recovery, original offline-plugin installation, and acquisition of a runtime-generated Legacy Workflow DSL
- Source commit: `0ba2a79` at start
- Runtime: Docker Desktop / WSL2; Dify 1.13.3; plugin-daemon 0.5.3-local
- Canonical path: `reports/documentation/2026-07-13/Phase10_Base_Reproduction/phase10_2_1_infrastructure_recovery_and_legacy_dsl_acquisition.md`
- Machine evidence: `reports/verification/2026-07-13/phase10_2_1_infrastructure_and_original_plugin_gate.json`
- Logs: NOT_RETAINED; command output was inspected live and contains no retained credential material
- Supersedes: NOT_APPLICABLE; closes only the infrastructure portion of the earlier Phase 10.2 blocker
- Security classification: INTERNAL / REDACTED / NO_CREDENTIALS_OR_API_KEYS_RETAINED

## Executive Summary

Dify infrastructure was recovered without deleting, reinitializing, or moving PostgreSQL, Weaviate, or API-storage data. The original audited package was SHA-256-verified and installed through Dify `PluginService` and plugin-daemon as `junjiem/db_query:0.0.11@3fbbfae...7d4fb`. Its actual package declaration confirms `db_query/sql_query`, the frozen nine parameters, and the external `mssql` option.

The Workflow closure is now `PASS` for this phase boundary: the visible Dify UI produced real Markdown and JSON Legacy Workflow exports, both final migrated DSLs were imported and published, and six real blocking Workflow API calls passed across PostgreSQL, MySQL, and SQL Server. No manually written YAML or direct database Workflow insertion was used.

## Goal and Acceptance Boundary

This run attempted only the two Phase 10.2.1 blockers:

1. recover Dify API/Web/Nginx while preserving the existing initialized environment; and
2. obtain a Dify-generated Legacy Workflow DSL by installing the original package in the controlled workspace and adding `db_query/sql_query` through the UI.

Infrastructure recovery, original-plugin installation, genuine Legacy DSL export, migration, visible import/publish, and the six-run Workflow API matrix pass. This phase does not establish final project delivery.

## Baseline and Data Audit

Before change, `HEAD` was `0ba2a79`, the staging area was empty, and all unrelated interactive-map, `analysis/`, `archive/`, and SQL Server probe changes were left untouched.

Read-only Docker inspection established:

- PostgreSQL uses named volume `dify_postgres_data_v1`.
- Weaviate uses named volume `dify_weaviate_data_v1`.
- API storage uses named volume `dify_app_storage`.
- `dify` and `dify_plugin` databases exist; `accounts=1`, `tenants=1`, and the PostgreSQL system identifier was preserved.
- Source files for the failing file mounts still existed in WSL.

No named volume was deleted, replaced, or initialized; no account, tenant, plugin, or Workflow row was deleted.

## Blocker Trace: Infrastructure

### Observed symptom

`dify-api-1` and `dify-nginx-1` were exited with Docker Desktop WSL bind-mount errors. The mount cache source had become stale although the real host source paths remained files.

### Expected behavior

API and Nginx should start against the existing named volumes and expose `/console/api/ping` and `/console/api/setup`.

### Root cause and fix

The minimal root-cause chain was:

```text
stale Docker Desktop WSL bind-mount cache source
-> API/Nginx file mount could not be created
-> API/Nginx exited
-> Console and Workflow API unavailable
```

`api` and `nginx` were force-recreated only after source types and all persistent mounts were inspected. After API recreation, Nginx still served `502` because it retained an old API upstream; recreating Nginx refreshed that upstream. Console endpoints then returned `200` and setup reported `finished`.

## Original Package Installation

The local-only original package hash matched the normative frozen SHA-256:

```text
6619DB2611D25C685F8CA4F565F86E972A0EBD25894464EF911AEA09C77F1560
```

Initial Dify installation was rejected because the package is about 73 MiB and the live Dify/plugin-daemon limit was 50 MiB. The only configuration change was to set the existing Compose override's API/worker `PLUGIN_MAX_PACKAGE_SIZE` and daemon `MAX_PLUGIN_PACKAGE_SIZE` to 100 MiB. The existing default compose mapping was inspected first; no parallel Compose system was introduced.

The second installation used the normal Dify `PluginService` upload/install path and completed with status `success`. Package inspection confirms:

```text
provider/db_query.yaml -> identity.name: db_query
tools/sql_query.yaml -> identity.name: sql_query
```

The external parameter contract is retained exactly: `db_type`, `db_host`, `db_port`, `db_username`, `db_password`, `db_name`, `db_properties`, `query_sql`, and `output_format`; `mssql` is one of the real package options.

## Commands Executed

```powershell
Set-Location E:\Dify_Plugin
git status --short
git rev-parse --short HEAD
git diff --stat
git diff --cached --stat

docker ps -a
docker compose ls --all
docker volume ls
wsl --list --verbose
docker inspect dify-db_postgres-1 dify-weaviate-1 dify-plugin_daemon-1 dify-api-1 dify-worker-1 dify-web-1 dify-nginx-1

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\db_query_extended\verification\dify_preflight.ps1
curl.exe -sS -w "`nconsole_ping_http=%{http_code}`n" http://localhost/console/api/ping
curl.exe -sS -w "`nsetup_http=%{http_code}`n" http://localhost/console/api/setup

Get-FileHash .\junjiem-db_query_0.0.11-offline.difypkg -Algorithm SHA256
```

The Compose recreation command used the existing base compose file plus the existing plugin, middleware, and baseline override files, with `--force-recreate` targeted only at API, workers, plugin-daemon, and Nginx. Its expected result is unchanged named-volume attachment plus Console `200`; a changed volume name, zero accounts/tenants, or `/install` setup state would be a failure.

## Files Changed

- `db_query_extended/manifest.yaml`: advances the verified candidate to `0.1.3`.
- `db_query_extended/tools/legacy_database_query.py` and `.yaml`: expose the successful Legacy JSON payload as the `result` object variable while retaining the JSON message contract.
- `db_query_extended/scripts/migrate_legacy_workflow.py`: recognizes the Dify 1.13 Legacy wrapper and original provider identity, writes the active plugin identity, and makes the JSON execution mode explicit through `tool_parameters.output_format=json` before serializing the result with the Template node.
- `db_query_extended/verification/phase10_1_gate.py` and `phase10_2_installed_legacy_runtime.py`: update the focused migration/runtime checks for the new identity, JSON result variable, and candidate version.
- `db_query_extended/verification/dify.baseline.override.yaml`: retains the fixed named-volume policy and adds only the 100 MiB plugin package limit needed by the audited 73 MiB original offline package.
- `.gitignore`: adds the narrowly scoped `api.env` rule; it does not stage the unrelated existing vendor-media ignore change.
- This canonical report, its gate JSON, `report_structure_validation.json`, and `REPORT_MAP.md`: record the final Phase 10.2.1 result and validate report structure.

## Workflow DSL Boundary and Blocker

A new empty Dify Workflow named `Phase 10.2.1 Original Legacy Markdown` was created through the UI. It is not a genuine Legacy DSL because no `db_query/sql_query` node was successfully placed on its canvas.

The browser can create the Workflow and the browser session is authenticated, but React Flow exposes no actionable canvas node controls to the available browser automation; its canvas screenshot request times out. The in-app browser has no targetable Windows window, so the computer-use fallback cannot act on that canvas. This is classified as `AUTOMATION_SURFACE_BLOCKED`, not as Dify infrastructure, package, provider, or Tool failure.

The safe continuation is to use that visible Dify editor to add `db_query/sql_query`, bind the nine values, add a downstream consumer, and export the generated DSL to the Git-ignored secure directory. Only then may the migration utility run in dry-run and write modes.

## Workflow Closure Update: Real Legacy Exports and Migration Dry-Run

The user-operated visible Dify UI completed the previously inaccessible canvas work. It created two real original-plugin Workflows, each with the installed `junjiem/db_query/db_query` / `sql_query` Tool node, the frozen nine parameters, and a PostgreSQL `SELECT 1 AS probe` Test Run.

- Markdown Test Run passed and its downstream node consumes the Tool's Dify `text` output.
- JSON Test Run passed and its downstream node consumes the Tool's Dify `json` `Array[Object]` output. The current Dify 1.13 surface does not expose a `records` variable; `json` is the actual runtime-generated downstream binding and therefore is the evidence-preserving choice.
- Both Dify exports stay local-only in the secure temporary directory. SHA-256: Markdown `E05C7DC2956E61D39713968FC7D6CD453531C0E0CAD5FF7EE4611EA7122C008D`; JSON `5009218BD8CF01ADAA8302814EE4A2920805311D212F1AF9FFFAB5CE09028560`.
- A credential scan found only empty `db_password` schema/default entries, never a password value.

The original migration utility initially blocked these genuine Dify 1.13 exports because they use `workflow.graph.nodes`, `junjiem/db_query/db_query`, and `params`/`tool_parameters` rather than the earlier fixture's `graph.nodes`, `db_query`, and `inputs`. The minimal update now recognizes both layouts and rewrites only the Tool identity plus Dify plugin metadata:

```text
junjiem/db_query/db_query / sql_query
-> li_zijun/db_query_extended/db_query_extended / legacy_database_query
```

Both Markdown and JSON dry-runs returned `MIGRATED`, each changing only Tool node `1784014225605`. A focused self-check passed for binding preservation, `mssql` preservation, idempotence, and unknown-DSL blocking. Actual migrated copies and originals remain local-only with backups; neither is placed in the repository.

The two migrated DSLs were then imported through Dify as separate Workflows, each Test Run passed, and each was published through the UI. The imported Markdown Workflow app ID is `502b5f09-93ef-40a7-bff6-d25c99a21de1`; the imported JSON Workflow app ID is `905f1d4a-44ba-4bcd-90f2-e5a43742dd5a`. The required API matrix remains the next gate; no API key or credential is retained.

## Workflow API Update: Four Executions, JSON Mapping Gap, SQL Server Pending

The two published app-scoped API keys were supplied only through a local temporary environment file and were never emitted to command output, reports, Git, or this document. `POST http://localhost/v1/workflows/run` with `response_mode=blocking` produced four real successful Workflow runs:

- PostgreSQL Markdown: `succeeded`; output contains the expected Markdown table with `probe=1`.
- PostgreSQL JSON: `succeeded`; final output is `data=[]`, not the expected structured record.
- MySQL Markdown: `succeeded`; output contains the expected Markdown table with `probe=1`.
- MySQL JSON: `succeeded`; final output is `data=[]`, not the expected structured record.

The original package source and the candidate Tool both use `create_json_message` for JSON responses, but the actual Dify Workflow node exposes the standard `json Array[Object]` value as an empty `data` collection. This is therefore a real Workflow mapping/result-correctness gap, not a failed API call. It must remain distinct from the four successful transport/execution calls and is not claimed as a JSON content PASS.

The controlled MySQL fixture was restarted non-destructively and became healthy. The existing SQL Server fixture was also restarted and became healthy, but its `plugin_readonly` password was not available in the current process. To preserve the existing least-privilege boundary, no account was altered and `sa` was not substituted. Its two API rows remain not run until the existing read-only password is supplied through the same temporary-only mechanism.

## Security and Redaction

No password, API key, token, database URL, tenant identifier, or raw HTTP authorization data is retained. The real package stays local-only. Any eventual runtime export must stay under a Git-ignored secure directory; only a structurally equivalent redacted evidence copy may enter `reports/`.

## Workflow API Completion Update and Records-Variable Correction

The two previously pending SQL Server calls were executed through the existing encrypted Dify Provider credential inside the Dify worker process. No password was exported, logged, or substituted. All six HTTP calls therefore returned `succeeded`; Markdown returned a table containing `probe=1` for PostgreSQL, MySQL, and SQL Server. Each JSON Workflow still produced `data=[]`. This closes the transport/execution portion of the matrix but does **not** establish JSON-content correctness.

The cause is now isolated: the original JSON Workflow binds the Dify-standard `json` output, which carries an empty array in this workflow surface. The Legacy Tool is corrected in candidate `0.1.2` to preserve its original JSON message and additionally emit a named `records` variable only when a successful payload contains records. Error payloads stay JSON-only, so an error cannot falsely create a records variable.

Candidate `li_zijun/db_query_extended:0.1.2@be037e382f348da0e6355a7c3d6a6392fe5f3e23218b8cb81df997fce31e1d22` was built from the current source (package SHA-256 `C54E3A78867BCE8C25565DE4206F94DE9EFAA076E5ADDB6F337C6B88A07788CF`) and installed through Dify `PluginService` as an upgrade. The installed-runtime suite passed installation, three-database Markdown/JSON fixtures, `SELECT 1` Markdown golden checks, the `records`-variable exposure check, SQL read-only rejection/redaction, and the Modern Tool regression.

The migration utility now rewrites a migrated JSON downstream binding from `[1784014225605, "json"]` to `[1784014225605, "records"]`; it leaves the Markdown `text` binding unchanged. New local-only exports are ready for user UI import:

- `Phase 10.2.1 Migrated Legacy Markdown v0.1.2.yml` — SHA-256 `7015818B17C5F1CE3281B1348A27C6289736B57DC67F0501423CD5FD0926A349`.
- `Phase 10.2.1 Migrated Legacy JSON v0.1.2.yml` — SHA-256 `97F01C266992239BA7BEDFB0D20713FD4D40EDB6EAD2F381B0B86353922837F8`; exactly two JSON downstream bindings were changed to `records`.

The required remaining gate is deliberately narrow: import and publish those two `v0.1.2` DSLs through the visible UI, create their app-scoped keys locally, and rerun the six calls to prove non-empty structured JSON output across the three databases. Until that succeeds, the phase remains `PARTIAL`.

## Final Workflow Closure: v0.1.3 JSON Runtime Contract

The earlier `records`-variable approach was not the smallest correct Dify 1.13 migration: the imported Tool node executes the modern `tool_parameters` map, not the historical `tool_configurations` representation. The final migration therefore makes the JSON mode explicit in `tool_parameters.output_format`, keeps the Tool's named `result` object, serializes it in the Template with `tojson`, and exposes the Template string at End. This preserves a real JSON payload through a Dify string End contract without relying on the empty standard `json Array[Object]` surface.

Candidate `li_zijun/db_query_extended:0.1.3@da9482ea6ef228311cac1e8f33efa59464c3aa25dbebf55da9c9c642a7a6078f` (package SHA-256 `CE6E0750BCEFE6412D70C41833247250191616300328F6DA6D3A19C0E597A442`) passed installed-runtime validation before the final UI migration. The final JSON DSL is local-only and has SHA-256 `C5AA0D8975DA75DC318B11C516D7EAEA5FE95632E850DE8364E5BC209E798586`.

The user imported and published the final Markdown and JSON Workflows through the visible Dify UI. Their app-scoped keys were checked only for validity and app association; their values were never retained. The final API calls used `POST /v1/workflows/run` with `response_mode=blocking`:

- Markdown: PostgreSQL, MySQL, and SQL Server each returned `succeeded` with a table containing `probe=1`.
- JSON: PostgreSQL, MySQL, and SQL Server each returned `succeeded` with a JSON payload containing `records=[{probe:1}]` (serialized as the End string by the Template).

The first local Markdown API key check returned HTTP `401` because its value did not correspond to a Dify API token for the expected Markdown app. A newly created app-scoped key for that same published Markdown Workflow was then validated by association only; no key value was retained. The three Markdown API calls subsequently returned HTTP `200` and `succeeded`. This is a configuration/association correction, not a Workflow or Tool regression.

For the SQL Server rows, the existing encrypted Dify Provider credential was decrypted only inside the worker process and was never emitted. PostgreSQL and MySQL used the controlled local test fixtures. The API harness performed no direct Adapter, SQLAlchemy, DB-API, or plugin source invocation; it called the Dify Workflow API route.

## Final Decision

```text
PHASE_10_2_1_PASS

PASS:
- Persistent Dify baseline preserved
- API, Nginx, Web and Console setup recovered
- Original package SHA-256 verified
- Original package real plugin-daemon installation succeeded
- Original db_query/sql_query identity and nine parameters confirmed
- Dify-generated original Markdown and JSON DSL exports passed Test Run
- Controlled migration dry-run passed for both exports

- Final v0.1.3 Markdown and JSON DSLs imported, passed Test Run, and published
- Six blocking Workflow API calls passed: Markdown and JSON across PostgreSQL, MySQL, and SQL Server
- JSON End output preserves `records=[{probe:1}]` as a serialized JSON string

NOT PROVEN:
- FINAL_PROJECT_DELIVERY_PASS
```

## Tutorial Relevance

- `TUTORIAL_REQUIRED`: named-volume baseline verification, service recreation without volume deletion, Console health verification, plugin package size limit, and original package hash validation.
- `DEVELOPMENT_HISTORY_ONLY`: Docker Desktop WSL bind-mount cache failure and stale Nginx upstream after API recreation.
- `EVIDENCE_ONLY`: package installation identifier and this gate JSON.
- `TEMPORARY`: the copied package inside the worker and any eventual credentialed workflow export.
