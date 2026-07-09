# Interactive Map Sync Review

Date: 2026-07-08  
Scope: `db_query_extended_interactive_map/db_query_extended_interactive_map/`

## Decision

Map status: **BLOCKED - MANUAL BROWSER VISUAL CHECK REQUIRED**

The interactive map is a project deliverable, not disposable generated junk.

## What was inspected

- `index.html`
- `assets/app.js`
- `assets/style.css`
- `assets/timeline-data.js`
- `assets/code-snapshots.generated.js`
- `scripts/generate_code_snapshots.py`
- nested `assets/code-snapshots/step-24-cockpit-and-map/`
- `data/`

## Root cause of nested snapshot files

`generate_code_snapshots.py` added map runtime files to Step 24:

- `index.html`
- `assets/app.js`
- `assets/style.css`
- `assets/timeline-data.js`
- `assets/file-metadata.js`
- `assets/code-snapshots.generated.js`

This caused nested Step 24 snapshot files to appear under:

```text
assets/code-snapshots/step-24-cockpit-and-map/
```

Capturing `assets/code-snapshots.generated.js` as full text is unsafe because it can recursively preserve generated snapshot state inside generated snapshot state.

## Fix applied

Narrow generator fix:

- `assets/code-snapshots.generated.js` is now summarized instead of copied into snapshots;
- any future `assets/code-snapshots/` path is also summarized;
- map source files can still be snapshotted normally.

File changed:

- `db_query_extended_interactive_map/db_query_extended_interactive_map/scripts/generate_code_snapshots.py`

## Regeneration

Regeneration was performed with:

```powershell
E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe db_query_extended_interactive_map\db_query_extended_interactive_map\scripts\generate_code_snapshots.py
```

Result:

- Step 13-24 snapshots regenerated.
- Step 24 cumulative files: 58.
- Recursive generated snapshot content is represented by a summary string.

## Static validation

Commands executed:

```powershell
node --check assets/app.js
node --check assets/timeline-data.js
node --check assets/code-snapshots.generated.js
python -m py_compile scripts/generate_code_snapshots.py
```

Result:

- JavaScript syntax checks: PASS, using bundled Codex Node runtime.
- Python generator compile check: PASS.
- Timeline structure: PASS, 24 entries.
- Snapshot structure: PASS, 24 entries.
- Recursive capture prevention: PASS.

## Current-state consistency

The reviewed current project facts remain:

- Phase 7.2 multilingual compatibility: PASS.
- MySQL / PostgreSQL / DM8 stored multilingual exact-equality gate: PASS.
- DM8 machine evidence: `reports/verification/2026-07-07/multilingual_dm_result.json`.
- Frontend screenshot set FE-15 through FE-24: 10/10 present.
- Frontend visual review: PASS_MANUAL_VISUAL_REVIEW.
- Independent machine vision review: NOT PERFORMED.
- Phase 7.3 / 7.3b: PASS.
- Provider: 6 PASS / 0 FAIL / 0 SKIP.
- Tool: 27 PASS / 0 FAIL / 0 SKIP.
- Workflow: 12 PASS / 0 FAIL / 0 SKIP.
- `verify_all`: 45 PASS / 0 FAIL / 0 SKIP.
- DM8 data capability: 14 PASS / 0 PARTIAL / 0 NOT_EVIDENCED / 0 FAIL.
- Workflow destructive SQL rejection: PASS with `ReadOnlyViolationError`.
- The older Workflow 0 PASS / 11 FAIL result is historical verifier false negative.
- Production plugin code was not changed by verifier normalization.

## Browser verification attempt and blocker

Real browser verification was attempted with the in-app browser.

Observed blocker:

- direct `file://` loading was not allowed by browser policy;
- a temporary local HTTP server returned `HTTP 200` from shell checks;
- the in-app browser still returned `ERR_CONNECTION_REFUSED` for `http://127.0.0.1:8765/index.html`;
- no alternative browser automation path was used, because this task requires a real browser acceptance path and must not fake visual PASS.

Current conclusion:

```text
BLOCKED - MANUAL BROWSER VISUAL CHECK REQUIRED
```

Therefore Commit 2G must not be created until a real browser visual check confirms:

- 24 timeline steps visible;
- step 1 through step 24 navigable;
- file / snapshot interaction works;
- no recursive `assets/code-snapshots/` contamination;
- no blocking browser console error.

## Deferred Decision

User decision recorded on 2026-07-08:

- manual browser visual acceptance is deferred;
- Commit 2G does not block Phase 8 database compatibility development;
- Commit 2G remains a separate visual delivery item;
- 2G-related modified and untracked files must not be mixed into Phase 8 database commits;
- the later 2G closeout still requires real browser acceptance before the map commit itself is created.
