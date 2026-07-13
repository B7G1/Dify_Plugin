# Phase 9.9 — Installed KingbaseES Workflow API and End-to-End Gate

- Date: 2026-07-13
- Phase: Phase 9.9
- Status: PASS
- Database: KingbaseES
- Scope: Installed plugin Workflow publication, real Workflow API execution, runtime trace, SQL safety, failure recovery, and targeted regression
- Source commit: `c69695e`
- Runtime: Dify 1.13.3, plugin-daemon 0.5.3-local, Python 3.12.3, Linux amd64, SQLAlchemy 2.0.51, ksycopg2 2.9.1
- Canonical path: `reports/documentation/2026-07-13/Phase09_KingbaseES/phase9_9_kingbasees_installed_workflow_end_to_end_gate.md`
- Machine evidence: `reports/verification/2026-07-13/kingbasees_phase9_9_*.json`
- Logs: `reports/logs/2026-07-13/Phase09_KingbaseES/phase9_9_*.log`
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / REDACTED / REDISTRIBUTION_REVIEW_PENDING

## Final Delivery Contract Reference

This report is governed by `reports/documentation/PROJECT_DELIVERY_CONTRACT.md` and `reports/REPORTING_STANDARD.md`.

Phase 9.9 closes the installed KingbaseES technical chain through Workflow API. It does not complete the whole project, approve public redistribution, close DM8 delivery, or complete the Development Process Document and build-from-template tutorial.

## Executive Summary

Phase 9.9 is `PASS`.

A dedicated KingbaseES Workflow was created, explicitly bound to the Phase 9.8 read-only KingbaseES Provider credential and the active installed plugin, published, API-enabled, and invoked through the real Dify endpoint `POST /v1/workflows/run`. The 22-call formal matrix passed with zero skipped cases:

- 12 positive query and output-contract calls;
- 5 SQL-safety and integrity calls;
- 4 failure-recovery sequence calls;
- 1 existing DM Workflow API regression call.

Every call was correlated to a persisted Dify `WorkflowRun` and its start, Tool, and end node executions. All 21 KingbaseES calls recorded the installed identifier:

```text
li_zijun/db_query_extended:0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9
```

The installed runtime loaded ksycopg2 and `libkci.so.5` from that package's `.venv`; no Phase 9.5 driver overlay or plugin source override was used.

The allowed conclusions are:

```text
PHASE_9_9_PASS
KINGBASEES_INSTALLED_WORKFLOW_API_PASS
KINGBASEES_END_TO_END_PASS
KINGBASEES_FINAL_OFFLINE_PLUGIN_TECHNICAL_PASS
```

## Goal and Acceptance Boundary

The goal was to extend the Phase 9.8 installed Provider/Tool PASS through a real published Workflow and public Workflow API call:

```text
Workflow API request
-> Dify published Workflow
-> installed Tool node
-> installed Provider credential
-> installed Adapter and dialect
-> installed ksycopg2 and libkci.so.5
-> real KingbaseES server
-> Tool JSON
-> end-node output
-> Workflow API response
```

The following were deliberately out of scope:

- public redistribution approval for the Kingbase driver or bundled native library;
- final DM8 offline delivery closure;
- full cross-database release regression;
- final Development Process Document;
- final build-from-template tutorial;
- final project delivery declaration.

## Baseline

- Branch: `feature/kingbasees-adapter`
- HEAD at start: `2d9d187 docs: establish final delivery contract`
- Phase 9.8 product/package source commit: `73ed5f3`
- Phase 9.8 installed candidate verification commit: `72f28e9`
- Phase 9.8 report commit: `5071163`
- Worktree baseline: 43 pre-existing modified/untracked paths, all treated as protected user work.
- Active installed plugin identifier: `li_zijun/db_query_extended:0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9`

No Phase 9.8 commit was amended or modified.

## Environment Preflight

The retained runtime was inspected before the formal gate. Required services were running:

