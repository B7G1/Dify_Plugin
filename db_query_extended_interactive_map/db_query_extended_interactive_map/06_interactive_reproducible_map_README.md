# db_query_extended 交互式复现地图说明

本目录提供一个静态 HTML 页面，用来展示 `db_query_extended` 插件从 0 到本地联调模板的形成过程。

## 打开方式

直接打开：

```text
index.html
```

即可。

## 页面包含

- 插件目录树：点击每个文件查看创建方式、使用软件、模板依据、作用和调用关系；
- 文件连线图：展示 Provider、Tool、utils、SQLAlchemy、数据库之间的调用关系；
- 第三方工具图标墙：解释 Python、Docker、WSL、Dify Plugin CLI、PostgreSQL 等工具为什么需要；
- 依赖安装图：展示 requirements.txt → pip install → .venv → import test → runtime；
- 新电脑复现路线图：从 Python 3.11 到 Dify Provider 校验的步骤；
- 踩坑提醒：DM 参数、localhost、业务库/测试库、双 compose 环境等问题。

## 当前边界

当前模板支持：

- MySQL
- PostgreSQL

当前模板不支持：

- DM / Dameng / 达梦
- KingbaseES

Workflow 中已经能添加“只读 SQL 查询”节点，但实际 SQL 执行结果仍应继续补测。
