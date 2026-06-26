# db_query_extended 交互式复现地图

这是 Day 1（2026-06-23）本地联调状态的静态展示页。它保留了 `index.html + assets + data` 的轻量结构，不依赖框架。

## 如何打开

请在本目录启动本地静态服务器后访问页面（页面用 `fetch` 读取 `data/*.json`，不建议直接双击 HTML）：

```powershell
cd E:\Dify_Plugin\db_query_extended_interactive_map\db_query_extended_interactive_map
E:\python.exe -m http.server 8088
```

本机已验证 `E:\python.exe` 可运行 Python 3.11。`E:\Scripts\python.exe` 当前会报
`No pyvenv.cfg file`，请不要使用它。地图不依赖插件虚拟环境；如已激活项目环境，也可以使用
`E:\Dify_Plugin\db_query_extended\.venv\Scripts\python.exe -m http.server 8088`。

然后打开 `http://localhost:8088`。

## 页面板块

- 可打开的 `db_query_extended` 根文件夹、文件/目录详情抽屉；
- Provider（蓝）、Tool（紫）与共享 utils（绿）的内部调用图；
- requirements → `.venv` → import → local runtime 的依赖安装链；
- 开发工具图标墙；
- 新电脑 12 步复现时间线。

## 当前边界

已确认：Python/Poetry/SDK/驱动环境、插件安装及 runtime、PostgreSQL 测试库、Provider validation、Workflow 可添加“只读 SQL 查询”节点。

未完成：DM/Dameng 支持、KingbaseES 支持，以及 Workflow 中 `SELECT 1` 和 `SELECT * FROM plugin_test_users LIMIT 5` 的最终实际执行补测。地图不会把这些项目表述为已完成。

## 事实来源

内容来自 `E:\Dify_Plugin\最新报告\04_db_query_extended_DM_credential_diagnosis_2026-06-23.md`、`05_local_plugin_dev_env_and_test_db_2026-06-23.md` 和 `baseline_day1_2026-06-23.md`。源码未直接确认的字段均标为“未确认”。