| Role | Container | Image | State |
| --- | --- | --- | --- |
| KingbaseES | `dify-plugin-phase94-kingbase` | `kingbase_v009r001c010b0004_single_x86:v1` | running |
| Dify metadata PostgreSQL | `dify-db_postgres-1` | `postgres:15-alpine` | running / healthy |
| Dify API | `dify-api-1` | `langgenius/dify-api:1.13.3` | running |
| Dify worker | `dify-worker-1` | `langgenius/dify-api:1.13.3` | running |
| Dify web | `dify-web-1` | `langgenius/dify-web:1.13.3` | running |
| Dify nginx | `dify-nginx-1` | `nginx:latest` | running |
| plugin-daemon | `dify-plugin_daemon-1` | `langgenius/dify-plugin-daemon:0.5.3-local` | running |
| Redis | `dify-redis-1` | `redis:6-alpine` | running / healthy |
| Sandbox | `dify-sandbox-1` | `langgenius/dify-sandbox:0.2.14` | running / healthy |

The host had neither `DIFY_WORKFLOW_API_URL` nor `DIFY_WORKFLOW_API_KEY`. The dedicated app credential was therefore generated through Dify's application credential model, persisted only in Dify, used in memory, and never emitted to evidence or logs.

## Installed Runtime Identity

The Phase 9.8 installed-runtime probe was reused against the live installed root with an empty plugin `PYTHONPATH` overlay:

```text
/app/storage/cwd/li_zijun/db_query_extended-0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9
```

Measured results:

- Python: 3.12.3;
- SQLAlchemy: 2.0.51;
- ksycopg2: 2.9.1;
- ksycopg2 module: installed plugin `.venv`;
- `libkci.so.5`: installed plugin `.venv`;
- Adapter/dialect import identity: PASS;
- PostgreSQL identity isolation: PASS;
- Phase 9.5 overlay: absent.

The verification harness used `PYTHONPATH=/app/api` only so a process inside `dify-worker-1` could import Dify's own application services and evidence models. That path is Dify application source, not plugin source or driver overlay. The Tool itself was dispatched by Dify to the installed plugin-daemon runtime above.

## Dedicated Workflow

The gate created and published one dedicated Workflow:

- name: `KingbaseES Phase 9.9 Installed Workflow Gate`;
- app ID: `98858e19-ec52-42ef-ad46-9114d16d545c`;
- published Workflow ID: `98a0fe03-b7df-4119-8ddd-7f0c8a5b69ac`;
- nodes: start -> installed database Tool -> end;
- start inputs: `sql`, `max_rows`;
- Provider credential: `KingbaseES Phase 9.8 Readonly`;
- credential binding: explicit by Dify credential ID;
- plugin binding: explicit active installed identifier;
- API state: enabled.

The existing DM Workflow was used only as a structural source and regression target. Its database credential was not reused by the KingbaseES Workflow. No existing production or user Workflow was repointed.

## Real Workflow API Invocation

The formal calls used:

```text
POST http://nginx/v1/workflows/run
Authorization: Bearer <redacted Dify app credential>
Content-Type: application/json
response_mode: blocking
```

The caller was an independent verification process inside `dify-worker-1`. It used Dify nginx and the public `/v1/workflows/run` service route; it did not invoke the Adapter, Tool class, SQLAlchemy, or DB-API directly.

For each response, the harness read persisted Dify evidence and asserted:

- Workflow run input contains non-null `sql` and the expected `max_rows`;
- start node received the API input;
- Tool node resolved a non-null SQL input and invocation payload;
- Tool node returned structured JSON;
- end-node input/output equals the Tool result;
- Workflow output equals the end-node output;
- Tool execution metadata identifies the installed plugin checksum.

The nginx access log contains exactly 22 formal `POST /v1/workflows/run` responses, all HTTP 200. Controlled SQL rejection is represented as a successful Workflow transport with the Tool's structured safe error contract; it is not an HTTP transport failure.

