# Final Repository Hygiene Audit

Date: 2026-07-02

## Findings

| Category | Count / files | Decision |
| --- | --- | --- |
| Virtual environments | 2 `.venv` directories | local-only; ignored; do not publish |
| Python bytecode caches | 177 `__pycache__` directories | disposable; ignored; safe to delete locally after review |
| R history | 8 `.Rhistory` files | disposable; ignored; do not publish |
| Local Plugin CLI binaries | `dify-plugin.exe`, `dify-plugin-windows-amd64.exe` | ignored local tooling; do not publish in source release |
| Generated reports/evidence | dated `reports/` content | retain; release evidence and history |
| Historical HTML assets | dated dashboards and archives | retain together to avoid broken relative links |

## Plugin package inventory

| File | Size | SHA-256 | Classification |
| --- | ---: | --- | --- |
| `db_query_extended-0.1.1-dm8-linux-amd64.difypkg` | 41,524,953 | `CEE3B0D7D54ECF1171E78739FF01C12D204F9B0CCCF7627D51AFAA69631A142B` | v1.0.0 release artifact |
| `db_query_extended.difypkg` | 18,590,127 | `3BA8952CCFB6C42D3865C28D2C1CC83A879BE1ADD2059AFFACF3D7E1B878736A` | earlier root build; archive candidate |
| `db_query_extended/db_query_extended.difypkg` | 21,467 | `BA7F9B04B73434CB4B90DE6784CA1C6982AED05BDD297CDD6481F25D0588BB63` | development build; not release artifact |
| `junjiem-db_query_0.0.11-offline.difypkg` | 73,095,087 | `6619DB2611D25C685F8CA4F565F86E972A0EBD25894464EF911AEA09C77F1560` | third-party reverse-analysis sample; retain outside release |
| `test_tool_schema.difypkg` | 10,967,969 | `B4AE5B013896755ED285F8996B03F6CEB6D888247929028BE40DC18242643515` | test artifact; archive candidate |

The packages are not byte-identical. No package was deleted or silently relabeled. The release owner should publish only the explicitly approved 0.1.1 Linux `amd64` candidate and its checksum.

## Worktree warning

The repository contains extensive pre-existing modified, deleted, and untracked material. A release commit must be assembled intentionally; `git add .` is not recommended. Review every deletion and stage the v1.0 scope by explicit path.

## Recommended local cleanup

After confirming no active process needs them, locally remove `.Rhistory`, `__pycache__`, `.pyc`, and disposable virtual environments. Archive older/test `.difypkg` files outside the source-release payload. This report intentionally performs no destructive cleanup.
