# Phase 7.1 DM8 最终技术报告

状态：**原阶段门禁 PASS；Compatibility PASS；Data Capability PARTIAL PASS**  
最终验收时间：2026-07-01（America/Chicago）

## 验收结论与范围

`db_query_extended` 0.1.1 已完成 Dify 插件、DM8 Provider、Workflow 和服务 API 的既定端到端门禁。最终执行 `verify_all.ps1` 得到：

- Provider：6 PASS / 0 FAIL / 0 SKIP
- Tool：27 PASS / 0 FAIL / 0 SKIP
- Workflow：12 PASS / 0 FAIL / 0 SKIP
- 合计：**45 PASS / 0 FAIL / 0 SKIP**

机器证据位于 `reports/verification/2026-07-01/`。

该结果证明 v1.0 的既定自动化门禁全部通过，但必须区分两类结论：

1. **Environment & Compatibility Validation：PASS**。Dify、插件、DM8 驱动、Provider、Workflow 和 API 能稳定协同运行。
2. **Data Capability Validation：PARTIAL PASS**。真实 DM8 表数据已经通过 WHERE、JOIN、LIMIT、多行查询进入 Workflow，Unicode 和参数绑定有值级断言；但 14 类数据能力尚有 5 项没有真实 artifact，3 项只有摘要证据，不能表述为完整数据能力验收。

数据能力专项矩阵及证据边界见 [`data_retrieval_validation.md`](data_retrieval_validation.md)。

## 第一层：Environment & Compatibility Validation

| 验证对象 | 结论 | 证明内容 |
|---|---|---|
| Docker / Dify 服务 | PASS | API、Worker、Web、Console、Plugin Daemon 能恢复并稳定运行 |
| Migration / ORM | PASS | Dify 元数据迁移与 SQLAlchemy 路径可运行 |
| Dataset / Console | PASS | Console 与数据集相关服务可访问 |
| dmPython / dmSQLAlchemy | PASS | Provider 校验和真实 Tool 查询成功 |
| Plugin / Provider | PASS | 0.1.1 安装并通过 DM8 凭据校验 |
| Workflow / API | PASS | 三节点 Workflow 发布，真实 API 调用成功 |

本层只证明运行兼容性，不单独证明业务数据字段和值均被正确取回。

## 第二层：Data Capability Validation

现有真实证据已经证明：

- `PLUGIN_TEST_USERS`、`PLUGIN_TEST_ORDERS` 的读取、过滤、JOIN、LIMIT 和多行返回；
- `max_rows` 对真实 DM8 查询产生截断结果；
- `中文测试` 经过 DM8 → Adapter → Tool → Workflow API → JSON 后值保持一致；
- dmPython 参数绑定、SQLAlchemy 和 JSON 格式化能够保留 Unicode。

但现有 artifact 多数只保存 `row_count/truncated` 摘要，尚未闭环证明 GROUP BY、NULL、JSON 类型、CLOB 和空结果，也没有为 SELECT/ORDER BY/COUNT 保存足够的字段级结果。因此本层当前不能标记为完整 PASS。

## 已真实执行的数据链路

1. 安装 `db_query_extended` 0.1.1。
2. 使用只读 DM8 测试账号创建 Provider 凭据并通过真实连接校验。
3. 创建并发布三节点 Workflow：用户输入 → 只读 SQL 查询 → 输出。
4. 创建新的 Workflow API Key，并仅在验收进程中临时注入。
5. 通过服务 API 对真实 DM8 测试表执行 SELECT、WHERE、JOIN、LIMIT、COUNT、排序截断和 Unicode 查询。
6. Tool 将结果转换为统一 JSON，Workflow End 节点返回结果；其中 Unicode 有精确值断言，其余多数归档为行数摘要。
7. 五类危险 SQL 拦截属于安全能力，不作为“数据已取回”的替代证据。

## End-to-End Data Flow Validation

```text
DM8 fixture tables
  -> dmPython / SQLAlchemy
  -> DM8 Adapter
  -> Readonly Tool JSON
  -> Dify Workflow
  -> Workflow API
  -> Web UI / End output
```

完整节点—证据映射、14 项数据能力矩阵以及待补证范围见 [`data_retrieval_validation.md`](data_retrieval_validation.md)。

## 验收中发现并关闭的问题

- 首次 Provider 运行使用旧端口 3307/5433，实际端口为 3306/5432；修正后通过。
- 首次 Workflow 套件运行时 `api/nginx/ssrf_proxy` 未运行；通过唯一入口 `start_dify.ps1` 恢复后重跑通过。
- Dify API 与本地 plugin-daemon 的 decode 参数存在大小写兼容差异。固定 override 只读挂载已有的一行兼容修复。

以上问题均未涉及删除数据库、Volume 或旧备份。

## 安全记录

Workflow API Key 和数据库密码均未写入报告、脚本、验收 JSON 或 Git。最终验收仅将 Key 注入当前 PowerShell 进程环境，运行结束即清除。

## 状态

- Phase PASS = YES
- Environment Ready = YES
- Environment & Compatibility Validation = PASS
- Data Capability Validation = PARTIAL PASS

`Phase PASS` 保留原 v1.0 自动化门禁的历史含义；不得将其解释为 14 类 DM8 数据能力均已完成值级验收。
