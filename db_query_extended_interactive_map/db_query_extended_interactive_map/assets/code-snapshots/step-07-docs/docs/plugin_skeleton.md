# 插件骨架与查询实现记录

## 目录结构

```text
db_query_extended/
├─ manifest.yaml
├─ main.py
├─ provider/                 # Provider 表单与真实连接验证
├─ tools/                    # 单次只读 SQL 查询 Tool
├─ utils/
│  ├─ errors.py              # 统一、面向使用者的错误类型
│  ├─ validation.py          # 参数与只读 SQL 校验
│  └─ database.py            # SQLAlchemy URL、连接、超时和结果转换
├─ sql/                      # MySQL / PostgreSQL 初始化脚本
├─ docs/
├─ docker-compose.yml
└─ requirements.txt
```

## Provider 当前能力

Provider YAML 提供 `database_type`、`host`、`port`、`username`、`password`、`database`、可选 `schema`、`charset`、`connect_timeout` 表单。

Provider Python 仅处理连接配置：校验必填项和数据库类型，使用 SQLAlchemy 建立实际连接并执行 `SELECT 1`。它不执行用户 SQL，不记录密码、连接 URL 或底层堆栈。

当前支持 `mysql` 与 `postgresql`；DM、KingbaseES 未实现。

## Tool 当前能力

Tool 接收 `sql`、`max_rows`（默认 100）、`timeout`（默认 30 秒）、`readonly`。

- 当前仅支持只读模式；`readonly=false` 会被拒绝。
- 允许单条 `SELECT`、`WITH`、`SHOW`、`DESC`、`DESCRIBE`、`EXPLAIN`。
- 拦截 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER`、`TRUNCATE`、`CREATE`、`REPLACE` 等危险关键字及多语句。
- 使用 SQLAlchemy 执行查询。MySQL 使用 `mysql+pymysql`；PostgreSQL 使用 `postgresql+psycopg2`（当前 gevent 兼容路线）。
- MySQL 使用 `MAX_EXECUTION_TIME`，PostgreSQL 使用事务级 `statement_timeout`。
- 读取 `max_rows + 1` 行后截断，返回 `columns`、`row_count`、`rows`、`truncated`、`max_rows`。

## 统一错误处理

统一覆盖参数缺失、不支持数据库类型、连接失败、SQL 执行失败、查询超时、结果限制和只读 SQL 拦截。对使用者仅返回可操作的简短错误信息，日志仅记录异常类别与摘要。

## 已完成验证

- Docker MySQL / PostgreSQL 均 healthy，初始化 SQL 已成功执行。
- 两库均通过 Provider 的真实连接验证（`SELECT 1`）。
- 两库均通过 Tool `SELECT * FROM students`，返回 5 行及正确字段。
- 两库均验证 `max_rows=3` 自动截断，`truncated=true`。
- `DELETE FROM students` 已被只读规则拦截。
- Python 编译、YAML 解析和 Dify CLI 打包通过。

## 下一步

1. 在真实 Dify plugin-daemon 中导入包并执行 Provider 表单与 Workflow 节点联调。
2. 为 MySQL/PostgreSQL 添加自动化测试，覆盖不存在库/表、SQL 语法错误和超时。
3. 以独立适配器和离线依赖交付方式，再规划 DM / KingbaseES 扩展。
