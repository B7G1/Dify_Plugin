# Future Branch Strategy

## Protected baselines

### `main`

Contains the latest accepted release state. Direct feature commits are prohibited. Changes arrive through reviewed pull requests with regression and secret checks.

### `release/v1.0`

Represents the frozen v1.0.0 release line. Do not develop features on this branch. Only narrowly approved documentation corrections or critical `v1.0.x` hotfix preparation may be proposed, and they must preserve the frozen contracts and evidence.

## Feature branches

- `feature/kingbasees` — Phase 10 and the first `v1.1.x` adapter expansion.
- `feature/oracle` — future Oracle adapter after KingbaseES acceptance.
- `feature/sqlserver` — future SQL Server adapter.
- `feature/sqlite` — future SQLite adapter after file-security design approval.

All new development starts in `feature/*`, never in `release/v1.0`. A feature branch must start from the accepted release baseline or the latest reviewed `main`, document its database/driver dependency, and preserve the complete prior regression suite.

## Merge policy

1. Open an issue defining scope and acceptance criteria.
2. Create the feature branch; do not modify the release branch directly.
3. Add adapter-specific tests and run all inherited checks.
4. Require zero unexplained FAIL or SKIP.
5. Review compatibility, security, documentation, package contents, and secrets.
6. Merge to `main` only after acceptance; create a new release branch/tag for the new version.

v1.0.0 remains historical and immutable. Feature releases evolve as `v1.1.x`; critical backward-compatible fixes use an owner-approved `v1.0.x` hotfix process.
