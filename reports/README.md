# Reports Index

This directory separates current release truth from historical evidence. A new reader should use the following order:

1. [`../BASELINE.md`](../BASELINE.md) — frozen environment identity and recovery entry.
2. [`release/v1.0/`](release/v1.0/README.md) — publishable v1.0 material.
3. [`documentation/Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md`](documentation/Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md) — final human-readable acceptance.
4. [`verification/2026-07-01/final_cold_boot/`](verification/2026-07-01/final_cold_boot/README.md) — authoritative 45/0/0 machine evidence.
5. [`html_reports/2026-07-01_phase7_1_final/dashboard.html`](html_reports/2026-07-01_phase7_1_final/dashboard.html) — documentation website.
6. [`documentation/Phase9_Product_Ready/`](documentation/Phase9_Product_Ready/README.md) — product/open-source readiness status.
7. [`documentation/Phase9_5_Public_Release/`](documentation/Phase9_5_Public_Release/README.md) — public demo, screenshot audit, and publication gates.
8. [`documentation/Phase9_5_Public_Release/Public_Release_Summary_v1.0.md`](documentation/Phase9_5_Public_Release/Public_Release_Summary_v1.0.md) — final v1.0 Public Release decision.
9. [`release/v1.0/RELEASE_CLOSURE.md`](release/v1.0/RELEASE_CLOSURE.md) — v1.0.0 lifecycle closure.
10. [`statistics/final_statistics.md`](statistics/final_statistics.md) — final repository and verification statistics.

## Taxonomy

| Directory | Content policy |
| --- | --- |
| `documentation/` | technical, executive, phase, setup, and diagnosis documents |
| `verification/` | JSON results, logs, backups, and dated execution evidence |
| `snapshots/` | immutable environment identity captures |
| `release/` | current release notes, compatibility, migration, and checklists |
| `html_reports/` | navigable dashboards and historical rendered reports |
| `architecture/` | pointer to the canonical root architecture set |
| `archive/` | superseded or duplicate material retained for history |

## Current status

- v1.0 technical baseline: PASS
- Automated acceptance: 45 PASS / 0 FAIL / 0 SKIP
- Supported adapters: MySQL, PostgreSQL, DM8
- Secrets: prohibited from reports and Git

Earlier dated reports remain evidence of their phase; they are not the current release statement. Do not delete them or use them in place of v1.0 documents.
