# Release Checklist

## Scope and identity

- [ ] Confirm intended plugin version, Git commit, branch, and clean release diff.
- [ ] Confirm no unrelated user work is staged.
- [ ] Confirm manifest, package filename, release notes, compatibility, and changelog agree.
- [ ] Confirm the release package hash is recorded if distributed.

## Acceptance

- [ ] Start only through `start_dify.ps1` and run preflight.
- [ ] Confirm persistent PostgreSQL identity and both required databases.
- [ ] Confirm plugin daemon is stable.
- [ ] Validate each supported Provider against a real database.
- [ ] Run real Workflow and API Unicode cases.
- [ ] Run `verify_all.ps1`; require zero FAIL and zero SKIP.
- [ ] Store JSON evidence under a new dated verification directory.

## Secrets and prohibited files

- [ ] Search staged content for `app-`, `Bearer`, `API_KEY`, `PASSWORD`, `TOKEN`, private keys, connection URLs, and credential exports.
- [ ] Confirm Workflow API Key is process-only and absent from reports/scripts/Git.
- [ ] Confirm database passwords and tokens are absent from logs and screenshots.
- [ ] Exclude `.env`, dumps, private keys, local history files, and credential-bearing Docker inspect output.
- [ ] Review package contents; do not bundle local caches or test secrets.

## Documentation and delivery

- [ ] Update `BASELINE.md`, release notes, limitations, compatibility, migration guide, and roadmap.
- [ ] Confirm Dashboard links work from disk.
- [ ] Confirm Technical, Executive, Verification, Snapshot, Architecture, and Release indexes agree.
- [ ] Review Known Limitations with the release owner.
- [ ] Obtain explicit approval before commit, tag, push, or plugin-store publication.

## v1.0.0 Public Release closure

- [x] Screenshot Review: PASS by final manual owner confirmation.
- [x] Plugin, Provider, Workflow, Dashboard, verification, architecture, and Cold Boot assets are accepted for public display.
- [x] 1918×1078 captures are classified as a non-blocking Minor Recommendation.
- [x] Phase 9.5 status pages and Dashboard are synchronized.
- [x] Project Status: RELEASED; Public Release: READY.
- [ ] Select an open-source license before claiming MIT, Apache-2.0, GPL-3.0, or another specific license.
- [ ] Obtain explicit approval before commit, tag, push, Marketplace submission, or external publication.

No commit, tag, push, or publication is authorized by this checklist itself.
