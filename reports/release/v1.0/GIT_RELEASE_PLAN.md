# Git Release Plan for v1.0.0

## Suggested tag

```text
v1.0.0
```

Use an annotated tag only after the release commit, selected package checksum, secret scan, and owner approval are complete.

## Suggested commit message

```text
release: freeze db_query_extended v1.0.0 baseline

- publish MySQL, PostgreSQL, and DM8 read-only baseline
- archive 45 PASS / 0 FAIL / 0 SKIP acceptance evidence
- add recovery, architecture, demo, and public release documentation
- set next phase to KingbaseES adapter
```

## Branch strategy

- `main`: protected, always reflects the latest accepted stable baseline. Merge through reviewed pull requests; require zero-fail regression and secret checks.
- `release/v1.0`: short-lived stabilization branch for selecting release files, checksum verification, documentation corrections, and final tag preparation. No new features.
- `feature/kingbasees`: Phase 10 development branch created from the tagged `v1.0.0` baseline. Keep KingbaseES work isolated until Provider/Tool/Workflow/API and full regression pass.
- Optional `hotfix/v1.0.x`: urgent v1.0 corrections branched from the tag and merged back into `main` and active feature work.

## Safe staging recommendation

Do not use `git add .` in the current dirty worktree. Stage explicit release paths, inspect `git diff --cached`, run the staged secret scan, and verify that historical user deletions or unrelated interactive-map edits are not accidentally included.

No commit, branch, tag, or push is performed by this plan.
