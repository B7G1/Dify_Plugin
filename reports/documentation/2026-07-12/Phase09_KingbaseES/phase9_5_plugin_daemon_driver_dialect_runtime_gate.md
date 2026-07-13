# Phase 9.5 — KingbaseES Official Driver and SQLAlchemy Runtime Gate

- Date: 2026-07-12
- Phase: Phase 9.5
- Status: PASS
- Database: KingbaseES
- Scope: Official-maintainer driver installation/import and DB-API/SQLAlchemy runtime feasibility in the real Dify plugin-daemon Python 3.12 runtime
- Source commit: `0787d42`
- Runtime: `dify-plugin_daemon-1`, Python 3.12.3, Linux x86_64/glibc 2.39, SQLAlchemy 2.0.51
- Canonical path: `reports/documentation/2026-07-12/Phase09_KingbaseES/phase9_5_plugin_daemon_driver_dialect_runtime_gate.md`
- Machine evidence: `reports/verification/2026-07-12/kingbasees_phase9_5_*.json`
- Logs: `reports/logs/2026-07-12/Phase09_KingbaseES/`
- Supersedes: Phase 10.1 conditional driver-feasibility conclusions where current real evidence now exists
- Security classification: Internal engineering; credentials and license contents excluded

## Executive Summary

Phase 9.5 is `PASS`.

The Kingbase-maintained `ksycopg2 2.9.1` CPython 3.12 Linux x86_64 wheel was downloaded from PyPI, rehashed, installed into an isolated `/tmp` target in the real running Dify plugin-daemon, and imported successfully. Its bundled `libkci.so.5` and native extension have no missing `ldd` dependencies.

DB-API connected to the preserved real KingbaseES V009R001C010 server and passed authentication, `SELECT 1`, Unicode, pyformat parameter binding, and connection close. No official SQLAlchemy dialect was present in the wheel, ISO, or registered entry points. A single-process compatibility shim using SQLAlchemy 2.0.51 created an Engine, connected to the real server, passed `SELECT 1`, Unicode and named binding, then closed and disposed cleanly.

This proves driver and SQLAlchemy runtime feasibility. It is not a formal Adapter, Provider, Tool, Workflow, packaging, redistribution, or end-to-end plugin PASS.

## Goal and Acceptance Boundary

The gate asked whether an auditable Kingbase driver can install and import in the real plugin-daemon Python 3.12 runtime and reach the real Phase 9.4 KingbaseES server through DB-API and SQLAlchemy 2.0.51.

It did not authorize product-code, requirements, manifest, Provider, Tool, Workflow, `.difypkg`, or cross-database regression changes.

## Baseline

- Branch: `feature/kingbasees-adapter`
- Baseline commit: `0787d42 docs: establish reporting standard and canonicalize reports`
- Phase 9.4 server/image/runtime gate: PASS
- Preserved server container: `dify-plugin-phase94-kingbase`
- Preserved volume: `dify-plugin-phase94-kingbase-data`
- Real plugin-daemon auto-discovered as `dify-plugin_daemon-1`, image `langgenius/dify-plugin-daemon:0.5.3-local`
- All unrelated dirty/untracked files were left untouched.

## Environment

| Item | Measured value |
| --- | --- |
| plugin-daemon | `dify-plugin_daemon-1`, running on `dify_default` |
| Python | `/usr/bin/python3`, 3.12.3 |
| OS/architecture | Linux x86_64, Ubuntu base, glibc 2.39 |
| global SQLAlchemy | not installed in base runtime |
| isolated SQLAlchemy | 2.0.51 |
| KingbaseES | V009R001C010 at `host.docker.internal:54321` |
| database/user type | `kingbase`; preserved Phase 9.4 local test administrator |
| credential source | server container environment, passed transiently and redacted |

The KingbaseES container was found exited after a Docker Desktop interruption. It was restarted without rebuild, replacement, volume deletion, or configuration change and became ready on the second poll.

## Driver provenance and inventory

Selected artifact:

`ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl`

Classification: `OFFICIAL_MAINTAINER_DISTRIBUTION`.

Evidence:

- PyPI project metadata identifies the author as `Kingbase`.
- The package description identifies it as the KingbaseES Python interface and points to Kingbase V9 documentation.
- Kingbase documentation describes installation through PyPI.
- The PyPI-reported SHA-256 and the newly downloaded file hash are identical.

Measured artifact facts:

| Field | Value |
| --- | --- |
| size | 4,423,009 bytes |
| SHA-256 | `59D2D19439FA0D8AE66A7972EF9EF1FE461E84389D50BC3E90C59ABB4962287A` |
| ABI/tag | `cp312-cp312-manylinux1_x86_64` |
| license metadata | LGPL with exceptions |
| native extension | `_ksycopg.cpython-312-x86_64-linux-gnu.so` |
| bundled client | `libkci.so.5` |
| SQLAlchemy dialect | absent |
| SQLAlchemy entry points | absent |

