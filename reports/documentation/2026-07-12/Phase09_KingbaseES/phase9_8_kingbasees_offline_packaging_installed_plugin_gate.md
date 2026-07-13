# Phase 9.8 — KingbaseES Offline Driver Packaging and Installed Plugin Gate

- Date: 2026-07-12
- Phase: Phase 9.8
- Status: PASS
- Database: KingbaseES
- Scope: Driver provenance, offline dependency closure, candidate package, Dify install/upgrade, installed Provider/Tool, and targeted installed regression
- Source commit: `73ed5f3`
- Runtime: Dify 1.13.3, plugin-daemon 0.5.3-local, Python 3.12.3, Linux amd64, SQLAlchemy 2.0.51, ksycopg2 2.9.1
- Canonical path: `reports/documentation/2026-07-12/Phase09_KingbaseES/phase9_8_kingbasees_offline_packaging_installed_plugin_gate.md`
- Machine evidence: `reports/verification/2026-07-12/kingbasees_phase9_8_*.json`
- Logs: `reports/logs/2026-07-12/Phase09_KingbaseES/phase9_8_*.log`
- Supersedes: NOT_APPLICABLE
- Security classification: INTERNAL / REDACTED / REDISTRIBUTION_REVIEW_PENDING

## Final Delivery Contract Reference

This Phase report is governed by:

`reports/documentation/PROJECT_DELIVERY_CONTRACT.md`

Phase 9.8 PASS is a packaging and installed Provider/Tool gate. It is not Workflow PASS, final KingbaseES end-to-end PASS, or final project delivery completion.

## Executive Summary

Phase 9.8 is `PASS`.

The Kingbase-maintained ksycopg2 2.9.1 wheel was rehashed, audited, pinned, preserved unchanged in the plugin wheel set, and included in a candidate `.difypkg`. A clean Python 3.12 container with `--network none` installed the complete 44-wheel dependency set using only `--no-index --find-links` and imported the plugin source, SQLAlchemy, ksycopg2, and bundled `libkci.so.5` without the Phase 9.5 overlay.

Dify installed and upgraded the real plugin to candidate checksum `bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9`. The installed runtime loaded the package-owned driver and passed real installed Provider, Tool, SQL safety, error redaction, PostgreSQL, Adapter-import, and dialect-isolation checks.

The allowed conclusions are:

```text
KINGBASEES_OFFLINE_DEPENDENCY_CLOSURE_PASS
KINGBASEES_CANDIDATE_PACKAGE_PASS
KINGBASEES_INSTALLED_PROVIDER_PASS
KINGBASEES_INSTALLED_TOOL_PASS
```

Workflow and final end-to-end delivery remain not tested.

## Baseline and Protected State

- branch: `feature/kingbasees-adapter`;
- development baseline: `9179304`;
- packaging implementation: `73ed5f3`;
- portable audit fix: `120772c`;
- installed-gate scripts: `72f28e9`;
- 43 pre-existing modified/untracked user paths were recorded and protected;
- no prune, volume deletion, old-plugin uninstall, database-table installation forgery, or destructive Git command was used;
- preserved KingbaseES container and volume remained in place.

## Existing Packaging Architecture

The project already uses one packaging path:

```text
requirements.txt
-> --no-index / --find-links=./wheels
-> db_query_extended/wheels/
-> dify plugin package
-> .difypkg
-> Dify PluginService / PluginInstaller
-> plugin-daemon local runtime
```

No pyproject or Poetry lock exists. The package command obeys `.difyignore`, includes the wheel directory, and excludes verification, docs, Git metadata, local environments, dist, and build output.

The existing wheel set already contained Dify SDK, SQLAlchemy 2.0.51, greenlet, typing-extensions, PyMySQL, psycopg2-binary, dmPython, dmSQLAlchemy, pymssql, and their transitive dependencies. SQL Server's `pymssql` wheel is the one exceptional tracked wheel; most project wheels and `dist/` artifacts are intentionally Git-ignored. Phase 9.8 follows that policy rather than force-adding another large binary.

