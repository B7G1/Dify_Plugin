# Reports Index

本目录是仓库报告、log、测试数据和可视化地图的主入口。中文汇报先看 [`../当前状态.md`](../当前状态.md)，完整导航看 [`REPORT_MAP.md`](REPORT_MAP.md)。

## Recommended Order

1. [`../当前状态.md`](../当前状态.md) — 每次对话后更新的中文汇报状态。
2. [`REPORT_MAP.md`](REPORT_MAP.md) — 按日期、进度、分类整理的报告地图。
3. [`../BASELINE.md`](../BASELINE.md) — frozen environment identity and recovery entry.
4. [`release/v1.0/`](release/v1.0/README.md) — publishable v1.0 material.
5. [`documentation/Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md`](documentation/Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md) — final human-readable acceptance.
6. [`documentation/Phase7_1_DM8_Adapter/data_capability_evidence_closure_2026-07-06.md`](documentation/Phase7_1_DM8_Adapter/data_capability_evidence_closure_2026-07-06.md) — DM8 14 capability evidence closure.
7. [`documentation/Phase7_2_Multilingual_Compatibility/README.md`](documentation/Phase7_2_Multilingual_Compatibility/README.md) — Phase 7.2 multilingual stored-data exact equality gate: PASS.
8. [`documentation/Phase7_3_Full_Adapter_Regression/README.md`](documentation/Phase7_3_Full_Adapter_Regression/README.md) — full MySQL / PostgreSQL / DM8 adapter regression gate: PASS.
9. [`verification/2026-07-01/final_cold_boot/`](verification/2026-07-01/final_cold_boot/README.md) — authoritative 45/0/0 machine evidence.
10. [`html_reports/2026-07-01_phase7_1_final/dashboard.html`](html_reports/2026-07-01_phase7_1_final/dashboard.html) — documentation website.
11. [`documentation/Phase11_SQLServer_Adapter/environment_gate.md`](documentation/Phase11_SQLServer_Adapter/environment_gate.md) — latest SQL Server environment gate status.

## Taxonomy

| Directory | Content policy |
| --- | --- |
| `documentation/` | technical, executive, phase, setup, and diagnosis documents |
| `verification/` | JSON results, logs, backups, and dated execution evidence |
| `html_reports/` | navigable dashboards, project maps, and rendered reports |
| `release/` | release notes, compatibility, migration, and checklists |
| `snapshots/` | immutable environment identity captures |
| `statistics/` | repository and verification statistics |
| `architecture/` | pointer to the canonical root architecture set |
| `archive/` | superseded or duplicate material retained for history |
| `root_reports/` | loose root-level report/render artifacts consolidated without deletion |

## Current Status

- v1.0 technical baseline: PASS
- Automated acceptance: 45 PASS / 0 FAIL / 0 SKIP
- Supported v1.0 adapters: MySQL, PostgreSQL, DM8
- DM8 data capability evidence: COMPLETE, 14 PASS / 0 PARTIAL / 0 NOT EVIDENCED / 0 FAIL
- Phase 7.2 Multilingual Compatibility: PASS
- Stored multilingual exact equality gate: MySQL PASS / PostgreSQL PASS / DM8 PASS
- DM8 multilingual machine evidence: `verification/2026-07-07/multilingual_dm_result.json` with `{"pass": 1, "fail": 0, "skip": 0}`
- Phase 7.2 frontend screenshot evidence: COMPLETE, 10/10 files present; manual visual review PASS; independent machine-vision verification NOT PERFORMED
- Phase 7.3 Full Adapter Regression: PASS; Provider 6 PASS, Tool 27 PASS, Workflow 12 PASS, verify_all 45 PASS / 0 FAIL / 0 SKIP
- `DIFY_TEST`: local DM8 administrator used only for interactive fixture setup authorization; not a plugin runtime credential and no password is recorded
- KingbaseES: Phase 10 documents and evidence archived
- SQL Server: Phase 11 environment gate PASS; not yet integrated into plugin business code or `verify_all.ps1`
- Secrets: prohibited from reports and Git

Earlier dated reports remain evidence of their phase; they are not the current release statement. Do not delete them or use them in place of v1.0 documents.
