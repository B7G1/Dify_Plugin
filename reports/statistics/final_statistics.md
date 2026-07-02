# v1.0.0 Final Statistics

Captured: 2026-07-02

## Repository and project

| Metric | Value | Counting rule |
| --- | ---: | --- |
| Phase documentation directories | 12 | directories matching `reports/documentation/Phase*` |
| Report Markdown files | 100 | `.md` files recursively under `reports/` at closure |
| HTML files | 9 | `.html` files recursively under `reports/html_reports/` |
| Dashboard / map entry files | 4 | HTML filenames containing dashboard, cockpit, or project_map |
| Verification evidence files | 64 | all files recursively under `reports/verification/` |
| Verification JSON files | 33 | `.json` files under `reports/verification/` |
| Supported databases | 3 | MySQL, PostgreSQL, DM8 |
| Provider configurations represented by the accepted Workflow | 1 | accepted DM8 Provider |
| Published acceptance Workflows | 1 | DM8 Readonly SQL Acceptance |
| Production adapters | 3 | MySQL, PostgreSQL, DM8 |
| Automated acceptance checks | 45 | Provider 6 + Tool 27 + Workflow 12 |

Counts describe the closure workspace, including historical evidence retained by policy.

## Verification

| Suite | PASS | FAIL | SKIP |
| --- | ---: | ---: | ---: |
| Provider | 6 | 0 | 0 |
| Tool | 27 | 0 | 0 |
| Workflow | 12 | 0 | 0 |
| Total | **45** | **0** | **0** |

## Git identity

- Branch at closure: `main`.
- Commit baseline: `9705c619a26a690925421fd5dd522d6e644dbc48`.
- Upstream state observed: `main...origin/main [ahead 3]`.
- Suggested release tag: `v1.0.0`.
- No release commit, tag, or push was executed during closure.

## Release artifact

- Product version: `v1.0.0`.
- Plugin version: `0.1.1`.
- Artifact: `db_query_extended-0.1.1-dm8-linux-amd64.difypkg`.
- Size: 41,524,953 bytes.
- SHA-256: `CEE3B0D7D54ECF1171E78739FF01C12D204F9B0CCCF7627D51AFAA69631A142B`.

## Environment identity

- Dify: 1.13.3.
- Plugin daemon: `langgenius/dify-plugin-daemon:0.5.3-local`.
- PostgreSQL system identifier: `7657369583221227555`.
- Environment Ready: YES.
- Public Release: READY.
- Lifecycle: COMPLETED.
