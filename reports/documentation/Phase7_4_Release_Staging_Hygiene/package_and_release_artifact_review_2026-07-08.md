# Package and Release Artifact Review

Date: 2026-07-08

## Package classification

| Artifact | Size | SHA-256 | Classification | Recommended action |
| --- | ---: | --- | --- | --- |
| `db_query_extended.difypkg` | 18,590,127 | `3BA8952CCFB6C42D3865C28D2C1CC83A879BE1ADD2059AFFACF3D7E1B878736A` | duplicate release package | Do not stage root copy; canonical copy is under `release/`. |
| `release/db_query_extended/0.1.0/artifacts/db_query_extended-0.1.0.difypkg` | 18,590,127 | `3BA8952CCFB6C42D3865C28D2C1CC83A879BE1ADD2059AFFACF3D7E1B878736A` | structured release artifact | Stage with release artifact commit if release 0.1.0 package evidence is desired. |
| `db_query_extended/db_query_extended.difypkg` | 21,467 | `BA7F9B04B73434CB4B90DE6784CA1C6982AED05BDD297CDD6481F25D0588BB63` | local early build output | Do not stage. |
| `junjiem-db_query_0.0.11-offline.difypkg` | 73,095,087 | `6619DB2611D25C685F8CA4F565F86E972A0EBD25894464EF911AEA09C77F1560` | third-party reference package | Do not stage in product release; keep local or archive outside source commit. |
| `test_tool_schema.difypkg` | 10,967,969 | `B4AE5B013896755ED285F8996B03F6CEB6D888247929028BE40DC18242643515` | test artifact | Do not stage. |

## Release directory

`release/db_query_extended/0.1.0/` contains:

- release notes;
- changelog;
- release manifest;
- ADR;
- metadata snapshot;
- verification results;
- package artifact;
- SHA256 sums.

Classification: **RELEASE_ARTIFACT**

Recommended action: stage as a dedicated release artifact commit, not mixed with interactive map or local test infrastructure.

## Staged-only secret gate

Targeted scan findings were reviewed and accepted as non-secret metadata:

- `metadata/provider/db_query_extended.yaml` contains the Provider field name `password` and input type `secret-input`;
- `verification/workflow_result.json` contains the redacted credential label `DIFY_WORKFLOW_API_KEY (redacted)`.

No live password, API key, token, or connection secret was found in the staged release artifact set.

## Final decision

Do not commit loose root `.difypkg` files. Keep one canonical package location under `release/db_query_extended/0.1.0/`.
