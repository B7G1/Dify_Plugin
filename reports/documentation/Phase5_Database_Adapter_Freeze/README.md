# Phase 5: 数据库核心 Adapter 架构冻结

状态：已完成（2026-06-28）

本阶段是架构重构，不新增数据库类型，不改变 Tool、Provider、JSON Schema 或 SQL 安全策略。目标是将 MySQL/PostgreSQL 差异从 `utils/database.py` 迁移到独立 Adapter，使后续数据库接入只需增加一个适配文件并在输入校验层声明支持类型。

## 为什么现在冻结

MySQL 和 PostgreSQL 已完成开发、真实数据库联调及 Dify Workflow 验证。此时两种实现足以提炼稳定接口，同时尚未引入 DM8/KingbaseES 的驱动差异，重构风险最低。

## 重构前

```text
database.py
├── MySQL URL / charset / timeout
└── PostgreSQL URL / ssl_mode / schema / timeout
```

## 重构后

```text
Tool / Provider
      │
      ▼
utils/database.py          生命周期、异常映射、格式化
      │
      ▼
DatabaseAdapter            统一契约
      │
 ┌────┴────────┐
 ▼             ▼
mysql.py   postgresql.py   驱动及会话差异
```

## Adapter 契约

- `build_database_url()`：生成 SQLAlchemy `URL`。
- `build_connect_args()`：生成 DBAPI 连接参数。
- `build_engine_options()`：保持 `pool_pre_ping` 和连接参数。
- `configure_session()`：设置查询超时、schema/search_path 等会话行为。
- `execute_query()`：执行已通过只读校验的 SQL。

Adapter 通过 `utils.adapters.<database_type>` 动态加载，并约定模块导出 `Adapter` 类。核心执行器不维护数据库类型分支。

## 稳定性约束

- 继续使用 `NullPool`，每次调用后执行 `engine.dispose()`。
- MySQL 保持 `mysql+pymysql`、charset 和 `MAX_EXECUTION_TIME`。
- PostgreSQL 保持 `postgresql+psycopg2`、`sslmode`、`statement_timeout` 和 `search_path`。
- Tool/Provider 调用方式、返回 JSON Schema、formatter、validation、sql_validator 均未修改。
- `manifest.yaml`、`requirements.txt`、Provider/Tool YAML 均未修改。

## 验证结果

2026-06-28：

| 验证项 | 结果 |
| --- | --- |
| Adapter 契约（MySQL/PostgreSQL） | PASS |
| MySQL Provider/Tool 数据库矩阵 | PASS |
| PostgreSQL Provider/Tool 数据库矩阵 | PASS |
| SQL 安全与 formatter 回归 | PASS |
| `verify_plugin.ps1` | 76 PASS / 0 FAIL / 1 SKIP |
| 本地 MySQL/PostgreSQL acceptance SQL | PASS |
| 插件重新打包 | PASS |
| Workflow 自动调用 | SKIP：当前会话未提供 API URL/Key；沿用 2026-06-25 已通过基线 |

机器证据：[`../../verification/2026-06-28/architecture_freeze_report_2026-06-28.json`](../../verification/2026-06-28/architecture_freeze_report_2026-06-28.json)

## 后续扩展入口

接入 DM8 或 KingbaseES 时，新增 `utils/adapters/dm.py` 或 `kingbase.py`，实现上述契约；再在 `validation.py` 和 Provider 配置中显式开放新类型。Tool 主逻辑、查询生命周期和结果格式化无需修改。本阶段没有提前添加任何国产数据库驱动或配置。
