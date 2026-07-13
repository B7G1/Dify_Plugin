# Phase 9.4 - KingbaseES Official Media Intake, Image Load and Runtime Gate

- Date: 2026-07-10
- Phase: Phase 9.4
- Status: PASS
- Database: KingbaseES
- Scope: Official media intake, image load, real server runtime and real SQL
- Source commit: `736902d`
- Runtime: Docker Desktop Linux/amd64; KingbaseES V009R001C010
- Canonical path: `reports/documentation/2026-07-10/Phase09_KingbaseES/phase9_4_official_media_image_runtime_gate.md`
- Machine evidence: `reports/verification/2026-07-10/kingbasees_phase9_4_runtime_gate.json`, `reports/verification/2026-07-10/kingbasees_media_sha256_inventory.csv`
- Logs: Not retained separately
- Supersedes: `reports/documentation/2026-07-09/Phase09_KingbaseES/phase9_official_media_runtime_feasibility.md`
- Security classification: Internal engineering; credentials and license contents excluded

Branch baseline: `feature/kingbasees-adapter`

Commit baseline: `d237e25` (`docs: assess KingbaseES official runtime feasibility`)

This PASS is limited to the KingbaseES server/runtime layer. It is not a driver, SQLAlchemy dialect, Adapter, Provider, Tool, Workflow, offline-package, or full compatibility PASS.

## Scope and safety boundary

- Read `AGENTS.md` before execution.
- Preserved all unrelated modified and untracked files.
- Did not run Docker prune, delete any container/volume, modify the formal Adapter, or change product code.
- Kept official assets under ignored `external_assets/kingbasees/incoming`.
- Wrote only Phase 9.4 evidence/reporting files and the report index.

## Official media intake

All three SHA-256 values were recomputed from the incoming files and matched `reports/verification/2026-07-10/kingbasees_media_sha256_inventory.csv`:

| Asset | Size | SHA-256 result |
| --- | ---: | --- |
| `KingbaseES_V009R001C010B0004_Lin64_install.iso` | 2,974,226,432 bytes | `E1A7477A6DDA1F72EEF5EBE0857D422BE9BFAF2374E1749CB38ED3FD30641E52` — MATCH |
| `KingbaseES_V009R001C010B0004_x86_64_Docker.tar` | 765,955,072 bytes | `16A436608CC204349E510CB136B8FC1FCBDF6874AEE7B204CDAC20A3522282DA` — MATCH |
| `license_4_V009R001C-开发版-365天.dat` | 4,998 bytes | `A3F7D3609CA143B51F6C671D956AE816F60DFE68814263BE8F4E37D8D2A47B9F` — MATCH |

The ISO was inspected read-only with `bsdtar`; it was not mounted and no installer was executed. Its `setup/silent.cfg` exposes `INSTALL_PATH=/opt/Kingbase/ES/V9` and an empty `LICENSE_PATH=` placeholder. No standalone Kingbase license file was found inside the ISO listing.

## Image load and measured metadata

The tar's own `manifest.json`, read before load, declared the tag:

`kingbase_v009r001c010b0004_single_x86:v1`

`docker load` succeeded with that exact tag. `docker image inspect` measured:

- image ID: `sha256:10ba6f33e228ddd6be155e80523afe712be333ee25ccf9f912ee3a31899dc82f`
- architecture / OS: `amd64` / `linux`
- author: `KDBDEV support@kingbase.com.cn`
- entrypoint: `/bin/bash /home/kingbase/docker-entrypoint.sh`
- user: `kingbase`
- working directory: `/home/kingbase/`
- exposed port: `54321/tcp`
- created: `2025-07-02T03:21:54.130758953Z`

Docker was operational as `desktop-linux`; server OS/architecture was `linux/amd64`.

## License path and license evidence

The image entrypoint and filesystem were inspected using disposable `--read-only` containers.

Confirmed image behavior:

1. bundled license starts at `/home/kingbase/install/kingbase/bin/license.dat`;
2. first initialization moves it to `${DATA_DIR}/../etc/license.dat`;
3. with the measured default `DATA_DIR=/home/kingbase/userdata/data`, the persistent path is `/home/kingbase/userdata/etc/license.dat`;
4. the original bin path becomes a symlink to that persistent file.

The image-bundled license parsed as KingbaseES `V009R001C`, enterprise edition, 90-day trial, PostgreSQL/Oracle/MySQL/SQL Server modes. It was used for this gate. On first real initialization its persisted metadata changed from `isFirstRead=1` to `isFirstRead=0` with `baseDate=2026-07-10`; therefore the persisted license SHA-256 changed, as expected, from the pristine image file hash.