## Positive Query Matrix

All 12 positive cases passed against the real KingbaseES fixture:

| Case | Result |
| --- | --- |
| `SELECT 1` | PASS; `probe=1` |
| fixture rows | PASS; actual table data returned |
| Chinese Unicode | PASS; fixture value preserved |
| NULL | PASS; JSON `null` preserved |
| NUMERIC/DECIMAL | PASS; value serialized through the common formatter |
| DATE | PASS |
| TIMESTAMP | PASS |
| schema-qualified read | PASS against `phase97_fixture` |
| `max_rows` | PASS |
| empty result | PASS; zero rows |
| aggregate | PASS |
| `ORDER BY` | PASS; deterministic order verified |

This matrix used fixture reads, not only SQL literals or catalog metadata.

## Output Contract

All 12 positive cases verified the installed Tool and Workflow output contract:

```text
columns
rows
row_count
truncated
max_rows
database_type
execution_time_ms
```

The formal result also retained the existing `success`, `error`, `warning`, and `generated_at` fields. The gate did not change the public formatter or add a KingbaseES-only response field.

`max_rows` and truncation behavior passed at the requested boundary, and the value propagated from Workflow input to Tool output. Empty results retained columns and returned `row_count=0` without being treated as failure.

## SQL Safety and Integrity

All five security cases passed:

- DML attempt: blocked by the common validator with `ReadOnlyViolationError`;
- DDL attempt: blocked by the common validator with `ReadOnlyViolationError`;
- multi-statement attempt: blocked by the common validator with `ReadOnlyViolationError`;
- controlled database error: returned `SqlExecutionError` without credentials, credentialed URL, token, or secret;
- post-rejection integrity probe: fixture check for `id=999` returned count zero.

The public SQL validator was the primary enforcement point. The dedicated database read-only account remained the defense-in-depth boundary. No write was accepted and fixture state was unchanged.

## Failure Recovery

The formal sequence was:

```text
successful query
-> controlled SQL rejection
-> SELECT 1
-> fixture read
```

All four calls passed. The controlled failure did not poison the installed Tool, Provider connection lifecycle, Workflow, plugin-daemon, or subsequent API requests. No service restart was needed for this formal recovery sequence.

## Baseline API Incident and Recovery

Before the formal gate, the first real existing-DM Workflow API baseline request timed out after 120 seconds. Nginx recorded HTTP 499 and no new `WorkflowRun` existed. Container-local Dify API health/setup requests also timed out although Gunicorn processes were still present.

Blocker trace:

```text
Observed symptom: existing DM Workflow API request timed out; nginx returned 499; no WorkflowRun.
Expected behavior: existing DM Workflow API returns HTTP 200 and a persisted run.
Initial hypothesis: nginx, Workflow, or plugin-daemon path failure.
Evidence collected: dify-api local endpoints also hung; downstream containers remained running.
Root cause: existing dify-api service process was unresponsive.
Fix: restart only the existing dify-api-1 container.
Validation after fix: setup endpoint returned HTTP 200, DM smoke passed, then all 22 formal calls passed.
```

KingbaseES, its volume, PostgreSQL, plugin-daemon, installed plugin, Redis, and user data were preserved. There was no prune, rebuild, package reinstall, database restart, or volume recreation.

## Targeted Regression

All seven targeted cases passed:

- PostgreSQL Provider real credential validation;
- PostgreSQL Tool real `SELECT 1`;
- existing DM Workflow API `SELECT 1`;
- Provider schema option order: `mysql`, `postgresql`, `dm`, `sqlserver`, `kingbasees`;
- Tool schema identity;
- active installed plugin identifier unchanged;
- installed Adapter/dialect and PostgreSQL identity isolation.

SQL Server remains `OPTIONAL`; this gate did not promote it into the main matrix. A complete cross-database regression and DM8 final delivery were not run or claimed.

