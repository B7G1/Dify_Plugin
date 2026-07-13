# Project Reporting Standard

- Standard version: 1.0
- Effective date: 2026-07-12
- Maintainer: Project documentation governance
- Status: ACTIVE
- Last updated commit: the latest commit returned by `git log -1 -- reports/REPORTING_STANDARD.md`
- Change policy: Update this file in place, increment the version for material changes, and record the change below. Do not create versioned copies.

## A. Purpose and scope

This is the only authoritative reporting policy for the project. It governs phase, database validation, environment, architecture, blocker, recovery, release, offline-installation, reproduction, machine-evidence, log, attachment, generated-HTML, `REPORT_MAP`, and interactive-map report-reference work.

It does not govern product source, SQL fixtures, Python/PowerShell verification scripts, Docker Compose, configuration templates, wheels, plugin packages, database media, or database data directories.

## B. Canonical directory structure

```text
reports/
├─ README.md
├─ REPORT_MAP.md
├─ REPORTING_STANDARD.md
├─ templates/
├─ documentation/YYYY-MM-DD/PhaseXX_Subject/
├─ verification/YYYY-MM-DD/
├─ logs/YYYY-MM-DD/PhaseXX_Subject/
├─ assets/YYYY-MM-DD/PhaseXX_Subject/
└─ generated/html/YYYY-MM-DD/PhaseXX_Subject/
```

- Human-maintained reports live only in `documentation`.
- Machine evidence lives only in `verification`.
- Raw stdout/stderr, Docker, transcript, installation, and probe logs live only in `logs`.
- Screenshots and attachments live only in `assets`.
- Generated HTML lives only in `generated`; it is never an authoring source.
- The `reports` root contains only entry points, standards, indexes, and templates.
- Repository-root project governance files such as `AGENTS.md`, `README.md`, roadmaps, matrices, and architecture indexes are not phase reports.
- `archive`, `analysis`, and interactive-map trees are never current authoritative report locations.

## C. One canonical report rule

Each task/run has exactly one canonical human report. Links, generated HTML, and explicitly labelled `HISTORICAL_SNAPSHOT / NON_AUTHORITATIVE` code snapshots are allowed; copied report bodies are not. Git preserves superseded text, so do not create archive copies for safety.

Different dates, execution batches, environments, or evidence boundaries may have separate reports. A later PASS does not erase an earlier BLOCKED run; lifecycle state in `REPORT_MAP.md` distinguishes them.

## D. Naming standard

- Date directory: `YYYY-MM-DD`.
- Stage directory: `PhaseXX_Subject`, or stable governance subjects such as `Environment_Persistence`, `Final_Delivery`, `Reproduction_Tutorial`, and `Report_Governance`.
- File: lowercase English with underscores, for example `phase9_4_official_media_image_runtime_gate.md`.
- Do not repeat the date in the filename.
- Do not use `final`, `latest`, `new`, `v2`, `copy`, or equivalent suffixes to create parallel reports. Revise the canonical file and rely on Git history.

## E. Required metadata

Every new human report starts with:

```text
- Date:
- Phase:
- Status:
- Database:
- Scope:
- Source commit:
- Runtime:
- Canonical path:
- Machine evidence:
- Logs:
- Supersedes:
- Security classification:
```

Top-level status is one of: `PASS`, `PARTIAL`, `BLOCKED`, `FAIL`, `CONDITIONAL GO`, `NO-GO`, `HISTORICAL_ONLY`, `SUPERSEDED`, `OPTIONAL`, `NOT_APPLICABLE`. Put finer gate results in the body.

## F. Required report sections

Use, when applicable: Executive Summary; Goal and Acceptance Boundary; Baseline; Environment; Work Performed; Commands Executed; Files Changed; Decisions; Verification Results; Evidence; Blockers; Abandoned Paths; Security and Redaction; Reproduction Trace; Git State; Final Decision; Next Step. Write `Not applicable` when an audit-relevant section has no content. Summarize logs; do not paste long raw output.

## G. Human report versus evidence

- Human report: explains facts, boundaries, decisions, and evidence.
- Machine evidence: JSON, CSV, checksums, inspect data, and structured test results.
- Log: raw stdout/stderr or service/runtime transcript.

