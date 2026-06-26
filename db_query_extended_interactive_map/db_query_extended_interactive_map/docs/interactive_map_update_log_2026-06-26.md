# 2026-06-26 交互式复现地图更新日志

本次更新按 2026-06-23 的地图维护说明执行，目标不是做普通总结页，而是继续维护可交互、可复现、可点击文件的工程地图。

## 更新范围

- 保留 Step 1-12 的历史语义。
- 新增 Step 13-24，覆盖 2026-06-25 平台联调到 2026-06-26 Plugin Core Freeze。
- `timeline-data.js` 改为干净中文，并记录每一步的 `files`、`changes`、`mode` 和命令。
- `file-metadata.js` 补充新增源码、报告、验证证据和 Cockpit 文件的来源、类别、作用与影响。
- `generate_code_snapshots.py` 改为保留既有 Step 1-12 累积快照，只追加 Step 13-24 的真实快照。
- `app.js` 改为从 `CODE_SNAPSHOTS` 动态生成文件树，避免硬编码旧 12 步。

## 交互保持

- Step 滚轮、Change Log、文件树、代码编辑器、tooltip 和调用图继续联动。
- 文件树按父子关系显示目录和文件。
- 本步骤变更文件显示 NEW / MOD 标记。
- 点击文件后显示累积快照，并与上一 Step 做逐行 diff。
- 平台步骤仍能切换到“文件浏览器”，不会让源代码树消失。

## 快照原则

- Step 13-24 的源码和报告快照来自真实工作区。
- 历史 Step 1-12 不用当前文件覆盖，避免伪造历史。
- 大体积或运行时对象继续使用 summary 文本表示。

## 验证

- `code-snapshots.generated.js` 包含 24 个 Step。
- Step 24 累积快照包含 `utils/database.py`、`utils/formatter.py`、`utils/sql_validator.py`。
- Step 9-12 仍能打开此前已经出现的源码文件。
- `app.js` / `timeline-data.js` / `file-metadata.js` 均为离线静态页面使用，不依赖后端。

