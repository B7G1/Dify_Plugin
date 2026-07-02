# Contributing

## Before coding

Read `BASELINE.md`, `Developer_Guide.md`, `architecture/README.md`, and `TEST_MATRIX.md`. Open an issue for behavior changes and state the database/version, risk, and proposed acceptance evidence.

## Development rules

- Preserve the read-only SQL boundary and stable JSON contract.
- Put database-specific behavior behind the Adapter contract.
- Never commit passwords, API keys, tokens, private keys, live connection URLs, database dumps, or credential screenshots.
- Do not reduce existing test coverage or convert a failure into SKIP.
- Keep machine evidence separate from prose conclusions.

## Pull requests

1. Create a focused branch and small, reviewable change.
2. Add or update tests before changing support status.
3. Run relevant unit/adapter checks and the full accepted regression.
4. Update compatibility, limitations, test matrix, release notes, and architecture when affected.
5. Complete the PR template and disclose any vendor driver/license dependency.

The release requirement is zero unexplained FAIL/SKIP. New database support additionally requires real Provider, Workflow, API, Unicode, type, timeout, and dangerous-SQL evidence.

## Documentation-only changes

Verify links, image provenance, dimensions, and secret hygiene. Never alter screenshots to fabricate a passing state.

By contributing, you confirm you have the right to submit the material. Contribution licensing terms remain pending the repository owner's license decision.
