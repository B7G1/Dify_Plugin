# Phase 7 DM8 Architecture Notes

## 已实现结构

- Adapter：`db_query_extended/utils/adapters/dm.py`。
- 发现机制：`utils.adapters.get_database_adapter("dm")`。
- Provider 类型：`database_type=dm`，默认端口 `5236`。
- Schema：凭据中的 `database` 映射为 DM8 当前 Schema。
- 安全模型：`PLUGIN_TEST_OWNER` 持有对象，`PLUGIN_TEST_USER` 仅有会话和 SELECT 权限。
- 运行时：固定 `dify` Compose 项目的 `plugin_daemon` 只读挂载官方 Linux DM client，并注入 `DM_HOME` 与 `LD_LIBRARY_PATH`。
- Workflow 契约：Start(`sql`, `max_rows`) → Tool → End(`result=Tool.json`)。

该结构复用既有 SQL 校验、结果格式化和 Tool 主流程，没有为 DM8 分叉业务协议。Phase 7.1 原门禁状态：**PASS**；该架构结论不代替数据能力逐项验收，后者当前为 PARTIAL PASS。
