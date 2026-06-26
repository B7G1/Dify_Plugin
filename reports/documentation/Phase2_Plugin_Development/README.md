# Phase 2 插件开发

Phase 2 完成了 `db_query_extended` 的第一版可运行插件。

## 做了什么

- 创建插件基础结构。
- 编写 Provider 和 Tool 文件。
- 接入 MySQL / PostgreSQL。
- 增加只读 SQL 校验。
- 建立本地数据库和验证脚本。

## 为什么重要

这一阶段证明插件不只是目录模板，而是可以本地执行查询并返回稳定 JSON 的工具。同时也确立了安全底线：插件只做只读查询，不执行写操作。

## 主要产出

- `db_query_extended/manifest.yaml`
- `db_query_extended/provider/`
- `db_query_extended/tools/`
- `db_query_extended/utils/`
- `db_query_extended/verify_plugin.ps1`
- `local_test_db/`

## 下一阶段

Phase 3 从本地正确性推进到真实 Dify 平台联调。