## Driver Provenance and Integrity

Selected artifact:

`ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl`

Measured facts:

| Field | Value |
| --- | --- |
| source | Kingbase-maintained distribution published on PyPI |
| local preserved source | `external_assets/kingbasees/incoming/` — LOCAL_ONLY / GIT_IGNORED |
| formal local wheel path | `db_query_extended/wheels/` — GIT_IGNORED / INCLUDED_IN_PACKAGE |
| size | 4,423,009 bytes |
| SHA-256 | `59D2D19439FA0D8AE66A7972EF9EF1FE461E84389D50BC3E90C59ABB4962287A` |
| package/version | ksycopg2 2.9.1 |
| tag | cp312-cp312-manylinux1_x86_64 |
| extension | `_ksycopg.cpython-312-x86_64-linux-gnu.so` |
| bundled client | `ksycopg2/libkci.so.5` |
| libkci SHA-256 | `0A242DDC4FE55728DDD5966D3D158AA9B1BC5DB4D36A9CA651D13177E503A3FF` |
| license metadata | LGPL with exceptions |

`readelf -h`, `readelf -d`, version inventory, and `ldd` were rerun. The extension is ELF64 x86-64, has `$ORIGIN` runtime lookup, resolves the wheel-bundled `libkci.so.5`, and has zero missing shared libraries. Results match Phase 9.5.

