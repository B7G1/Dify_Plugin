# Phase 10 Dependency and Packaging Readiness

Date: 2026-07-02  
Decision: **BLOCKED — do not build v1.1.0 yet**

Latest automated result: `7 PASS / 0 FAIL / 0 SKIP / 5 BLOCKED`.

## Why this is the next gate

The KingbaseES Adapter, Driver abstraction, Provider Preview, Mock verification, Workflow specification, and acceptance orchestration are already prepared. The highest remaining non-database risk is releasing a package that exposes KingbaseES but lacks an approved Python 3.12 driver, SQLAlchemy dialect, native client closure, or redistribution permission.

This audit is additive and read-only with respect to package artifacts. It does not install, download, build, remove, or rewrite a `.difypkg`.

## Current consistency

- Manifest remains plugin `0.1.1`, Python `3.12`, architecture `amd64`.
- Requirements retain the accepted v1 direct dependency pins.
- Offline wheels include Python 3.12 Linux amd64-compatible direct dependencies for MySQL, PostgreSQL, and DM8.
- Requirements intentionally do not declare `ksycopg2` or a Kingbase dialect before approval.
- The canonical v1 artifact remains `db_query_extended-0.1.1-dm8-linux-amd64.difypkg` with SHA-256 `CEE3B0D7D54ECF1171E78739FF01C12D204F9B0CCCF7627D51AFAA69631A142B`.
- Other `.difypkg` files are historical, third-party, test, or development artifacts and must not be selected for a release.

## Blocking requirements for v1.1

1. approved `ksycopg2` CPython 3.12 Linux x86_64 wheel copied into the offline wheel set;
2. a Kingbase SQLAlchemy dialect proven against SQLAlchemy 2.0.51;
3. `libkci`/native dependency inventory and successful `ldd` closure in plugin-daemon;
4. driver/dialect/native library/image/license redistribution review;
5. real database, Provider, Workflow, API, and complete v1 regression acceptance;
6. only then: version bump, requirements update, package build, clean install, checksum, and release evidence.

## Automated check

Run:

```powershell
Set-Location E:\Dify_Plugin\db_query_extended
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verification\verify_phase10_packaging.ps1
```

Machine evidence: `reports/verification/2026-07-02/phase10_kingbasees/packaging_readiness.json`.

BLOCKED is the correct result until official Kingbase artifacts and licensing arrive. It must never be converted to PASS by a mock or an unverified third-party image.
