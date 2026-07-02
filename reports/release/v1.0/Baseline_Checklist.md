# v1.0 Baseline Checklist

## Identity

- [x] Plugin package version is 0.1.1.
- [x] Git commit and branch are recorded in `BASELINE.md`.
- [x] Dify, SDK, runtime, daemon, and database versions are documented.

## Persistence and runtime

- [x] Fixed Compose project is `dify`.
- [x] Startup uses `start_dify.ps1`.
- [x] PostgreSQL identifier remained `7657369583221227555` after cold boot.
- [x] `dify` and `dify_plugin` exist.
- [x] Plugin daemon has no restart loop.

## Acceptance

- [x] Provider: 6/0/0.
- [x] Tool: 27/0/0.
- [x] Workflow: 12/0/0.
- [x] Total: 45 PASS / 0 FAIL / 0 SKIP.
- [x] DM8 Unicode and Workflow API were exercised after cold boot.

## Release hygiene

- [x] No business logic changed during baseline documentation work.
- [x] Release documents contain no API key, password, or token.
- [x] Screenshot Review completed by final manual owner confirmation; current UI evidence is approved.
- [ ] Review the full Git diff and select release files intentionally.
- [ ] Run the repository secret scan immediately before commit.
- [ ] Create release commit/tag only after human approval.
