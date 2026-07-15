# Phase 10.3 — Legacy-Compatible Architecture Mapping

- Date: 2026-07-15
- Phase: Phase 10.3 — Legacy-Compatible Architecture Mapping
- Status: PASS
- Database: Design scope: MySQL, PostgreSQL, SQL Server; Oracle/Oracle11g declared-but-unsupported; no DM8 or KingbaseES runtime work
- Scope: Freeze the Legacy/Modern Tool architecture and Phase 10.4 implementation boundary without changing product behavior, deployed plugins, or Workflows.
- Source commit: `26a5219` (working tree contains this phase's uncommitted documentation/evidence only, plus protected unrelated user changes)
- Runtime: Static source/YAML/DSL verification; no database, Dify API, installed plugin, or Workflow invocation
- Canonical path: `reports/documentation/2026-07-15/Phase10_Base_Reproduction/phase10_3_legacy_compatible_architecture_mapping.md`
- Machine evidence: `reports/verification/2026-07-15/phase10_3_legacy_compatible_architecture_mapping.json`
- Logs: NOT_APPLICABLE
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / NO_CREDENTIALS

## Executive Summary

Phase 10.3 freezes two explicit Tool contracts over one shared execution core. It does not merge UI contracts, does not change the known-good Workflows, and does not claim new database support. The static Gate passed 12 checks against the current source, provider YAML, Tool YAML, and formal JSON DSL asset.

The precise modern Tool name is `db_query_extended`; `database_query` is not an implementation identifier in this repository. The Legacy Tool is `legacy_database_query`.

## Goal and Acceptance Boundary

The goal is to retain the original plugin's nine-parameter UI, five declared database values, Markdown table, `{"records": [...]}` JSON shape, and Start → Tool → Template → Output topology while reusing the modern adapter registry, connection lifecycle, timeout, row-limit, serialization, and error-cleaning core.

This phase is a design freeze. It does **not** implement the three explicitly identified Phase 10.4 changes, run Oracle/Oracle11g, add DM8/KingbaseES behavior, re-import DSL, or change already-published apps.

## Frozen Architecture

```text
Legacy Tool: legacy_database_query
  -> Legacy Input Mapper
  -> Legacy SQL Policy
  -> Shared Execution Core
  -> Legacy Output Formatter

Modern Tool: db_query_extended
  -> Provider Credential Mapper
  -> Modern Read-only Policy
  -> Shared Execution Core
  -> Modern Structured Formatter
```

The shared execution core is `utils.database.execute_read_only_query`, which selects the adapter through the registry and returns normalized result data. Only the execution result and sanitized internal exceptions cross the shared boundary.

The following must remain separate:

| Boundary | Legacy | Modern |
| --- | --- | --- |
| Entry identity | `legacy_database_query` | `db_query_extended` |
| Connection source | nine inline Tool parameters | Provider credential schema |
| SQL input | `query_sql` | `sql` |
| Output JSON | exactly `records` | structured envelope with `columns`, `rows`, `row_count`, `truncated`, `max_rows` and modern metadata |
| Markdown | GitHub table is part of contract | not a compatibility requirement |
| Dify workflow | legacy Start/Tool/Template/Output topology | independent modern callers |

## 1. Dual-entry Contract Freeze

`legacy_database_query` keeps the original ordered parameter list:

```text
db_type, db_host, db_port, db_username, db_password,
db_name, db_properties, query_sql, output_format
```

It keeps the declared values `mysql`, `oracle`, `oracle11g`, `postgresql`, and `mssql`; its default format is Markdown. `db_query_extended` remains a different, Provider-credential-backed Tool with `sql`, `max_rows`, `timeout_seconds`, `readonly`, and `output_format`.

Both Tools remain registered by one project-owned provider. This is two externally stable contracts, not one polymorphic schema with conditional fields.

## 2. Legacy-to-Internal Mapping

| Legacy parameter | Internal target | Frozen mapping |
| --- | --- | --- |
| `db_type` | adapter key | `mysql → mysql`, `postgresql → postgresql`, `mssql → sqlserver` |
| `db_host` | `host` | direct, normalized |
| `db_port` | `port` | direct, normalized/defaulted by internal validation |
| `db_username` | `username` | direct |
| `db_password` | `password` | direct, never logged or persisted in evidence |
| `db_name` | `database` | direct; legacy permits it to be absent |
| `db_properties` | selected internal options | parse as query pairs; only `schema`, `charset`, `ssl_mode` may enter config |
| `query_sql` | `sql` | legacy SQL-policy input |
| `output_format` | formatter selection | `markdown → legacy Markdown`, `json → {"records": [...]}` |

`oracle` and `oracle11g` deliberately do not enter the adapter registry: both are `UNSUPPORTED_DECLARED_LEGACY`. This preserves the original visible options without inventing a runtime claim. `mssql` is a legacy name only; the internal key is permanently `sqlserver`.

### `db_properties` policy

The current mapper already parses query-pair syntax before assigning `schema`, `charset`, and `ssl_mode`. Phase 10.4 must make the policy explicit: unsupported keys or duplicate keys are rejected rather than silently discarded. Raw properties never become Modern Provider credentials or arbitrary SQLAlchemy URL fragments.

## 3. Shared Core and Security Boundary

Both paths use the same short-lived engine lifecycle, adapter selection, timeout execution, row acquisition, result normalization, serialization, and cleanup. Legacy and Modern perform their own mapping and formatting before/after this core.

| Behavior | Legacy decision | Modern decision |
| --- | --- | --- |
| SQL policy | target is exactly one original-style `SELECT` statement | current modern read-only policy |
| Max rows | internal compatibility ceiling; no tenth Legacy parameter | explicit `max_rows` |
| Timeout | internal compatibility default; no tenth Legacy parameter | explicit `timeout_seconds` |
| Success Markdown | required GitHub table | not a compatibility promise |
| Success JSON | only `records` | modern structured envelope |
| Errors | original runtime exception path, with sanitized text | structured sanitized error envelope |
| Security | safety strengthening must be called an enhancement, never original behavior | native modern safety contract |

The original Tool only accepted one `SELECT`, while the current Legacy implementation routes through the modern `ReadOnlyValidator`; the error branch currently emits a JSON error message. Neither discrepancy is hidden: both are Phase 10.4 implementation requirements below. They do not invalidate the design freeze because this phase makes the target behavior and migration boundary explicit.

## 4. Workflow and DSL Persistence

The Legacy Workflow topology remains Start → SQL QUERY → Template → Output. The passed JSON DSL is the persistence baseline:

```yaml
tool_parameters:
  output_format:
    type: constant
    value: json
```

`tool_configurations.output_format` alone is never treated as execution proof. The stable DSL assets and their hashes are retained by Phase 10.2.2; this phase only references them and does not regenerate, import, or publish them.

## 5. Phase 10.4 Required Changes

These are implementation work, intentionally not performed now:

1. Add Legacy-only SQL validation that preserves the original single-`SELECT` acceptance boundary before entering the shared core.
2. Change the Legacy Tool error branch to retain the Dify exception path while exposing only sanitized text; do not replace original-compatible failure flow with a new structured Legacy JSON error contract.
3. Reject unknown or duplicate `db_properties` keys explicitly; preserve only the three mapped options.

No Oracle/Oracle11g adapter, DM8 extension, KingbaseES extension, database driver, package, Provider, or Workflow change is included in that list.

## Verification Results

[`phase10_3_legacy_compatible_architecture_mapping.json`](../../../verification/2026-07-15/phase10_3_legacy_compatible_architecture_mapping.json) records 12 PASS checks for:

- distinct Tool identities and registrations;
- exact Legacy parameter order and five database values;
- exact Modern parameter contract;
- `mssql → sqlserver` mapping and controlled Oracle paths;
- shared `execute_read_only_query` core;
- Legacy/Modern output isolation;
- parsed property boundary; and
- persisted `tool_parameters.output_format=json` in the final JSON DSL.

The next implementation Gate must test the following matrix: nine parameter order, all Legacy mappings, controlled Oracle/Oracle11g behavior, Markdown table, JSON `records` only, modern-envelope isolation, persisted JSON Tool parameter, sanitized Legacy exception path, and Legacy/Modern non-regression.

## Commands Executed

From PowerShell in `E:\Dify_Plugin`:

```powershell
python db_query_extended\verification\phase10_3_legacy_architecture_gate.py `
  --output reports\verification\2026-07-15\phase10_3_legacy_compatible_architecture_mapping.json
```

Expected result: exit code 0 with 12 checks and zero failures. A failure indicates source, Tool schema, provider registration, or archived JSON DSL no longer matches this architecture freeze; it does not authorize a silent contract change.

## Files Changed

| File | Change |
| --- | --- |
| `db_query_extended/verification/phase10_3_legacy_architecture_gate.py` | new, static architecture verification only |
| this report | new canonical human architecture decision record |
| `reports/verification/2026-07-15/phase10_3_legacy_compatible_architecture_mapping.json` | generated Gate evidence |
| `reports/verification/2026-07-15/phase10_3_report_structure_validation.json` | report-structure evidence |
| `reports/REPORT_MAP.md` | adds the canonical Phase 10.3 index entry |

Product source and runtime configuration are unchanged.

## Final Decision

```text
PHASE_STATUS: PASS
ALLOWED_CONCLUSIONS:
  - LEGACY_AND_MODERN_TOOL_BOUNDARIES_FROZEN
  - LEGACY_TO_INTERNAL_MAPPING_FROZEN
  - LEGACY_OUTPUT_AND_MODERN_OUTPUT_ISOLATION_FROZEN
  - PHASE_10_4_IMPLEMENTATION_SEQUENCE_FROZEN
NOT_YET_PROVEN:
  - ORACLE_RUNTIME_PASS
  - ORACLE11G_RUNTIME_PASS
  - DM8_NEW_RUNTIME_PASS
  - KINGBASEES_NEW_RUNTIME_PASS
  - PHASE_10_4_IMPLEMENTATION_PASS
  - FINAL_PROJECT_DELIVERY_PASS
FINAL_DELIVERY_IMPACT: development-history and tutorial-relevant architecture record only; no final delivery gate is closed.
NEXT_PHASE: Phase 10.4 — Legacy-Compatible Architecture Implementation
```

### Record classification

- `TUTORIAL_REQUIRED`: two Tool contracts, mapping boundary, and JSON DSL persistence rule.
- `TUTORIAL_REFERENCE`: adapter registry and shared execution core call direction.
- `DEVELOPMENT_HISTORY_ONLY`: why Legacy SQL/error/property behavior must not silently inherit modern semantics.
- `EVIDENCE_ONLY`: static Gate JSON and archived DSL hash reference.
- `TEMPORARY`: terminal output and local working-tree status.