The ignored download remains under `external_assets/kingbasees/incoming`; it was not copied to the formal plugin wheels directory or Git.

## Work Performed

1. Searched the official ISO, server image, formal wheels, caches, prior experiments, and reports.
2. Found no driver/dialect in the ISO or formal wheels; found server-side `libkci.so.5.12` only.
3. Queried current PyPI metadata, downloaded the exact CPython 3.12 wheel, and reverified SHA-256.
4. Copied the wheel plus existing SQLAlchemy 2.0.51, greenlet and typing-extensions wheels to `/tmp/kingbasees_phase95/wheels`.
5. Installed with `pip --no-deps --target /tmp/kingbasees_phase95/site`.
6. Imported the driver from the isolated path and inspected DB-API metadata.
7. Ran `readelf` and `ldd` on the extension and bundled `libkci`.
8. Ran real DB-API queries.
9. Proved the official dialect route absent.
10. Ran an experimental, process-local SQLAlchemy compatibility shim and real queries.

## Commands Executed

Working directory: `E:\Dify_Plugin`; shell: PowerShell.

Representative exact command shapes:

```powershell
Invoke-RestMethod https://pypi.org/pypi/ksycopg2/2.9.1/json
Invoke-WebRequest <PyPI file URL> -OutFile external_assets\kingbasees\incoming\ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl
Get-FileHash <wheel> -Algorithm SHA256

docker cp <wheel> dify-plugin_daemon-1:/tmp/kingbasees_phase95/wheels/
docker exec dify-plugin_daemon-1 /usr/bin/python3 -m pip install --no-deps `
  --target /tmp/kingbasees_phase95/site <local wheels>

docker exec --env PYTHONPATH=/tmp/kingbasees_phase95/site `
  dify-plugin_daemon-1 /usr/bin/python3 /tmp/kingbasees_phase95/driver_import_probe.py

docker exec dify-plugin_daemon-1 /usr/bin/ldd `
  /tmp/kingbasees_phase95/site/ksycopg2/_ksycopg.cpython-312-x86_64-linux-gnu.so

docker exec --env PYTHONPATH=/tmp/kingbasees_phase95/site `
  --env KINGBASE_HOST=host.docker.internal --env KINGBASE_PORT=54321 `
  --env KINGBASE_DATABASE=kingbase --env KINGBASE_USERNAME=<runtime-user> `
  --env KINGBASE_PASSWORD=<runtime-secret> dify-plugin_daemon-1 `
  /usr/bin/python3 /tmp/kingbasees_phase95/runtime_connection_probe.py
