# db_query_extended 交互式复现地图：全流程与后续复用说明

更新日期：2026-06-23  
地图目录：`E:\Dify_Plugin\db_query_extended_interactive_map\db_query_extended_interactive_map`

## 1. 这张地图的目的

这不是静态项目报告，而是一个离线可打开的、可交互的“从模板到 Dify 平台联调”的复现地图。它必须帮助后续汇报快速回答：

- 插件目录中每个关键目录/文件何时出现、由什么工具创建或完善；
- 本地测试、离线依赖、打包、Dify 安装、Provider 校验和 Workflow 分别发生在什么阶段；
- 当前已验证边界与尚未完成边界；
- 当前工作仓库和地图中的步骤状态是否一致。

## 2. 不可牺牲的交互与视觉要求

后续维护不得把地图退化为普通 Markdown 或静态报告。必须保留并继续完善：

- 暗色科技风、清楚的信息层级与适当留白；
- 左侧预览、右侧步骤滚轮/说明/Change Log 的工作台布局；
- Step 滚轮选择器、平滑切换、淡入、NEW/MOD/删除状态高亮；
- 文件浏览器/平台场景可切换标签；
- 文件/目录/平台对象 hover tooltip；
- 文件、步骤、Change Log、代码编辑器、调用图之间的联动；
- 代码编辑器的滚动、顶部/底部淡出、逐行 Diff；
- 调用图 hover 高亮、无关节点弱化、点击详情；
- 平滑滚动与闪烁定位。

颜色语义：蓝色是 Provider/配置，紫色是 Tool，绿色是 shared utils/新增，黄色是修改，红色是删除，灰色是依赖/平台对象。

## 3. 真实工作仓库范围

真实插件目录：`E:\Dify_Plugin\db_query_extended`

地图必须至少体现下列真实内容，而不能只展示简化骨架：

- 模板层：`.github/`、`_assets/`、`.env.example`、`.gitignore`、`GUIDE.md`、`PRIVACY.md`；
- 插件层：`main.py`、`manifest.yaml`、`provider/`、`tools/`、`utils/`；
- 本地测试层：`docker-compose.yml`、`sql/init_mysql.sql`、`sql/init_postgres.sql`；
- 环境层：`.venv/`、`__pycache__/`；
- 打包层：`dist/`、`db_query_extended.difypkg`、`.difyignore`；
- 离线依赖层：`requirements.txt`、`requirements.download.txt`、`wheels/`；
- 文档层：`docs/`、`README.md`。

目录树必须按照真实父子关系呈现：例如 `provider/` 后面是 Provider 文件，`sql/` 后面是初始化 SQL，`docs/` 后面是文档。不能按路径字母排序后把子文件散落在列表末尾。

## 4. 当前真实时间线（12 步）

1. Dify 模板与基础资产；
2. 本地测试底座：入口、Compose、MySQL/PostgreSQL 初始化 SQL；
3. 项目 Python 环境：`.venv`；
4. Provider / Tool / Utils 核心实现；
5. 首次打包：README、`dist/`、`.difypkg`；
6. 离线依赖补齐：requirements、`.difyignore`、wheels；
7. 开发文档与设计记录；
8. Dify 平台最小恢复；
9. 安装本地插件并确认 runtime ready；
10. PostgreSQL Provider 校验成功；
11. Workflow 添加“只读 SQL 查询”节点；
12. Workflow SQL 最终补测。

已确认：MySQL/PostgreSQL Provider 模型、PostgreSQL 测试库、Provider validation、API ↔ daemon、Workflow 节点可添加。  
未完成：DM/Dameng、KingbaseES、Workflow SQL 最终实际执行验收。

## 5. 快照数据模型（必须遵守）

代码展示不得使用硬编码示意代码冒充真实文件。数据入口：

- `assets/timeline-data.js`：12 步真实时间线、Change Log、场景类型；
- `assets/file-metadata.js`：来源、作用、关联、影响；
- `assets/code-snapshots/`：每一步增量保存的关键文本副本；
- `assets/code-snapshots.generated.js`：离线页面使用的**累积状态**快照；
- `scripts/generate_code_snapshots.py`：从真实插件目录刷新快照。

