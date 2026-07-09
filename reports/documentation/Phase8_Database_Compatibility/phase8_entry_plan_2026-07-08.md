# Phase 8 Entry Plan

Date: 2026-07-08  
Phase: `Phase 8 - Additional Database Compatibility Development`

## 1. Phase 8 goal

Extend database compatibility on top of the current frozen baseline without breaking:

- MySQL validated path;
- PostgreSQL validated path;
- DM8 validated path;
- read-only SQL safety;
- JSON output contract;
- existing verification expectations.

## 2. Current baseline

Current baseline evidence in repo:

- Provider: `6 PASS / 0 FAIL / 0 SKIP`
- Tool: `27 PASS / 0 FAIL / 0 SKIP`
- Workflow: `12 PASS / 0 FAIL / 0 SKIP`
- Total: `45 PASS / 0 FAIL / 0 SKIP`

Primary evidence:

- `reports/verification/2026-07-07/phase7_3b_verify_all/summary.json`
- `reports/verification/2026-07-07/phase7_3b_workflow_result.json`

## 3. Protected paths

Phase 8 must not casually change:

- MySQL / PostgreSQL existing behavior;
- DM8 validated execution path;
- `verify_all.ps1` baseline contract unless the change is additive and regression-safe;
- existing Tool success/error JSON semantics.

## 4. Candidate database priority

Recommended order right now:

1. SQL Server
2. KingbaseES
3. DM8 follow-up only where adapter hardening is actually needed

Why:

- SQL Server already has local test environment material under `local_test_db/sqlserver/`;
- KingbaseES already has preview adapter structure, but runtime feasibility still looks incomplete;
- DM8 already has substantial evidence, so it is not the first place to spend new expansion effort.

## 5. Adapter interface check

The repository already has an adapter abstraction:

- `utils/adapters/base.py`
- `utils/adapters/__init__.py`
- concrete adapters for `mysql`, `postgresql`, `dm`, `kingbasees`

Current extension shape is small and usable:

- one adapter module per `database_type`;
- URL builder;
- connect args builder;
- session configuration hook;
- default query execution path shared in base class.

This means Phase 8 should extend the existing adapter surface, not invent a new framework.

## 6. What each database needs

For any new `database_type`, Phase 8 should minimally define:

1. provider option in `provider/db_query_extended.yaml`;
2. adapter module under `utils/adapters/`;
3. any driver runtime gate under `utils/drivers/` if needed;
4. runtime dependency in `requirements.txt` and packaged wheels if the driver is accepted;
5. local fixture environment under `local_test_db/`;
6. provider validation coverage;
7. tool query validation coverage;
8. workflow/API validation path if the database reaches that stage;
9. documentation and rollback notes.

## 7. Evidence required for acceptance

Each database should eventually produce:

- local environment preparation evidence;
- provider credential validation evidence;
- tool query pass/fail evidence;
- read-only rejection evidence;
- workflow execution evidence if integrated into Dify workflow;
- final dated report under `reports/documentation/`.

## 8. Risk and rollback strategy

Main risks:

- driver availability for Python 3.12 Linux amd64 runtime;
- SQLAlchemy dialect mismatch;
- schema/search_path differences;
- timeout/session-setting differences;
- breaking existing validation assumptions in shared code.

Rollback rule:

- additive changes only at first;
- one database at a time;
- if a new database destabilizes shared logic, revert that narrow change rather than broadening the abstraction.

## 9. First development recommendation

First recommended target: SQL Server.

Reason:

- the repo already has independent SQL Server environment assets;
- it uses a mainstream dialect/driver path compared with the still-blocked KingbaseES runtime story;
- it is a cleaner Phase 8 expansion target than revisiting DM8 first.