## Commands Executed

Commands below are the material reproduction trace. They were run from PowerShell in `E:\Dify_Plugin` unless a container shell is shown.

```powershell
git status --short
git log -15 --oneline
git branch --show-current
docker ps -a
docker inspect dify-plugin-phase94-kingbase
docker inspect dify-plugin_daemon-1

# Reuse the Phase 9.8 probe against the installed plugin, without a plugin overlay.
docker cp db_query_extended/verification/kingbasees_phase9_8_runtime_probe.py dify-plugin_daemon-1:/tmp/kingbasees_phase9_8_runtime_probe.py
docker exec dify-plugin_daemon-1 sh -lc "PYTHONPATH= python /tmp/kingbasees_phase9_8_runtime_probe.py --installed-root '/app/storage/cwd/li_zijun/db_query_extended-0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9' --expected-checksum 'bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9' --output /tmp/kingbasees_phase9_9_installed_runtime.json"
docker cp dify-plugin_daemon-1:/tmp/kingbasees_phase9_9_installed_runtime.json reports/verification/2026-07-13/kingbasees_phase9_9_installed_runtime.json

# Copy only verification inputs into the independent Dify worker process.
docker cp db_query_extended/verification/kingbasees_phase9_9_workflow_gate.py dify-worker-1:/tmp/kingbasees_phase9_9_workflow_gate.py
docker cp reports/verification/2026-07-13/kingbasees_phase9_9_installed_runtime.json dify-worker-1:/tmp/kingbasees_phase9_9_installed_runtime.json
docker exec dify-worker-1 sh -lc "mkdir -p /tmp/kingbasees_phase9_9_20260713_0802 && PYTHONPATH=/app/api python /tmp/kingbasees_phase9_9_workflow_gate.py --output-dir /tmp/kingbasees_phase9_9_20260713_0802 --runtime-evidence /tmp/kingbasees_phase9_9_installed_runtime.json"

docker cp dify-worker-1:/tmp/kingbasees_phase9_9_20260713_0802/. reports/verification/2026-07-13/
python -m py_compile db_query_extended/verification/kingbasees_phase9_9_workflow_gate.py
git diff --check
git status --short
git diff --staged
```

The first harness attempt without `PYTHONPATH=/app/api` failed before any gate execution with `ModuleNotFoundError: app_factory`. The corrected command exposes Dify's own application module path to the harness. It does not expose repository plugin source to plugin-daemon and does not weaken the installed-runtime assertion.

## Files Changed

Formal verification:

- `db_query_extended/verification/kingbasees_phase9_9_workflow_gate.py` — creates/publishes the dedicated Workflow, calls the real API, correlates run/node evidence, and produces the matrix.

Human report and index:

- this canonical report;
- `reports/REPORT_MAP.md` — one Phase 9.9 entry.

Machine evidence:

- `kingbasees_phase9_9_preflight.json`;
- `kingbasees_phase9_9_installed_runtime.json`;
- `kingbasees_phase9_9_workflow_positive.json`;
- `kingbasees_phase9_9_workflow_types.json`;
- `kingbasees_phase9_9_workflow_contract.json`;
- `kingbasees_phase9_9_workflow_security.json`;
- `kingbasees_phase9_9_failure_recovery.json`;
- `kingbasees_phase9_9_runtime_trace.json`;
- `kingbasees_phase9_9_regression.json`;
- `kingbasees_phase9_9_final_gate.json`.

Redacted logs:

- `phase9_9_preflight.log`;
- `phase9_9_workflow_api.log`;
- `phase9_9_dify_api_redacted.log`;
- `phase9_9_worker_redacted.log`;
- `phase9_9_plugin_daemon_redacted.log`;
- `phase9_9_security.log`;
- `phase9_9_regression.log`.

No product source, manifest, requirements, wheel, `.difypkg`, Phase 9.8 artifact, database fixture, or release file changed.

