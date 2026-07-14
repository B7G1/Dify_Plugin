# Phase 10.0 — Original Plugin Contract Freeze and Correct Reproduction Blueprint

- Date: 2026-07-13 (America/Chicago)
- Phase: Phase 10.0 — Base Plugin Reproduction
- Status: PASS / DESIGN_AND_CONTRACT_FREEZE_ONLY
- Database: MySQL, Oracle, Oracle11g, PostgreSQL, MSSQL; extensions DM8 and KingbaseES
- Scope: read-only reference-package re-extraction, formal contracts, architecture and tutorial-route freeze
- Source commit at start: `d29247494f9a48c6dc79de8ea8e9e31ae2cfa2ca`
- Canonical report: this file
- Machine evidence: [`reports/verification/2026-07-13/phase10_0_final_gate.json`](../../../verification/2026-07-13/phase10_0_final_gate.json)
- Logs: [`reports/logs/2026-07-13/Phase10_Base_Reproduction/`](../../../logs/2026-07-13/Phase10_Base_Reproduction/)
- Security: reference artifact is LOCAL_ONLY / NOT_TRACKED_BY_GIT / REDISTRIBUTION_NOT_ASSUMED

## 1. Executive Summary

Phase 10.0 freezes the target before implementation. The reference artifact was rehashed and directly read; its five original database options, nine Tool parameters, UI labels, two output modes, drivers, and Oracle11g thick-client call are recorded in versioned machine-readable contracts. No Provider, Tool, Adapter, dialect, formatter, requirements, or runtime package was changed.

## 2. Advisor Requirement Confirmation

The required baseline is Oracle-installable/queryable reproduction plus query, parameter, output, Workflow, UI, and installable-runtime parity for all five original databases. DM8 and KingbaseES remain additive extensions, not substitutes.

## 3. Final Delivery Contract Reference

[`PROJECT_DELIVERY_CONTRACT.md`](../../PROJECT_DELIVERY_CONTRACT.md) now normatively names the five original databases, six parity categories, the security exception, and the correct tutorial route. DM8/KingbaseES final offline evidence requirements are unchanged.

## 4. Scope and Non-Claims

This phase is `ANALYSIS / CONTRACT_FREEZE / ARCHITECTURE_DESIGN / REPRODUCTION_BLUEPRINT / NO_PRODUCTION_CODE_CHANGE`. It does not claim original-base reproduction, Oracle or Oracle11g PASS, legacy Workflow migration PASS, DM8 final delivery, seven-database regression, or final project delivery.

## 5. Git Baseline and Protected State

The start branch was `feature/kingbasees-adapter`; HEAD exactly matched expected `d292474`. The pre-existing dirty worktree includes protected interactive-map, analysis, archive, environment, SQL Server probe, and schema-test paths. No destructive Git operation, broad staging, or change to those paths was used.

## 6. Original Artifact Identity

The local reference file is `junjiem-db_query_0.0.11-offline.difypkg` (the supplied name with `(1)` is an identity alias). It is 73,095,087 bytes; ZIP integrity passed; SHA-256 was recomputed as `6619DB2611D25C685F8CA4F565F86E972A0EBD25894464EF911AEA09C77F1560`.

## 7. Mandatory Five-Database Scope

Exact legacy option order: `mysql`, `oracle`, `oracle11g`, `postgresql`, `mssql`. SQL Server has the dual position `ORIGINAL_BASE_PLUGIN_REQUIRED_DATABASE` and `OPTIONAL_MODERN_PROVIDER_COMPATIBILITY_PATH`; a legacy Workflow must retain `mssql`.

## 8. DM8 and KingbaseES Extension Scope

`dm8` and `kingbasees` are stable additive targets after the original baseline. Their established technical evidence is retained, but it cannot close the original-base reproduction gate.

## 9. UI Contract

Directly extracted UI facts are frozen in [`original_plugin_ui_contract.json`](../../../contracts/original_plugin_ui_contract.json): plugin label `Database Query` / `数据库查询`, Tool label `SQL Query` / `SQL查询`, descriptions, icon `icon.svg`, and provider/tool identifiers. UI parity does not permit copying the original author, package identifier, version, copyright, or notice. Installed Dify node-selector rendering remains explicitly `UNKNOWN` because no disposable tenant installation was performed.

## 10. Parameter Contract

