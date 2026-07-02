# Dify Plugin Marketplace Preparation

## Readiness decision

Current product state: **v1.0.0 RELEASED**. Official Dify Marketplace submission is a separate owner-controlled distribution action.

| Area | Current evidence | Gap / action |
| --- | --- | --- |
| Manifest | version 0.1.1, Python 3.12, amd64, minimum Dify 1.0.0 | fix corrupted Chinese labels; review Marketplace schema; change `verified: false` only through the official process |
| License | no repository license found | owner must select and approve an open-source license; add root `LICENSE` and package notice |
| README | root README rebuilt with architecture and manually approved evidence | update plugin-local README after license/contact decisions |
| Privacy | data handling policy completed | owner must publish an accountable privacy contact before submission |
| Icon | light and dark SVG assets exist | validate Marketplace dimensions, contrast, trademark, and SVG safety |
| Examples | real Workflow/API evidence exists internally | publish sanitized SQL and Workflow examples without credentials or internal hostnames |
| Screenshots | Screenshot Review PASS; all current v1.0.0 display assets manually approved | optional later normalization from 1918×1078 to 1920×1080 is non-blocking |
| Metadata | preparation metadata exists in `marketplace/metadata.yaml` | validate it against the current official Marketplace schema after owner/contact/license decisions |
| Package | 0.1.1 package exists | rebuild reproducibly, inspect contents, record SHA-256, test clean installation |
| Verification | 45 PASS / 0 FAIL / 0 SKIP | preserve public summary and sanitized evidence; define supported-environment statement |
| Security | `SECURITY.md`, issue/PR templates, read-only validation, and secret policy documented | owner must enable private reporting and publish responsible contacts |

## Required submission set

1. Approved `LICENSE`.
2. Final manifest with corrected UTF-8 localization and validated Marketplace metadata.
3. Completed privacy policy with an owner-approved public contact.
4. Plugin-local public README with Quick Start, credential fields, SQL examples, limitations, and support route.
5. Sanitized screenshots listed in `docs/images/README.md`.
6. Reproducible package and checksum.
7. Clean-Dify install, Provider validation, Workflow/API test, and full regression evidence.
8. Human review confirming no password, API key, token, internal hostname, personal data, or proprietary DM8 material is bundled.

Do not choose a license or claim official Marketplace verification without the project owner's explicit decision.
