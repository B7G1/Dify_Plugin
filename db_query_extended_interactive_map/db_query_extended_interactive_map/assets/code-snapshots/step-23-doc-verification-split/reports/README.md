# 报告体系

本目录分为三条线，分别服务不同读者。

## Documentation：给人读

位置：`reports/documentation/`

用于导师汇报、新成员接手、项目展示和后续维护。这里解释项目为什么这样设计、每天做了什么、遇到什么问题、怎么解决、下一步是什么。

## Verification：给机器和验收看

位置：`reports/verification/`

用于保存 JSON、日志、PowerShell transcript、Docker 输出、plugin-daemon 输出、Workflow 输出和自动化验证结果。

## HTML Reports：统一入口和交互地图

位置：`reports/html_reports/`

这里包含 Project Cockpit 和交互式步骤地图：

- [Project Cockpit](html_reports/2026-06-24/project_dashboard.html)：整个项目的驾驶舱。
- [交互式步骤地图](html_reports/2026-06-26_interactive_step_map/project_map.html)：从旧 Step 12 继续展示 Step 13 到 Step 24 的代码和文件变化。

第一次接触项目的人建议先打开 Project Cockpit，再阅读 Documentation。需要证明功能真的通过时，再进入 Verification。

