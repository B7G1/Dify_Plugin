# Release Freeze 与交付资料阶段报告

报告日期：2026-06-29  
阶段：Phase 6 - Release Freeze

## 阶段结论

基于 Phase 5.5 的 35 PASS / 0 FAIL / 0 SKIP，当前 MySQL/PostgreSQL 稳定实现冻结为 `db_query_extended 0.1.0`。本阶段没有新增数据库功能，重点是建立可交付、可校验和可追溯的版本基线。

## 完成事项

1. manifest/meta 版本从 `0.0.1` 更新为 `0.1.0`。
2. 建立 `release/db_query_extended/0.1.0/` 交付目录。
3. 生成版本化 `.difypkg` 和 SHA-256 校验值。
4. 快照保存 Provider、Tool、Workflow 和 Summary 验证证据。
5. 新增 CHANGELOG、Release Notes 和 ADR-0001。
6. 明确 Release Freeze 边界及 Phase 7 扩展门禁。
7. 上一份 Phase 5.5 最新报告已归档。

## 冻结门禁

```text
Provider   4 PASS
Tool      20 PASS
Workflow  11 PASS
Total     35 PASS / 0 FAIL / 0 SKIP
```

## 下一阶段

Phase 7 开始 DM8/KingbaseES Adapter 扩展。新增数据库必须保持 `0.1.0` 的 MySQL/PostgreSQL 行为，并通过完整 `verify_all.ps1` 回归。

## Phase 7.1 运行环境事件（2026-06-30 01:18）

### 故障与判定

`dify-plugin_daemon-1` 出现反复重启，日志核心错误为 `FATAL: database "dify_plugin" does not exist`。直接原因是当前启动的 PostgreSQL 实例缺少 Dify 插件运行时依赖库 `dify_plugin`，不是 `db_query_extended` 插件代码丢失，也不是 MySQL/PostgreSQL 测试库丢失。

上层原因高度疑似为 Compose 项目或容器上下文混用、PostgreSQL 数据卷切换或重建。现场证据是当前同时存在 `dify-*` 与 `docker-*` 两组容器；由于缺少完整的数据卷变更记录，该判断暂不升级为已证实根因。

### 修复证据

补建 `dify_plugin` 数据库后，`plugin_daemon` 恢复正常运行，不再因上述 FATAL 错误持续重启。修复结果进一步确认故障发生在 Dify 运行环境依赖层。

### 预防措施

1. 固定 Compose 项目名。
2. 固定 PostgreSQL 数据目录或命名数据卷。
3. 每次启动前确认当前容器组及其项目归属。
4. 启动前检查 PostgreSQL 中是否存在 `dify_plugin`。
5. 避免混用 `dify-*` 和 `docker-*` 两套环境；确需并存时记录端口、项目名和数据卷映射。

该事件仅表示 plugin daemon 的数据库依赖已恢复，不代表 Dify 主业务环境或 Phase 7.1 已通过。DM8 Workflow API 与最终统一回归仍须以真实验证结果为准。

## 后续诊断更新（2026-06-30 01:40）

进一步检查确认，当前 `dify-db_postgres-1` 的 `pgdata` 于 01:17 新初始化，主库虽然存在 117 张表，但 `accounts=0`、`tenants=0`，因此访问 Console 会进入 `/install`。现场未找到另一份仍由容器或 named volume 挂载的 Dify PostgreSQL 数据目录。

同时确认管理员重新初始化曾因 `/app/api/storage` 为 `root:root` 而失败，API 无法写入租户 RSA 私钥，事务回滚后 `accounts` 仍为空。该目录权限已修正并验证可写，但为了先完成持久化诊断，尚未再次提交管理员初始化。

当前结论为环境 FAIL，DM8 开发暂停。完整证据、根因分级、备份要求和固定方案见：

- `reports/documentation/Phase7_1_DM8_Adapter/dify_environment_diagnosis_2026-06-30.md`
- `db_query_extended/verification/dify_preflight.ps1`
- `db_query_extended/verification/start_dify.ps1`

## 入口

- `release/db_query_extended/0.1.0/README.md`
- `release/db_query_extended/0.1.0/RELEASE_NOTES.md`
- `release/db_query_extended/0.1.0/adr/ADR-0001-release-freeze.md`
- `reports/documentation/Phase6_Release_Freeze/README.md`