## Decisions

1. A dedicated KingbaseES Workflow was created instead of repointing an existing DM Workflow, preserving user state and making the credential/plugin binding auditable.
2. The public Workflow API was required; an Adapter probe, Tool class call, or direct database script cannot prove Workflow publication, input resolution, node execution, and Workflow output.
3. The existing Dify service/model path was used for deterministic Workflow setup and evidence readback. API execution itself remained external through nginx.
4. The Phase 9.8 installed identifier was pinned and asserted in every KingbaseES Tool-node execution record. No old checksum or source runtime was accepted.
5. The existing output contract and common SQL validator were reused unchanged. No KingbaseES branch was added to Workflow or Tool code.
6. Driver redistribution remains pending review even though the installed technical chain is complete.

## Abandoned Paths

- Repoint an existing DM Workflow: rejected because it would mutate unrelated validation state.
- Direct Adapter/Tool invocation as Workflow evidence: rejected because it skips Dify API, publication, node input resolution, and persisted Workflow runs.
- Repository plugin `PYTHONPATH` overlay: rejected because it could hide an installed package defect.
- Administrator database account as acceptance identity: rejected in favor of the Phase 9.8 read-only credential.
- Database permissions as the only SQL-safety control: rejected; the common validator must fail first.
- Rebuild/reinstall after the Dify API hang: rejected; a minimal restart of only the unresponsive API container restored the existing environment.
- Claim full project delivery: rejected because DM8 and final documentation/tutorial deliverables remain open.

## Evidence

| Evidence | Purpose | Result |
| --- | --- | --- |
| `kingbasees_phase9_9_preflight.json` | baseline, containers, Workflow binding, API recovery | PASS |
| `kingbasees_phase9_9_installed_runtime.json` | installed driver/native library/source identity | PASS |
| `kingbasees_phase9_9_workflow_positive.json` | 12 real query cases | 12 PASS, 0 FAIL, 0 SKIP |
| `kingbasees_phase9_9_workflow_types.json` | Unicode/NULL/numeric/date/timestamp | 5 PASS |
| `kingbasees_phase9_9_workflow_contract.json` | output field contract | 12 PASS |
| `kingbasees_phase9_9_workflow_security.json` | DML/DDL/multi/error/integrity | 5 PASS |
| `kingbasees_phase9_9_failure_recovery.json` | success/failure/recovery sequence | 4 PASS |
| `kingbasees_phase9_9_runtime_trace.json` | 22 WorkflowRun and node traces | PASS |
| `kingbasees_phase9_9_regression.json` | PostgreSQL/DM/schema/identity regression | 7 PASS |
| `kingbasees_phase9_9_final_gate.json` | aggregate gate and conclusion boundary | PASS; skip count 0 |

Machine evidence includes real run IDs, node execution IDs, resolved SQL inputs, Tool JSON, Workflow outputs, assertions, and durations. Credentials are represented only by safe names/IDs and presence/length metadata.

## Security and Redaction

- No API credential value is written to repository evidence or logs.
- No database password or credentialed URL is retained.
- Dify and plugin-daemon logs were captured only for the execution window and stored as redacted logs.
- Automated scans returned zero matches for the known local secrets, Dify app-token shape, credentialed URLs, and populated Authorization headers.
- The official Kingbase license content and external media remain outside Git.
- Binary/driver redistribution classification remains `REDISTRIBUTION_REVIEW_PENDING`.

## Reproduction Trace

Prerequisites:

1. the Phase 9.8 plugin identifier above is installed and active;
2. retained KingbaseES and Dify containers are running;
3. Dify contains the named KingbaseES and PostgreSQL test credentials;
4. the KingbaseES read-only fixture from Phase 9.7/9.8 exists;
5. the installed-runtime evidence is regenerated for the current installed root.

Run the commands in **Commands Executed**. Expected terminal summary:

