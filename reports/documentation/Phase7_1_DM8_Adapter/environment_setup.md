# Phase 7.1 DM8 测试环境准备

## 状态

首次执行在部分数据插入阶段失败：Windows DIsql 对中文脚本文本解码异常，并将 `&` 识别为 DEFINE 变量。

修订版脚本使用 `DROP USER IF EXISTS ... CASCADE` 清理半执行状态，执行 `SET DEFINE OFF`，并将测试字符串临时改为 ASCII。修订版已完成真实执行，DM8 测试环境准备阶段 PASS。ASCII 初始化数据只用于规避 Windows DIsql 文件编码问题，不取消后续 Unicode 参数绑定、Tool JSON 和 Workflow API UTF-8 验收要求。

Phase 7.1 原自动化门禁于 2026-06-30 标记为 **PASS**；最终证据为 `reports/verification/2026-06-30/workflow_dm8_result.json`。该结论证明环境与既定 Workflow 用例通过，不等价于全部数据能力均有字段级证据；专项审计见 [`data_retrieval_validation.md`](data_retrieval_validation.md)。

## 运行环境故障记录（2026-06-30 01:18）

### 现象

`dify-plugin_daemon-1` 反复重启，日志核心错误为：

```text
FATAL: database "dify_plugin" does not exist
```

### 原因判定

直接原因是当前启动的 PostgreSQL 实例中缺少 Dify 插件运行时依赖库 `dify_plugin`。该故障不是 `db_query_extended` 插件代码丢失，也不是 MySQL/PostgreSQL 测试库丢失。

更上层原因高度疑似为 Compose 项目或容器上下文混用、PostgreSQL 数据卷切换或重建。现场同时存在 `dify-*` 与 `docker-*` 两组容器，这是当前判断的重要证据；由于尚未取得数据卷切换或重建的完整操作记录，上层原因保留为“高度疑似”，不写成已证实结论。

### 修复证据

在当前 PostgreSQL 实例中补建 `dify_plugin` 数据库后，`plugin_daemon` 恢复正常运行，不再因上述 FATAL 错误持续重启。这证明本次故障位于 Dify 运行环境依赖层，而非 `db_query_extended` Adapter 或既有数据库测试数据层。

### 预防措施

1. 固定 Docker Compose 项目名，所有启动、停止、检查和恢复命令使用同一个项目名。
2. 固定 PostgreSQL 数据目录或命名数据卷，避免不同 Compose 环境连接到不同数据卷。
3. 启动前检查当前容器组，确认实际操作目标与预期环境一致。
4. 启动前检查 PostgreSQL 中是否存在 `dify_plugin` 数据库，并将该检查加入环境健康检查。
5. 避免同时混用 `dify-*` 与 `docker-*` 两套容器环境；如必须并存，应明确项目名、端口和数据卷归属并形成书面映射。

## 设计

采用 Owner/Reader 分离：`PLUGIN_TEST_OWNER` 持有数据，`PLUGIN_TEST_USER` 只有三张表的 SELECT 权限。任何 Provider、Tool、Workflow 或自动化连接都禁止使用管理员账号。

## 文件

- `local_test_db/dm8/01_admin_setup.sql`：创建用户、表、数据和 SELECT 授权。
- `local_test_db/dm8/02_admin_audit.sql`：检查账号状态和对象权限。
- `local_test_db/dm8/03_readonly_verify.sql`：只读账号执行真实查询验收。
- `local_test_db/dm8/README.md`：复原步骤、凭据、命令和验收标准。

## 与现有基线的一致性

三张表、字段、12/24/10 行数据及 Unicode/NULL/DECIMAL/TIMESTAMP 案例来自 `local_test_db/mysql/init.sql` 和 `local_test_db/postgres/init.sql`。DM8 只做语法和类型映射，不改变业务数据。

## 最终状态

DM8 环境、Provider、既定 Tool、Unicode 和 Workflow API 用例均已真实通过。最终 Workflow API 结果为 `12 PASS / 0 FAIL / 0 SKIP`；Compatibility 为 PASS，Data Capability 因部分值级 artifact 缺口为 PARTIAL PASS。