关键原则：磁盘上的 `assets/code-snapshots/step-*` 可以是增量审计材料；浏览器读取的 `CODE_SNAPSHOTS` 必须是累积状态。因此 Step 9 打开一个 Step 4 已出现的源码文件时，应显示完整内容、但不高亮；不能说“该文件尚未出现”。

`.venv/`、`wheels/`、`.difypkg`、`dist/` 等大体积/二进制对象只保存 `summary.txt`，不能全量复制。

刷新快照命令：

```powershell
E:\python.exe E:\Dify_Plugin\db_query_extended_interactive_map\db_query_extended_interactive_map\scripts\generate_code_snapshots.py
```

如果无法从当前工作区还原历史版本，摘要必须写“待确认”；不能伪造旧代码。

## 6. 页面模块与联动规则

### Step 工作台

- 文件浏览器标签：展示截至当前 Step 已出现的完整仓库树；只把本步变化标为 NEW/MOD；
- 平台场景标签：在 Step 8–12 用 Dify/Docker 风格模拟 UI，不能只输出文本；
- 用户即使处于平台 Step，也能切回文件浏览器交互；
- 点击 Step 更新预览、Change Log、代码编辑器；
- 点击 Change Log 定位并打开本步最相关快照。

### 文件浏览器

- 文件夹展开后，子项需缩进并带竖向引导线；
- hover 显示来源、作用、关联、类别、运行影响与本步改动状态；
- 点击文件打开代码编辑器；若当前 Step 未出现，提示首次出现 Step；
- 文件树最后一步应与当前工作仓库的主要结构一致。

### 代码编辑器

- 文件来源必须是 `CODE_SNAPSHOTS`；
- 和上一 Step 同路径文件做简单逐行 diff：`+` 新增、`-` 删除、`~` 修改；
- 首次出现的文件全文新增；未改动的继承文件正常显示；
- 窗口不应过高，允许滚动，靠近顶部/底部可淡出；
- 文件树和编辑器要物理上接近，点击后不应要求用户滚动很远寻找代码。

### Internal Call Graph

- 不允许 `nth-of-type`、手工 `top/left` 或 `!important` 修核心坐标；
- HTML 节点由正常 Grid/Flex 布局，SVG overlay 用 `getBoundingClientRect()` 自动计算贝塞尔路径；
- 页面加载、resize、hover 状态变化后重新计算边；
- hover 节点高亮相关边/节点并弱化无关节点；点击节点打开文件详情与代码；
- 图中应额外解释 Provider 路径、Tool 路径、依赖/驱动以及数据库支持边界。

## 7. 文件与职责

| 文件 | 职责 |
|---|---|
| `index.html` | 页面结构、模块锚点、外部数据脚本加载顺序 |
| `assets/style.css` | 主要暗色视觉与响应式布局 |
| `assets/app.js` | 渲染、联动、滚轮、tooltip、Diff、自动 SVG 连线 |
| `assets/timeline-data.js` | 真实 12 步数据 |
| `assets/file-metadata.js` | 文件元信息 |
| `assets/code-snapshots.generated.js` | 离线可用的累积快照数据 |
| `scripts/generate_code_snapshots.py` | 从真实插件目录刷新快照 |
| `docs/interactive_map_update_log.md` | 简短技术更新日志 |

## 8. 验收清单

- 离线打开 `index.html` 能显示快照，不依赖后端；
- Step 切换仍有动画，滚轮仍可用；
- 文件树不会因平台步骤而为空；
- 所有主要目录按父子关系显示；
- Step 9–12 可打开先前出现的完整源码；
- 平台标签显示前端组件式场景，不是字符画；
- tooltip、Change Log、代码 Diff、调用图仍联动；
- 调用图 resize 后端点仍贴近节点；
- 浏览器控制台无错误；
- 不触碰 Dify volume、业务库、插件安装与 Docker 容器。
