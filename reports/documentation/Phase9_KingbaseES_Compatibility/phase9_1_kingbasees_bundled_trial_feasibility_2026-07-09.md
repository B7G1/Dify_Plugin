# Phase 9.1 - KingbaseES Bundled Trial License Feasibility Gate

Date: 2026-07-09

Verdict: `BLOCKED - OFFICIAL_INSTALL_MEDIA_MISSING`

## 1. Previous blocker

The previous KingbaseES environment gate treated the missing external `license.dat` as the main blocker.

For Phase 9.1, that conclusion is paused and narrowed. The project owner confirmed that official KingbaseES documentation describes a development/trial path where installation can use the software bundled trial authorization when no external authorization file is selected.

This gate therefore re-checks the local repository, Docker inventory, and existing KingbaseES preparation scripts to determine whether the current environment can exercise that official bundled trial path.

## 2. Official bundled trial assumption

Project-owner supplied official-documentation facts for this gate:

- KingbaseES development edition provides a 365-day free trial authorization.
- The development edition is intended for product trial and day-to-day development.
- The development edition limits database connection count, but is suitable for local development validation.
- Official installation documentation states that when no authorization file is selected during installation, the software bundled trial authorization is used.

This report accepts those facts as the Phase 9.1 operating assumption. The local gate still must verify whether a matching official installer or official image is actually present in this workspace or Docker environment.

## 3. Current local assets

Inspected path:

`E:\Dify_Plugin\local_test_db\kingbase`

Current files:

| Path | Purpose |
|---|---|
| `local_test_db/kingbase/.env.example` | Placeholder variables for local KingbaseES test environment |
| `local_test_db/kingbase/docker-compose.yml` | Isolated KingbaseES test compose project template |
| `local_test_db/kingbase/prepare.ps1` | Preflight script checking image availability and compose rendering |
| `local_test_db/kingbase/README.md` | Current environment preparation notes |
| `local_test_db/kingbase/init/01_create_database_and_role.sql` | Draft admin setup SQL |
| `local_test_db/kingbase/init/02_schema_and_data.sql` | Draft deterministic fixture SQL |
| `local_test_db/kingbase/verification/verify.ps1` | Draft verification wrapper |
| `local_test_db/kingbase/verification/verify.sql` | Draft verification SQL |

Docker inventory check:

| Inventory | Result |
|---|---|
| KingbaseES-related images | None found |
| KingbaseES-related containers | None found |
| KingbaseES-related volumes | None found |

Repository media check:

- No KingbaseES installer was found in the repository.
- No KingbaseES image tar was found in the repository.
- No official KingbaseES Docker image is currently loaded in Docker.
- No local `license.dat` was found or used.

## 4. Installer / image version

No official KingbaseES installer or Docker image is currently available in the audited workspace or Docker inventory.

Therefore the exact local KingbaseES version, edition, and architecture cannot be verified in this gate.

The existing compose template is designed for a Linux container image exposing port `54321` and running in PostgreSQL compatibility mode via `DB_MODE=pg`, but this is a template expectation, not a verified runtime fact.

## 5. Edition finding

Current local edition: `NOT_VERIFIED`

Reason: no official installer/image is present to inspect.

The project-owner supplied official documentation supports a development/trial path in principle, but Phase 9.1 cannot map that path to a concrete local artifact yet.

## 6. Bundled trial license finding

Phase 9.1 did not find any current local installation media from which to inspect bundled trial behavior.

Result:

`BUNDLED_TRIAL_PATH_NOT_LOCALLY_TESTABLE_YET`

Important boundary:

- This is not evidence that KingbaseES requires an external `license.dat` for the development path.
- This is evidence that the current workspace/Docker environment does not yet contain the official installer or image needed to exercise the bundled trial path.

## 7. Current prepare script finding

Inspected file:

`local_test_db/kingbase/prepare.ps1`

The script requires:

- `KINGBASE_IMAGE`
- `KINGBASE_ADMIN_PASSWORD`

The script does not require:

- `LICENSE_FILE`
- `license.dat`

The compose template requires:

```yaml
image: "${KINGBASE_IMAGE:?Set KINGBASE_IMAGE to the exact vendor-provided image loaded locally}"
```

Finding:

`LOCAL_PREP_SCRIPT_IS_IMAGE_GATE_NOT_LICENSE_DAT_GATE`

The current blocker is not a confirmed external-license requirement. The current blocker is that no official KingbaseES install media or vendor-provided image is available locally.

The README still uses conservative wording about image/license readiness. That wording should be updated only after an official installer/image is provided and the bundled trial startup path is actually exercised.

## 8. Whether external license.dat is actually required

Current answer:

`NOT_PROVEN_REQUIRED`

Based on this local audit:

- No current script requires an external `license.dat`.
- No external `license.dat` was used.
- No official media is present, so the bundled trial behavior cannot be started or confirmed.

The earlier blocker should therefore be restated as:

`OFFICIAL_INSTALL_MEDIA_MISSING`

not:

`EXTERNAL_LICENSE_DAT_REQUIRED`

## 9. Startup probe result

Startup probe was not executed.

Reason:

`OFFICIAL_INSTALL_MEDIA_MISSING`

No official KingbaseES installer or Docker image is currently present. Running a startup probe without official media would violate the source boundary for this phase.

No third-party image, mock server, PostgreSQL substitute, copied license, patched binary, or time modification was used.

## 10. Server feasibility result

Server feasibility validation was not executed.

Not executed checks:

- server accepting connections
- admin connection
- `plugin_test` database
- readonly test user
- test schema
- fixture table
- `SELECT 1`
- Unicode fixture
- schema-qualified read

Reason:

`OFFICIAL_INSTALL_MEDIA_MISSING`

## 11. Secret hygiene

- No password was written into this report.
- No license content was inspected or copied.
- No external `license.dat` was used.
- No plugin credentials, tokens, or Workflow API keys were recorded.

## 12. Legal / source boundary

This gate preserved the requested legal/source boundary:

- Did not download or use third-party KingbaseES images.
- Did not download or use third-party `license.dat`.
- Did not copy an existing installation license.
- Did not modify license files or binaries.
- Did not patch KingbaseES runtime behavior.
- Did not change system time.
- Did not substitute PostgreSQL or a mock server as KingbaseES.

## 13. Next task

Provide or load one official KingbaseES development/trial artifact:

1. Official KingbaseES installer that supports bundled trial authorization; or
2. Official KingbaseES Docker image/tar that is legally obtained and supports the development/trial path.

Then rerun Phase 9.1 as an isolated startup probe:

- do not pass external `license.dat`;
- use the official bundled trial behavior;
- use isolated compose project/container/port/volume;
- record version, edition, architecture, trial/license status if available from runtime;
- then run minimal server feasibility validation.

## 14. Final verdict

`BLOCKED - OFFICIAL_INSTALL_MEDIA_MISSING`