The required order is `db_type`, `db_host`, `db_port`, `db_username`, `db_password`, `db_name`, `db_properties`, `query_sql`, `output_format`. Raw YAML plus normalized labels, descriptions, types, forms, required/default values, options, YAML order, and absent min/max/placeholder declarations are frozen in [`original_plugin_parameter_contract.json`](../../../contracts/original_plugin_parameter_contract.json). Runtime variable-widget behavior is `UNKNOWN_FROM_STATIC_YAML`, not guessed.

## 11. Output Contract

The reference defaults to `legacy_markdown`; `legacy_json_records` returns exactly `{ "records": [object, ...] }`; modern output remains a separate `modern_structured_json` mode with `columns`, `rows`, `row_count`, `truncated`, `max_rows`, `database_type`, and `execution_time_ms`. Legacy NULL is `""`; modern NULL is `null`. The audited original runtime provides an exact Markdown `SELECT 1` golden sample and real JSON fixture samples. The broader Markdown matrix is `PENDING_FIXTURE_CAPTURE`, rather than invented.

## 12. Query Functional Contract

Every original database has a separately frozen driver, URL route, smoke query, runtime status, and gap: MySQL `mysql+pymysql`, Oracle `oracle+oracledb`, Oracle11g `oracle+oracledb` plus native client, PostgreSQL `postgresql+psycopg2`, MSSQL `mssql+pymssql`. The future gate covers SELECT 1, fixtures, Unicode, NULL, numeric, date/timestamp, schema/owner read, empty results, aggregate, ORDER BY, properties, and database-specific SQL.

## 13. SQL Server Dual Positioning

The compatibility layer maps legacy `mssql` to `SQLServerAdapter`; current `sqlserver` remains the modern-provider path. Neither name is allowed to silently overwrite the other in exported Workflow migration.

## 14. Oracle Route Analysis

`ORACLE_IMPLEMENTATION_ROUTE_CONDITIONAL`: source confirms `oracledb==2.2.1` and `oracle+oracledb`; Python-oracledb thin is the primary candidate for modern Oracle, with `oracle+oracledb` as SQLAlchemy integration. Real server/version, offline wheel inspection, Dify runtime, and query evidence remain required before selection becomes PASS.

## 15. Oracle11g Route Analysis

`ORACLE11G_IMPLEMENTATION_ROUTE_CONDITIONAL`: the original code calls `oracledb.init_oracle_client()`, making thick mode with a compatible Oracle Instant Client the compatibility candidate. The required Client media/license, Linux amd64 runtime libraries, server, and query fixture are absent; modern Oracle must not stand in for Oracle11g.

## 16. Workflow Migration Contract

Migration means retaining all nine fields and bindings, `mssql`, output-format semantics, and downstream Markdown/`records` consumers without manual credential re-entry or graph rewiring. The recommended implementation is a legacy-compatible Tool plus a migration utility for exported DSL. In-place original identity is rejected because it would impersonate the original publisher. The original exported DSL is not available, so a controlled equivalent fixture is required later.

## 17. Legacy-Compatible Tool Design

The future Tool accepts inline credentials and the original nine fields, maps only legacy values inside the compatibility layer, and exposes the two legacy formatters. It must redact credentials and use the shared safe core.

## 18. Modern Tool Preservation

The existing Provider-based Tool remains separate: provider credentials plus `sql`, `max_rows`, `timeout_seconds`, `readonly`, and modern structured JSON. Its preserved security and operational improvements are not overwritten by legacy behavior.

## 19. Shared Secure Core Architecture

Both Tools will share credential normalization, secret redaction, read-only validation, connection lifecycle, adapter/dialect registry, result normalization, and formatter-mode dispatch. Target mappings are frozen in [`final_reproduction_architecture.json`](../../../contracts/final_reproduction_architecture.json).

## 20. Security Hardening Boundary

`NORMAL_READ_QUERY_PARITY_REQUIRED`; `SECURITY_VULNERABILITY_PARITY_FORBIDDEN`. Credentialed URLs/password logs, raw database errors, CTE DML, SELECT INTO, INTO OUTFILE, FOR UPDATE, multi-statements, and resource leaks stay blocked. Rejecting a safe normal query remains a compatibility failure.

## 21. Machine-Readable Contracts

The seven contracts live under [`reports/contracts/`](../../../contracts/): UI, parameters, output, database scope/routes, Workflow migration, architecture, and correct reproduction sequence. Each records schema version, source artifact/hash, source files/raw values, normalized fields, validation status, unknowns, and evidence references.

## 22. Current-to-Target Gap Matrix