```

Secret values were retrieved transiently from the preserved server container and never written to reports or logs.

## Files Changed

Product code changed: none.

Added two isolated experiment probes:

- `experiments/kingbasees/phase9_5/driver_import_probe.py`
- `experiments/kingbasees/phase9_5/runtime_connection_probe.py`

Added this canonical report, five machine JSON files and six redacted raw logs. Updated `reports/REPORT_MAP.md` only for the new canonical entry.

## Driver Import Results

| Gate | Result |
| --- | --- |
| DRIVER_ARTIFACT_PROVENANCE_CONFIRMED | PASS |
| DRIVER_SHA256_VERIFIED | PASS |
| PLUGIN_DAEMON_PYTHON312_INSTALL_PASS | PASS |
| PLUGIN_DAEMON_PYTHON312_IMPORT_PASS | PASS |
| isolated module path | PASS |
| DB-API 2.0 metadata | PASS |

Driver details:

- version: `2.9.1 ... for Python3.12 Kingbase V9`
- `apilevel`: `2.0`
- `threadsafety`: `2`
- `paramstyle`: `pyformat`
- import elapsed: approximately 0.277 seconds

## Native Dependency Results

The extension is ELF64 x86-64 and has `RUNPATH=$ORIGIN`. It resolves `libkci.so.5` from the isolated wheel directory. `ldd` reported zero missing libraries.

Bundled `libkci.so.5`:

- SHA-256: `0A242DDC4FE55728DDD5966D3D158AA9B1BC5DB4D36A9CA651D13177E503A3FF`
- SONAME: `libkci.so.5`
- `ldd` missing count: 0
- observed extension GLIBC requirement: no higher than `GLIBC_2.14`, below runtime glibc 2.39

`libkci` contains a vendor build-time RUNPATH, but all required libraries resolved from the runtime system. No ISO/server client directory was required for import.

## SQLAlchemy Routes

### Route A — official dialect

Result: `NOT_FOUND`.

- no `sqlalchemy.dialects` entry point in the wheel;
- no dialect module in the official ISO or local assets;
- `registry.load("kingbase.ksycopg2")` raised `NoSuchModuleError`;
- no official Engine was created.

This is not a driver failure.

### Route B — isolated compatibility shim

Result: PASS.

The first run reached the database through DB-API but SQLAlchemy initialization failed because the PostgreSQL dialect could not parse `KingbaseES V009R001C010` as a PostgreSQL version string. The minimal process-local shim overrode `_get_server_version_info`, returned the real Kingbase release tuple used by the probe, and supplied `ksycopg2` through `import_dbapi`.

The probe used temporary `psycopg2` namespace aliases only inside its process because SQLAlchemy's PostgreSQL dialect imports those names internally. The aliases disappear when the process exits and are not a formal product design.

SQLAlchemy was not patched or downgraded.

## Verification Results

| Check | DB-API | SQLAlchemy 2.0.51 shim |
| --- | --- | --- |
| real TCP authentication | PASS | PASS |
| `SELECT 1` | `1` | `1` |
| Unicode | `金仓数据库` | `金仓数据库` |
| parameter binding | `参数绑定` using pyformat | `参数绑定` using named bind |
| connection close | PASS | PASS |
| rollback | not required for scalar read | PASS |
| engine dispose | NOT_APPLICABLE | PASS |

No persistent table or write statement was created.

## Decisions

- Driver selected: `ksycopg2 2.9.1`, because the artifact is maintained as Kingbase on the primary registry, matches Python 3.12/Linux x86_64, contains its native client, and passed real import/connection.
- SQLAlchemy remains exactly 2.0.51; downgrading would invalidate the plugin runtime baseline.
- Official dialect route is recorded as absent, not fabricated from PostgreSQL compatibility.
- Route B is accepted only as runtime feasibility evidence. A formal Adapter must replace process-level aliases with a scoped, maintainable Kingbase dialect/DB-API integration.
- The evidence is sufficient to enter Adapter implementation, but not to claim end-to-end KingbaseES plugin support.

## Blockers

Runtime gate blockers: none.

Remaining delivery blockers:

- formal namespaced dialect/Adapter design without global module aliasing;
- redistribution/legal review for the wheel and bundled client;
- formal offline wheel closure and plugin-daemon installation path;
- Provider, Tool, Workflow and regression evidence.

## Abandoned Paths

- Unknown/third-party drivers: rejected; none used.
- Driver from ISO: abandoned because none exists there.
- Official SQLAlchemy dialect: unavailable in inspected artifacts.
- SQLAlchemy downgrade to 1.x: rejected because the required runtime is 2.0.51.
- Persistent/global `sys.modules["psycopg2"]` modification: rejected; aliases were process-local only.
- First shim version: failed at server-version parsing; corrected at the actual SQLAlchemy override point.

## Security and Redaction

No password, connection URL with password, license content, `.env`, API key, token, ISO, Docker tar, wheel, or database data is tracked. Evidence records only credential source and `***REDACTED***`.

## Reproduction Trace

Prerequisites: running preserved KingbaseES server, running real plugin-daemon, ignored verified wheel, and transient credentials.

Expected sequence: verify wheel SHA; isolate-install to `/tmp`; run import probe; require module path under `/tmp`; run `ldd` and require zero missing; run DB-API probe; confirm official dialect result; run shim probe; require scalar, Unicode, binding, close and dispose results.

Failure meaning is stage-specific: artifact mismatch, ABI rejection, import/native dependency failure, network/authentication failure, dialect resolution failure, query mismatch, or cleanup failure. No stage is promoted beyond its measured boundary.

## Git State

Only Phase 9.5 experiment, report, evidence, logs and REPORT_MAP paths are eligible for this independent commit. Existing user changes remain unstaged.

## Final Decision

`PASS`

All Phase 9.5 runtime acceptance items passed. The official dialect was absent, but the allowed isolated compatibility route proved SQLAlchemy 2.0.51 Engine feasibility against the real KingbaseES server.

## Next Step

Proceed to Phase 9.6 — KingbaseES Adapter Implementation. Implement the smallest scoped dialect/Adapter path that removes experimental global aliases, then validate Provider, Tool and Workflow separately.

## Sources

- [PyPI ksycopg2 2.9.1 project](https://pypi.org/project/ksycopg2/2.9.1/)
- [PyPI ksycopg2 2.9.1 machine metadata](https://pypi.org/pypi/ksycopg2/2.9.1/json)
- [KingbaseES V9 documentation](https://help.kingbase.com.cn/v9/index.html)
