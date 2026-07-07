# Phase 7 DM8 Lessons Learned

## 2026-06-30

- Dify plugin-daemon 是 Linux/Python 3.12，Windows `dmPython` wheel 不能用于真实运行时；最终使用官方 Linux 驱动与固定 DM client runtime。
- DM8 crypto 依赖必须随 `plugin_daemon` 的稳定启动环境提供，不能只验证 wheel 可以 import。
- Workflow 重建后必须固定输出契约：End 输出变量名为 `result`，值绑定 Tool 的 `json`。
- 插件重装或 Start 变量重建会使节点变量 ID 失效，必须重新绑定 `sql` 和 `max_rows`。
- API Key 只允许通过进程环境变量临时注入，禁止进入报告、脚本、证据或 Git。

原阶段门禁状态：**PASS**；Compatibility PASS，Data Capability PARTIAL PASS。完整过程见 [`../../Phase7_1_DM8_Adapter/README.md`](../../Phase7_1_DM8_Adapter/README.md)。
