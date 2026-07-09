# db_query_extended 0.1.0

状态：**Release Frozen**  
冻结日期：2026-06-29  
验证门禁：**35 PASS / 0 FAIL / 0 SKIP**

## 交付内容

```text
0.1.0/
├── README.md
├── RELEASE_NOTES.md
├── SHA256SUMS.txt
├── release-manifest.json
├── CHANGELOG.md
├── artifacts/
│   └── db_query_extended-0.1.0.difypkg
├── verification/
│   ├── provider_result.json
│   ├── tool_result.json
│   ├── workflow_result.json
│   └── summary.json
├── metadata/
│   ├── manifest.yaml
│   ├── requirements.txt
│   ├── provider/db_query_extended.yaml
│   └── tools/db_query_extended.yaml
└── adr/ADR-0001-release-freeze.md
```

## 安装

1. 本地 Dify 1.13.3 开发环境确认 plugin-daemon 使用 `FORCE_VERIFYING_SIGNATURE=false`。
2. 在 Dify Plugins 页面上传 `artifacts/db_query_extended-0.1.0.difypkg`。
3. 配置 MySQL 或 PostgreSQL Provider。
4. 执行 `db_query_extended/verification/verify_all.ps1` 复验。

此包未签名，仅用于当前本地开发/验收环境。生产发布必须补充正式签名、密钥管理和目标环境验证。

## 完整性检查

```powershell
Get-FileHash .\artifacts\db_query_extended-0.1.0.difypkg -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

校验值不一致时不得安装或作为 Phase 7 基线。

## 冻结边界

- Tool、Provider、JSON Schema、SQL 安全策略和 Adapter 契约冻结。
- 支持数据库仅为 MySQL/PostgreSQL。
- Phase 7 必须新增 Adapter，不得把国产数据库分支重新写回 `database.py`。
- Release 证据是冻结快照；后续验证结果另建日期目录，不覆盖本目录。