Official references used for provenance were the [PyPI ksycopg2 project](https://pypi.org/project/ksycopg2/) and the [KingbaseES Python client guide](https://help.kingbase.com.cn/v8/development/client-interfaces/python/index.html).

## License and Notice Boundary

`db_query_extended/THIRD_PARTY_NOTICES.md` records package, version, origin, SHA-256, copyright holders, bundled native library, notice retention, and review state.

The wheel's original `LICENSE` states LGPL v3-or-later, an OpenSSL linking exception, and a source-form obligation for modified portions. The unchanged wheel and its original LICENSE are included together. No official statement expressly prohibiting this internal candidate was found in the inspected package metadata or vendor Python-client documentation.

This is not legal advice and does not close public redistribution review:

```text
LICENSE_METADATA_RECORDED
NOTICE_INCLUDED
REDISTRIBUTION_REVIEW_PENDING
INTERNAL_CANDIDATE_ALLOWED
```

No KingbaseES server license, trial authorization, external `license.dat`, ISO, Docker image/tar, or database data is in the plugin package.

## Requirements and Offline Closure

Both dependency files now pin:

```text
ksycopg2==2.9.1
```

Candidate dependency inventory:

- wheel count: 44;
- every wheel filename, package, version, size, SHA-256, Python/platform tag, license metadata, source classification, requirement role, inclusion state, and verification state recorded;
- SQLAlchemy 2.0.51, greenlet 3.5.2, typing-extensions 4.15.0, and all direct database drivers present;
- missing dependency count: 0.

Clean-room procedure:

1. created temporary `langgenius/dify-plugin-daemon:0.5.3-local` container;
2. set Docker network mode to `none`;
3. mounted nothing from host site-packages and used no existing venv;
4. extracted the candidate package;
5. ran Python 3.12 pip with `--isolated --no-index --no-cache-dir --find-links` into a fresh target;
6. imported ksycopg2, SQLAlchemy, Dify SDK, plugin database utility, Provider, and Tool;
7. verified `libkci.so.5` and module paths;
8. asserted no `/tmp/kingbasees_phase95` path and no download log lines.

Result: `PASS`.

## Candidate Package

| Field | Value |
| --- | --- |
| version | 0.1.1, unchanged |
| reason version unchanged | prior same-version checksum upgrade path is established; no arbitrary bump required |
| filename | `db_query_extended-0.1.1-kingbasees-candidate.difypkg` |
| local path | `db_query_extended/dist/phase9_8/` — GIT_IGNORED |
| size | 41,232,413 bytes |
| file SHA-256 | `117206A0F0D50FDA0EA7C1895E82BA0151AE0DEE3583B3E914240A0D2985C389` |
| Dify plugin checksum | `bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9` |
| source commit | `73ed5f3` |
| files | 77 |
| wheels | 44 |

The package contains the entrypoint, manifest, Provider/Tool declarations, KingbaseES Adapter/dialect, requirements, third-party notice, and unchanged ksycopg2 wheel. Audit found zero forbidden paths and zero secret hits.

The package contains the driver's own third-party LICENSE inside its wheel and the project notice. It does not contain a KingbaseES server license, external media, `.env`, API token, private key, database dump, verification secret, Git metadata, cache, venv, or Phase 9.5 path.

## Installation Baseline and Rollback

Before installation:

```text
version: 0.1.1
active identifier: li_zijun/db_query_extended:0.1.1@4d1e293d9c5df7a8614e7d5e086a6a8a856a7a76accf835bc18ab6736f84af47
rollback package: release/db_query_extended/phase8_sqlserver_candidate/db_query_extended-0.1.1-sqlserver-candidate.difypkg
rollback package SHA-256: 8A3C8E931DA66E373831B8D1C5F3C77AF1DF33771FEC0719F41BE093DB5E9E20
```

Rollback procedure: upload the preserved previous package through Dify `PluginService.upload_pkg`, then use the returned identifier in the same package install/upgrade manager. The old package and installed runtime were not deleted.

## Dify Installation and Checksum Activation

The real Dify application service path was used:

```text
PluginService.upload_pkg
-> PluginInstaller decode
-> install_from_identifiers
-> install task success
-> PluginInstaller.upgrade_plugin
-> upgrade task success
-> tenant active checksum switched
```

The preserved Dify 1.13.3 API client sends `plugin_unique_identifier`, while plugin-daemon 0.5.3 requires Go binder field `PluginUniqueIdentifier`. This known project-local compatibility issue first caused a 400 decode response. A process-local compatibility patch, previously established by the SQL Server installation work, changed only the request parameter name and retained Dify's decode, permission, install, and upgrade managers.

The first install task succeeded but left the tenant on the old checksum. This is the established install-versus-upgrade distinction. The real package upgrade manager then switched the existing installation without uninstalling it.

Final state:

```text
active identifier: li_zijun/db_query_extended:0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9
install task: success
upgrade task: success
plugin-daemon runtime: ready
```

## Installed Runtime Proof

Installed root:

`/app/storage/cwd/li_zijun/db_query_extended-0.1.1@bb60478dadf46594b3fdbad140b4ec3a21782899ec7a70e67ff9a1e6088430f9`

Installed module paths:

- ksycopg2: `.venv/lib/python3.12/site-packages/ksycopg2/__init__.py` under the installed root;
- libkci: `.venv/lib/python3.12/site-packages/ksycopg2/libkci.so.5` under the installed root;
- SQLAlchemy: `.venv/lib/python3.12/site-packages/sqlalchemy/__init__.py` under the installed root;
- Adapter: installed root `utils/adapters/kingbasees.py`;
- dialect: installed root `utils/dialects/kingbasees.py`.

The runtime process command points to the candidate `.venv/bin/python -m main`. `PYTHONPATH` is empty. Hard assertions proved that neither module paths nor environment use `/tmp/kingbasees_phase95`, `/tmp/kingbasees_phase96`, or `/tmp/kingbasees_phase97`.

## Installed Provider Results

All 9 installed Provider cases passed through `PluginToolManager` and candidate checksum:

- valid `phase97_fixture`, `public`, and empty schema;
- explicit port, explicit timeout, and a real special-character password;
- wrong password, unreachable port, invalid database, invalid schema, and missing host;
- Provider schema includes canonical `kingbasees`;
- public errors contain no password or credentialed URL.

The read-only credential is stored through Dify's `BuiltinToolManageService`, which validates through the installed plugin and persists encrypted credentials. Connection close and Engine disposal follow the already verified common `finally` lifecycle; repeated positive/negative calls and subsequent Tool queries succeeded without leaked or poisoned connections.

## Installed Tool Results

All 14 installed Tool cases passed through `ToolManager.get_tool_runtime` or the same installed dispatch manager:

- `SELECT 1`;
- 12-row fixture read;
- stored Chinese Unicode;
- NULL, NUMERIC, DATE, and TIMESTAMP serialization;
- schema-qualified fixture read;
- `max_rows=5`, `row_count=5`, `truncated=true`;
- empty result, aggregate `84.00`, and descending ORDER BY;
- DML, DDL, and multi-statement rejection;
- bad-auth error redaction;
- successful query immediately after failed authentication, proving runtime/failure cleanup.

The installed response contract retained columns, rows, row_count, truncated, max_rows, database_type, and execution_time_ms. `database_type` was `kingbasees`.

## Installed Targeted Regression

- real PostgreSQL Provider `SELECT 1`: PASS;
- real PostgreSQL Tool `SELECT 1`: PASS;
- Provider options remain MySQL, PostgreSQL, DM8, SQL Server, KingbaseES;
- public Tool declaration preserved;
- MySQL, PostgreSQL, DM8, SQL Server, and KingbaseES Adapter imports: PASS;
- SQL Server remains `OPTIONAL`;
- psycopg2 module identity unchanged after KingbaseES dialect registration;
- `postgresql.psycopg2` dialect identity unchanged.

DM8 full regression was not run or rebuilt because it is outside this package-focused gate and no package import conflict was found.

## Commands Executed

Representative commands from `E:\Dify_Plugin`:

```powershell
Get-FileHash external_assets\kingbasees\incoming\ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl -Algorithm SHA256
Copy-Item <verified-wheel> db_query_extended\wheels\

.\dify-plugin.exe plugin package .\db_query_extended `
  -o db_query_extended\dist\phase9_8\db_query_extended-0.1.1-kingbasees-candidate.difypkg `
  --max-size 100
.\dify-plugin.exe plugin checksum <candidate.difypkg>

docker create --name dify-plugin-phase98-offline --network none `
  --entrypoint /bin/sh langgenius/dify-plugin-daemon:0.5.3-local -c "sleep 3600"
docker exec -e PIP_NO_INDEX=1 -e PIP_NO_CACHE_DIR=1 dify-plugin-phase98-offline `
  /usr/bin/python3 -m pip install --isolated --no-index --no-cache-dir `
  --find-links /phase98/candidate/wheels --target /phase98/site `
  -r /phase98/candidate/requirements.txt

docker exec --workdir /app/api -e PYTHONPATH=/app/api dify-worker-1 `
  /app/api/.venv/bin/python /tmp/kingbasees_phase9_8_installed_gate.py install ...
docker exec --workdir /app/api -e PYTHONPATH=/app/api dify-worker-1 `
  /app/api/.venv/bin/python /tmp/kingbasees_phase9_8_installed_gate.py validate ...
```

Credentials were passed transiently through environment variables and are absent from commands, reports, evidence, and logs.

## Files Changed

Packaging implementation:

- `db_query_extended/requirements.txt`;
- `db_query_extended/requirements.download.txt`;
- `db_query_extended/THIRD_PARTY_NOTICES.md`;
- local ignored `db_query_extended/wheels/ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl`;
- four Phase 9.8 packaging/offline/install/runtime verification scripts.

Local artifact:

- ignored `db_query_extended/dist/phase9_8/db_query_extended-0.1.1-kingbasees-candidate.difypkg`.

Evidence and reporting:

- eight machine JSON files;
- eleven redacted/structured logs;
- this canonical report;
- one REPORT_MAP row.

No manifest version, Adapter behavior, Provider fields, Tool contract, Workflow, external license, server image, or database fixture definition changed.

## Blocker and Abandoned Path Trace

### Audit utility mismatch

- Symptom: plugin-daemon image lacks the `file` command.
- Root cause: audit script assumed a nonessential utility.
- Fix: use required `readelf -h` instead; no package was installed into the base image.
- Validation: native audit PASS.

### Package container format

- Symptom: Python `tarfile` rejected `.difypkg` while Windows tar listed it.
- Root cause: `.difypkg` is ZIP; Windows tar transparently supports ZIP.
- Fix: standard-library `zipfile`.
- Validation: 77 files, 44 wheels, content audit PASS.

### Dify decode parameter

- Symptom: package upload succeeded; decode returned HTTP 400.
- Root cause: Dify 1.13.3 sends snake_case while daemon 0.5.3 expects `PluginUniqueIdentifier`.
- Fix: process-local, previously verified parameter-name compatibility patch.
- Validation: decode 200, install success.

### Install versus active upgrade

- Symptom: install task succeeded but tenant remained on old checksum.
- Root cause: install prepared the package/runtime; it did not replace the existing same-version tenant installation.
- Fix: official `PluginInstaller.upgrade_plugin` path.
- Validation: upgrade success and active candidate checksum match.

Rejected paths:

- runtime PyPI download;
- host pip cache or existing venv as offline proof;
- continued Phase 9.5 overlay use;
- extracting libkci outside its wheel;
- putting server License or media in the plugin;
- deleting the old plugin before install;
- direct Dify installation-table mutation;
- unrecorded binary copy;
- force-adding ignored wheel/package binaries to Git;
- claiming public redistribution review complete.

No Phase 9.8 acceptance blocker remains. `REDISTRIBUTION_REVIEW_PENDING` remains a release-governance boundary, not an internal technical candidate blocker.

## Security and Redaction

Candidate and evidence scans found zero secrets, credentialed URLs, private keys, external licenses/media, database dumps, user Downloads/sandbox paths, or Phase 9.5 overlay references. Deliberate bad-password values appear only inside verification source as synthetic test constants and never as real credentials.

## Reproduction Trace

Starting at `9179304`:

1. verify the preserved wheel's name, size, SHA-256, metadata, LICENSE, extension, libkci, readelf, and ldd results;
2. copy the unchanged verified wheel to the ignored formal wheels directory;
3. pin ksycopg2 2.9.1 and retain the notice;
4. build with the project Dify CLI command;
5. compare package SHA-256 and Dify checksum;
6. run the packaging gate;
7. perform the network-none, no-index clean install and offline probe;
8. record the old identifier and rollback package;
9. use Dify PluginService/PluginInstaller upload, install, and upgrade paths;
10. assert active checksum and installed module paths;
11. rotate the read-only test password only through the installed driver;
12. run installed Provider, Tool, and regression suites.

Failure meanings remain separate: provenance/hash, native closure, no-index dependency closure, package content, Dify upload/decode/install/upgrade, checksum activation, installed import, Provider, Tool, or regression.

## Tutorial Relevance

- requirements, wheels, notice, package build, Dify install/upgrade, Provider/Tool validation: `TUTORIAL_REQUIRED`;
- rollback and checksum activation: `TUTORIAL_REQUIRED`;
- Dify/daemon decode parameter incident: `DEVELOPMENT_HISTORY_ONLY`;
- machine JSON/logs: `EVIDENCE_ONLY`;
- temporary audit/offline containers and `/tmp` harness files: `TEMPORARY`.

## Git State and Final Decision

The wheel and candidate package follow existing ignored-binary policy. Their hashes and manifests are committed as evidence. Exact paths only are eligible for staging; the original 43 user changes remain outside Phase 9.8.

Final decision: `PASS`.

Proceed to Phase 9.9 — Installed KingbaseES Workflow API and End-to-End Gate. Phase 9.8 does not claim Workflow PASS, final end-to-end PASS, or final offline delivery completion.
