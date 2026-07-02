# Git Release Plan — v1.0.0

## Recommendation

```text
Branch: main
Tag: v1.0.0
Release type: annotated Git tag + GitHub Release
```

## Suggested commit

```text
Release v1.0.0

Freeze technical baseline.
DM8 adapter framework completed.
45 PASS / 0 FAIL / 0 SKIP.
Environment Ready.
Public Release READY.
```

## Suggested GitHub Release title

```text
db_query_extended v1.0.0 — Stable Read-only Database Adapter Baseline
```

## GitHub Release Notes

`db_query_extended v1.0.0` is the first completed public baseline of the Dify read-only database query framework.

Highlights:

- Supports MySQL 8.4, PostgreSQL 16, and DM8.
- Provides one stable Provider → Tool → Adapter → JSON contract.
- Includes a published DM8 Workflow and real Workflow API verification.
- Enforces bounded, read-only SQL and rejects dangerous statements before execution.
- Uses persistent PostgreSQL/Weaviate named volumes and a single managed startup entry.
- Passed cold-boot persistence verification with PostgreSQL system identifier `7657369583221227555` unchanged.
- Passed **45 tests / 0 failures / 0 skips**: Provider 6, Tool 27, Workflow 12.
- Includes public architecture, Dashboard, Demo, recovery, release, paper, and presentation material.

Release artifact:

```text
db_query_extended-0.1.1-dm8-linux-amd64.difypkg
SHA-256: CEE3B0D7D54ECF1171E78739FF01C12D204F9B0CCCF7627D51AFAA69631A142B
```

The v1.0.0 lifecycle is completed and frozen. Future database work begins in Phase 10 and evolves as `v1.1.x`.

## Execution guard

Do not use `git add .` in the current dirty worktree. Stage explicit release paths, review every staged deletion and binary, run the secret scan, and obtain owner approval before commit, tag, push, or GitHub Release creation.

This plan performs no Git operation.