```json
{"status":"PASS","api_call_count":22,"gates":{"kingbasees_phase9_9_preflight":"PASS","kingbasees_phase9_9_workflow_positive":"PASS","kingbasees_phase9_9_workflow_types":"PASS","kingbasees_phase9_9_workflow_contract":"PASS","kingbasees_phase9_9_workflow_security":"PASS","kingbasees_phase9_9_failure_recovery":"PASS","kingbasees_phase9_9_runtime_trace":"PASS","kingbasees_phase9_9_regression":"PASS"}}
```

Failure meaning:

- installed-runtime identity failure: Phase 9.8 package/runtime regression;
- HTTP/API failure without a persisted run: Dify service/API blocker;
- missing or wrong plugin identifier in Tool metadata: installed-plugin binding failure;
- start/Tool/end mismatch: Workflow input or output-contract failure;
- unsafe statement accepted or fixture changed: security gate failure;
- post-failure query failure: lifecycle/recovery failure;
- any skip: acceptance matrix incomplete and therefore not PASS.

## Development Process and Tutorial Relevance

`DEVELOPMENT_HISTORY_REQUIRED`:

- why installed Provider/Tool PASS does not imply Workflow PASS;
- the API 499 incident, evidence-based root cause, minimal API-only restart, and preserved downstream state;
- why Dify application imports for the harness are distinct from a plugin source overlay;
- why persisted run/node metadata is needed to prove the actual installed checksum.

`TUTORIAL_REQUIRED`:

- create a database-specific Workflow;
- bind the Provider credential and Tool node;
- publish and enable the Workflow API;
- call `/v1/workflows/run` with `sql` and `max_rows`;
- verify Tool JSON, end-node output, API response, SQL rejection, and failure recovery.

`EVIDENCE_ONLY`:

- run IDs, node execution IDs, durations, raw structured outputs, and dated container snapshots.

`TEMPORARY`:

- `/tmp/kingbasees_phase9_9_20260713_0802` inside `dify-worker-1`;
- copied harness/runtime-evidence inputs inside the container;
- in-memory API and database credentials.

## Git State and Scope Protection

- Baseline protected entries: 43.
- Phase 9.9 test commit: `c69695e test: verify installed KingbaseES workflow end to end`.
- Documentation/evidence are committed separately from the test implementation.
- Exact-path staging was used; `git add .` and `git add -A` were not used.
- Unrelated `.gitignore`, interactive map, `analysis/`, `archive/`, `env_check/`, SQL Server probe directories, historical reports, and `test_tool_schema/` were not staged or modified by this phase.
- No destructive Git or Docker command was used.

## Final Decision

```text
PHASE_STATUS: PHASE_9_9_PASS

ALLOWED_CONCLUSIONS:
KINGBASEES_INSTALLED_WORKFLOW_API_PASS
KINGBASEES_END_TO_END_PASS
KINGBASEES_FINAL_OFFLINE_PLUGIN_TECHNICAL_PASS

NOT_YET_PROVEN:
FINAL_PROJECT_DELIVERY_PASS
PUBLIC_REDISTRIBUTION_APPROVED
DM8_FINAL_DELIVERY_PASS
DEVELOPMENT_PROCESS_DOCUMENTATION_COMPLETE
FROM_ZERO_REPRODUCTION_TUTORIAL_COMPLETE

REDISTRIBUTION_STATUS:
REDISTRIBUTION_REVIEW_PENDING
```

This phase changes the final plugin technical evidence, not product code. It is development-process history, contains material required by the future tutorial, and is reproducible from the committed harness plus dated machine evidence.

## Next Step

KingbaseES can leave its technical phase-gate sequence. The next independent engineering gate should close the DM8 final offline package and installed Workflow chain under the same no-skip evidence standard. After both core databases are technically closed, the project can assemble the Development Process Document and build-from-template tutorial without conflating those documentation deliverables with runtime PASS.