Static presence is not runtime PASS. `BUNDLE_STRUCTURE_VALID` is not `OFFLINE_INSTALLATION_VERIFIED`; `DRIVER_IMPORT_PASS` is not end-to-end compatibility; historical evidence is not a current rerun.

## H. Evidence naming

Names state the subject and gate, such as `kingbasees_phase9_4_runtime_gate.json`. Avoid ambiguous names such as `result.json`, `output.txt`, `new.json`, and `final_result.json` in the permanent evidence tree.

## I. Duplicate handling

- Exact duplicate human reports: keep one canonical file.
- Highly overlapping human reports: merge still-correct unique material, then remove the duplicate.
- Superseded report: mark `SUPERSEDED` or remove the copy and use Git history.
- Never deduplicate distinct machine runs merely because their schemas or summaries resemble one another.
- PARTIAL and PASS reports may coexist only when their dates/tasks/evidence boundaries are explicit.

## J. Generated HTML policy

HTML is generated from canonical Markdown or structured data and is never edited as the report source. Keep one generated copy. Interactive maps link to canonical Markdown or generated HTML and must not embed a second manually maintained report body.

## K. REPORT_MAP policy

Every report add, move, rename, merge, or retirement updates `REPORT_MAP.md`. Each record includes Date, Phase, Status, Database, Canonical report, Machine evidence, Logs, Assets, Source commit, and Lifecycle state. Lifecycle is one of `CURRENT`, `SUPERSEDED`, `HISTORICAL_ONLY`, `PARTIAL_EVIDENCE`, `FINAL_CANDIDATE`. No dead links or competing canonical reports are allowed.

## L. Link policy

Use repository-relative links. Do not persist Downloads, sandbox, or machine-specific external-media paths as links. Describe local media as `LOCAL_ONLY / NOT_TRACKED_BY_GIT`. After a move, update Markdown, README, generator, JavaScript index, interactive-map data, and verification-script references without leaving compatibility copies.

## M. Sensitive-data policy

Never store passwords, API keys, tokens, license contents, private keys, credentialed connection strings, `.env` contents, cookies, or personal authentication data. It is acceptable to record existence, size, SHA-256, type, version, and runtime acceptance. License files, ISO/tar media, and database data remain Git-ignored.

## N. Git policy

Do not use `git add .`, `git add -A`, `git reset --hard`, `git clean -fd`, or revert user changes. Stage exact reviewed paths. Report governance gets a documentation-only commit and never shares a commit with product behavior.

## O. Required validation

Every report-reorganization task checks canonical uniqueness, exact duplicates, broken links, map paths, root cleanliness, evidence/log preservation, generated HTML, interactive map, sensitive exclusion, and `git diff --check`. Record results in `reports/verification/YYYY-MM-DD/report_structure_validation.json`.

A gate is PASS only when broken links, root-level phase reports, and duplicate canonical reports are zero; each task has one canonical report; evidence/logs are not silently lost; sensitive assets are untracked; and the interactive map still works. Otherwise report `PARTIAL` or `BLOCKED` honestly.

## P. Default behavior for report requests

When the user asks to create, organize, archive, consolidate, clean, summarize, or update reports:

1. Read `AGENTS.md` and this standard.
2. Inspect Git status and protect user changes.
3. Identify date, phase, report, evidence, logs, assets, and generated files.
4. Select one canonical path and compare duplicates.
5. Update references and `REPORT_MAP.md`.
6. Redact secrets and validate paths, uniqueness, generated artifacts, and Git diff.
7. Stage only exact report-governance paths and give a human summary.

Do not ask where reports belong unless the task identity itself is genuinely ambiguous.

## Reporting Task Checklist

Before: read `AGENTS.md`; read this standard; inspect Git status; identify user changes, task date, and phase.

During: choose the canonical path; separate reports/evidence/logs/assets/generated output; compare duplicates; update links and `REPORT_MAP`; redact secrets.

After: validate links, uniqueness, generated artifacts, map entries, and sensitive exclusion; run `git diff --check`; review every staged path.

## Change Log

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-07-12 | Established the canonical project reporting policy. |
