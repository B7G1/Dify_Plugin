# Reports

This directory is the single entry point for project reporting.

Read in this order:

1. [`REPORTING_STANDARD.md`](REPORTING_STANDARD.md) — mandatory policy for every report task.
2. [`REPORT_MAP.md`](REPORT_MAP.md) — canonical report and evidence index.
3. [`templates/PHASE_REPORT_TEMPLATE.md`](templates/PHASE_REPORT_TEMPLATE.md) — required metadata and audit sections for new phase reports.

## Canonical taxonomy

| Path | Responsibility |
| --- | --- |
| `documentation/YYYY-MM-DD/PhaseXX_Subject/` | one human-maintained report per task/run |
| `verification/YYYY-MM-DD/` | machine JSON/CSV/checksum/test evidence |
| `logs/YYYY-MM-DD/PhaseXX_Subject/` | raw stdout/stderr and runtime logs |
| `assets/YYYY-MM-DD/PhaseXX_Subject/` | screenshots and attachments |
| `generated/html/YYYY-MM-DD/PhaseXX_Subject/` | generated HTML only |
| `templates/` | report authoring templates |

The legacy phase-first documentation and `html_reports` trees are historical migration inputs, not permission to create new reports there. New work must use the dated structure. Code snapshots are `HISTORICAL_SNAPSHOT / NON_AUTHORITATIVE`; do not edit them as report sources.

Machine evidence is not deleted merely because a human report summarizes it. Logs are not copied into reports. Sensitive assets, credentials, license contents, database media, and data directories never enter Git.

From the reporting-governance commit onward, every report request is governed by [`REPORTING_STANDARD.md`](REPORTING_STANDARD.md).
