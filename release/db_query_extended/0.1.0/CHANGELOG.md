# Changelog

本文件记录 `db_query_extended` 的用户可见变更。版本遵循语义化版本原则。

## [0.1.0] - 2026-06-29

### Added

- MySQL 8.4 与 PostgreSQL 16 只读查询支持。
- 可扩展 `DatabaseAdapter` 抽象以及 MySQL/PostgreSQL 独立 Adapter。
- Provider 凭据校验、查询超时、schema/search_path、charset 和 SSL mode。
- 稳定 JSON 结果格式、`max_rows` 截断和 JSON-safe 类型转换。
- `verify_provider.ps1`、`verify_tool.ps1`、`verify_workflow.ps1` 和 `verify_all.ps1`。
- Workflow API 正向查询与危险 SQL 自动化验收。

### Changed

- 数据库差异从 `utils/database.py` 迁移到 `utils/adapters/`。
- Provider 的 port/connection timeout 使用 Dify 1.13.3 兼容的 `text-input`，运行时仍转换为整数。
- SQL 安全策略冻结为单条 `SELECT` 或 `WITH ... SELECT`。

### Security

- DROP、UPDATE、DELETE、ALTER、CREATE 及其他写操作在数据库执行前被拒绝。
- API Key 仅通过环境变量传入，不写入脚本或验证报告。

### Verification

- Provider：4 PASS。
- Tool：20 PASS。
- Workflow API：11 PASS。
- 总计：35 PASS / 0 FAIL / 0 SKIP。

### Not Included

- DM8、KingbaseES 或其他数据库 Adapter。
- 生产环境连接池、证书部署和高可用设计。