| Scope | Current state | Target | Blocking gap | Next phase |
| --- | --- | --- | --- | --- |
| MySQL/PostgreSQL query | PASS | legacy full parity | UI/parameters/output/Workflow | 10.1/10.2 |
| SQL Server query | PASS | `mssql` full parity | legacy option/UI/Workflow | 10.1/10.2 |
| Oracle | not completed | installable/queryable | full runtime and Adapter | 10.3 |
| Oracle11g | blocked | installable/queryable | Client/runtime | 10.4 |
| Legacy Markdown/JSON/UI/Workflow | missing | exact compatibility | implementation | 10.1 |
| DM8 | functional pass | final offline delivery | later closure | 11 |
| KingbaseES | technical pass | retain/regress | non-blocking now | 12 |

## 23. Final Correct Reproduction Sequence

`FINAL_CORRECT_REPRODUCTION_SEQUENCE`: verify reference artifact; read-only unpack; freeze contracts; confirm the five original databases; confirm extensions; design dual Tool/shared core; prepare legal dependencies and seven databases; implement secure core; implement the five original adapters; validate legacy behavior; add DM8; add KingbaseES; close offline package, installation, and evidence.

## 24. Development History Classification

`DEVELOPMENT_HISTORY_REQUIRED`: the early two-database assumption, modern Provider-first architecture, late original-UI audit, SQL Server reclassification, Oracle scope correction, and the decision to add a compatibility layer rather than discard secure work.

## 25. Tutorial Required Steps

`TUTORIAL_REQUIRED`: source artifact audit first; contract freeze; dual Tool/shared-core design; early dependency plan; per-database implementation and validation; offline package and installed final checks.

## 26. Tutorial Excluded Detours

`TUTORIAL_EXCLUDED_DETOUR`: two-database-first implementation, incompatible-parameter retrofit, modern-JSON-only retrofit, Markdown omission, SQL Server as purely optional, and any temporary overlay route.

## 27. Delivery Contract Changes

The normative contract gained §1.2 only: the exact five-database scope, six parity requirements, security-hardening exception, and tutorial-route rule. It does not remove or weaken the three final deliverables or the DM8/KingbaseES standards.

## 28. Commands Executed

```powershell
git branch --show-current; git rev-parse HEAD; git status --short; git diff --check
python -m py_compile db_query_extended\verification\phase10_contract_gate.py
python db_query_extended\verification\phase10_contract_gate.py --write-contracts
```

## 29. Files Created or Modified

Created: seven contract JSON files, `phase10_contract_gate.py`, eleven Phase 10 verification JSON files, and the redacted command log. Modified: `PROJECT_DELIVERY_CONTRACT.md` and `REPORT_MAP.md`. No production-plugin file changed.

## 30. Evidence and Logs

Evidence is [`reports/verification/2026-07-13/phase10_0_*.json`](../../../verification/2026-07-13/); the raw, secret-free command result is [`phase10_0_contract_gate.log`](../../../logs/2026-07-13/Phase10_Base_Reproduction/phase10_0_contract_gate.log).

## 31. Git State

Start matched `d292474`; all existing dirty paths remain protected. Only exact Phase 10 contract, verification, log, and report paths are eligible for staging.

## 32. Final Decision

```text
PHASE_STATUS: PHASE_10_0_PASS
ALLOWED_CONCLUSIONS:
ORIGINAL_PLUGIN_CONTRACT_FROZEN
MANDATORY_DATABASE_SCOPE_FROZEN
LEGACY_UI_CONTRACT_FROZEN
LEGACY_PARAMETER_CONTRACT_FROZEN
LEGACY_OUTPUT_CONTRACT_FROZEN
WORKFLOW_MIGRATION_CONTRACT_FROZEN
FINAL_REPRODUCTION_ARCHITECTURE_FROZEN
FINAL_CORRECT_REPRODUCTION_SEQUENCE_FROZEN
NOT_YET_PROVEN:
ORIGINAL_BASE_PLUGIN_REPRODUCTION_CONFIRMED
ORACLE_REPRODUCTION_PASS
ORACLE11G_REPRODUCTION_PASS
LEGACY_WORKFLOW_MIGRATION_PASS
DM8_FINAL_DELIVERY_PASS
FINAL_SEVEN_DATABASE_MATRIX_PASS
FINAL_PROJECT_DELIVERY_PASS
```

## 33. Next Phase

`Phase 10.1 — Legacy-Compatible Tool, Output and Workflow Migration Implementation` may now implement the frozen surface while retaining the modern Tool and the shared secure core.