The external 365-day development license was mounted only at neutral path `/intake/license.dat:ro` in a disposable read-only container and parsed with the image's own `license_parser_tool`. It identified KingbaseES `V009R001C`, development edition, `validDays=365`, `MaxConnections=10`, and all four DB modes. It was not placed into the runtime path and was not activated. A direct read-only file bind over the initial bin path was not attempted because the entrypoint must move that file during initialization.

## Real runtime gate

Created isolated resources only:

- container: `dify-plugin-phase94-kingbase`
- volume: `dify-plugin-phase94-kingbase-data`
- host mapping: host port `54321 -> container 54321/tcp`; verified through `127.0.0.1:54321`
- image: `kingbase_v009r001c010b0004_single_x86:v1`

The local test administrator password was injected at runtime and is intentionally omitted from repository evidence.

Measured results:

- `initdb`: PASS
- server start: PASS
- `sys_isready -h 127.0.0.1 -p 54321`: accepting connections
- host `Test-NetConnection 127.0.0.1 -Port 54321`: `TcpTestSucceeded=True`
- `select version()`: `KingbaseES V009R001C010`
- `select current_database(), current_user`: `kingbase|system`
- `select 1`: `1`
- authenticated TCP SQL: `127.0.0.1|54321|KingbaseES V009R001C010`
- container restart: PASS; ready on poll attempt 2
- post-restart SQL: `KingbaseES V009R001C010|kingbase|system|1`
- post-restart license path: `/home/kingbase/userdata/etc/license.dat`

The container and volume were left running/preserved for the next evidence layer. No cleanup or prune was performed.

## Command trace

Working directory: `E:\Dify_Plugin`

Shell: PowerShell

Required secret input: local-only administrator password, passed as a process/container environment value and not stored in reports.

Key commands:

```powershell
Import-Csv reports\verification\2026-07-10\kingbasees_media_sha256_inventory.csv |
  ForEach-Object { Get-FileHash -LiteralPath $_.Path -Algorithm SHA256 }

docker version --format '{{json .}}'
tar -xOf external_assets\kingbasees\incoming\KingbaseES_V009R001C010B0004_x86_64_Docker.tar manifest.json
bsdtar -tf external_assets\kingbasees\incoming\KingbaseES_V009R001C010B0004_Lin64_install.iso
docker load --input external_assets\kingbasees\incoming\KingbaseES_V009R001C010B0004_x86_64_Docker.tar
docker image inspect kingbase_v009r001c010b0004_single_x86:v1

docker run --rm --read-only --entrypoint /bin/cat `
  kingbase_v009r001c010b0004_single_x86:v1 `
  /home/kingbase/docker-entrypoint.sh

docker run -d --name dify-plugin-phase94-kingbase --privileged --restart no `
  --env DB_USER=system --env DB_PASSWORD='<local-only>' --env DB_MODE=pg `
  --env ENCODING=UTF8 --env NEED_START=yes --publish 54321:54321 `
  --volume dify-plugin-phase94-kingbase-data:/home/kingbase/userdata `
  kingbase_v009r001c010b0004_single_x86:v1

docker exec dify-plugin-phase94-kingbase `
  /home/kingbase/install/kingbase/bin/sys_isready -h 127.0.0.1 -p 54321 -U system -d kingbase
docker exec dify-plugin-phase94-kingbase `
  /home/kingbase/install/kingbase/bin/ksql -X -U system -d kingbase -Atc 'select version();'
docker restart dify-plugin-phase94-kingbase
```

Expected result: exact media hashes match, image loads under its manifest-provided tag, the real server accepts connections, real SQL returns the KingbaseES version, and the same volume/license survives restart.

Failure meaning:

- hash mismatch: stop; media identity is not proven;
- load failure: image intake gate fails;
- missing/mismatched entrypoint or architecture: runtime assumptions must not proceed;
- license parser/initdb rejection: license/runtime gate fails;
- no readiness or SQL after restart: runtime persistence gate fails.

## Gate decision and remaining boundary

Phase 9.4 decision: **PASS**.

Closed blockers:

- `BLOCKED_BY_OFFICIAL_MEDIA`
- `DOCKER_DAEMON_UNAVAILABLE`
- `REAL_KINGBASE_SERVER_NOT_STARTED`

Still not closed by this phase:

- official Python driver artifact/import in plugin-daemon Python 3.12;
- SQLAlchemy dialect runtime feasibility;
- real Adapter/Provider/Tool/Workflow execution;
- offline wheel and package dependency closure.

No formal Adapter change is justified by this server-only gate.

## Delivery trace classification

- Final plugin changed: **NO**
- Development process history: **YES** — official media intake and the earlier blocker closure
- Final tutorial: **TUTORIAL_REQUIRED** for official image hash/load/start commands; license comparison detail is `DEVELOPMENT_HISTORY_ONLY`
- Machine JSON/CSV: **EVIDENCE_ONLY**
- Reproducible from current records: **YES**, subject to possession of the ignored official assets and a local administrator password
