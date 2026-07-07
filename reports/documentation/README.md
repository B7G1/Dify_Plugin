# Documentation Index

## Current authoritative set

- `Phase7_1_DM8_Adapter/Final_Acceptance_Report_2026-07-01.md`
- `Phase7_1_DM8_Adapter/technical_report_2026-07-01.md`
- `Phase7_1_DM8_Adapter/executive_report_2026-07-01.md`
- `Phase7_1_DM8_Adapter/dify_environment_diagnosis_2026-06-30.md`
- `Phase7_1_DM8_Adapter/data_retrieval_validation.md` — DM8 数据能力专项矩阵与端到端证据链；历史审计入口，后续 closure 已补齐。
- `Phase7_2_Multilingual_Compatibility/README.md` — PASS；MySQL / PostgreSQL / DM8 stored multilingual exact equality gate 全部通过。
- `../verification/2026-07-07/multilingual_dm_result.json` — DM8 multilingual machine evidence，`{"pass": 1, "fail": 0, "skip": 0}`。
- `Phase7_2_Multilingual_Compatibility/frontend_screenshot_evidence_index.md` — frontend screenshot file set COMPLETE, 10/10; project-owner manual visual review PASS; independent machine-vision verification NOT PERFORMED.
- `Phase7_3_Full_Adapter_Regression/README.md` — PASS；Provider 6/0/0，Tool 27/0/0，Workflow 12/0/0，verify_all 45/0/0.
- `../../Developer_Guide.md`
- `../../architecture/README.md`
- `Phase9_Product_Ready/README.md`
- `Phase9_5_Public_Release/README.md`
- `Phase9_5_Public_Release/Public_Release_Summary_v1.0.md`

## Historical phases

`Phase1_*` through `Phase7_*` preserve design decisions and evidence chronology. Where a phase contains several summaries, its latest dated final/README document is the entry point; earlier daily notes remain historical and are not release truth.

Release-facing material belongs in `reports/release/v1.0/`, not in this directory.

## Credential boundary note

`DIFY_TEST` was used only as a local DM8 administrator for interactive fixture setup authorization. It is not a plugin runtime credential. Provider / Adapter / Tool / Workflow execution remains on the read-only `PLUGIN_TEST_USER` path.
