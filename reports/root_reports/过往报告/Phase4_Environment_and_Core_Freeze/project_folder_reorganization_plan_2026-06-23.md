# E:\Dify_Plugin 安全整理方案（仅计划，2026-06-23）

## 结论

当前目录可整理，但**本轮不执行任何移动、重命名、删除、重打包、提交或推送**。先把链接、构建命令与包来源记录清楚，避免把“整洁”变成一次新的状态丢失事件。

## 建议目标结构

```text
E:\Dify_Plugin
├── plugins/
│   └── db_query_extended/
├── interactive_maps/
│   └── db_query_extended_interactive_map/
├── analysis/
│   └── junjiem-db_query_0.0.11/
├── tests/
│   └── test_tool_schema/
├── tools/
│   └── dify-plugin/windows-amd64/
├── packages/
│   ├── db_query_extended/
│   ├── reference/
│   └── tests/
├── logs/
│   └── environment_checks/
├── 最新报告/
│   ├── research/                 # 当前 01/02/03 资料可在确认后归入
│   ├── diagnostics/              # 04、05 与后续诊断报告
│   ├── baselines/                # baseline_day1
│   ├── exports/                  # HTML 导出物
│   ├── logs/
│   └── 06_交互式复现地图/         # 地图 README/报告索引（非网页运行文件）
└── archive/
    ├── reports/
    └── local-state/
```

`analysis/junjiem-db_query_0.0.11/` 与 `最新报告/logs/` 已基本合理，可先保持原位。建议把地图网页作为一个完整目录整体迁移，不拆散 `index.html`、`assets/`、`data/`。

## 建议执行顺序（须用户确认后）

1. 备份/记录：先生成 `git status --short`、关键包 SHA-256、插件构建命令和现有绝对/相对路径清单。
2. 链接审计：用全文搜索检查所有 `README.md`、报告 Markdown、HTML 中对 `db_query_extended/`、`.difypkg`、`最新报告/`、`assets/`、`data/` 的引用。
3. 处理地图双层目录：决定外层仅作容器目录，还是把内层内容提升一层。此步会改变入口 URL，必须更新文档再移动。
4. 以“复制 → 验证 → 用户确认 → 再删除旧副本”的方式迁移源码、地图、测试项目与包；不要一次性批量移动。
5. 每迁移一组，重新打开地图、执行插件构建/安装前检查，并更新 `最新报告/README.md` 索引。
6. 最后才讨论空 `.Rhistory` 与疑似重复 CLI 的归档/删除；重复 EXE 先做哈希比较。

## 移动前必须更新或验证的断链点

| 位置 | 当前依赖 | 移动后风险 | 处理方式 |
|---|---|---|---|
| 地图 `index.html` | `assets/style.css`、`assets/app.js`、JS 中的 `data/*.json` | 若只移动其中一层会白屏/无法读 JSON | 保持网页项目目录整体移动；在本地 HTTP 服务下打开验证。 |
| 地图 README | 当前绝对打开目录 | 移动后启动命令失效 | 更新 `cd` 路径和文档链接。 |
| 插件源码与 `.difypkg` | 构建上下文/手工安装路径 | 构建命令、Dify 本地上传路径可能失效 | 记录构建命令，移动后重新构建或明确包版本。 |
| 报告 Markdown / `最新报告/README.md` | 可能有相对链接、同目录 HTML 导出 | 文件重定位会断开引用 | 移动前全文检索；更新链接后以 Markdown 渲染器检查。 |
| 历史报告 `过往报告/README.md` | 报告子目录相对路径 | 迁入 archive 后链接可能断裂 | 先保留原层级或批量重写链接。 |
| `dify-plugin*.exe` | `.gitignore` 与可能的脚本/PATH | CLI 命令找不到 | 更新 `.gitignore` 和文档；不承诺自动更新 PATH。 |

## Git 与交付建议

当前分支是 `main`，远端为 `origin`。工作区已有与本任务无关的修改、删除和未跟踪内容，先不要把它们混入本次文档提交。

在用户确认范围后，可考虑单独、可审查的提交：

```text
docs: add interactive db_query_extended reproducible map
docs: add project folder inventory and reorganization plan
```

本轮未执行 `git add`、commit 或 push。

## 明确不做的事项

- 不执行 `docker compose down -v`、`rm -rf`、volume 删除、数据库重置；
- 不触碰 `/home/zli2759/projects/dify-dm/docker/volumes`；
- 不修改插件功能、不重装插件、不影响当前 Dify 最小重建平台。
