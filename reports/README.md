# 报告体系

本目录分为三条线，分别服务不同读者。

## Documentation：给人读

位置：`reports/documentation/`

用于导师汇报、新成员接手、项目展示和后续维护。这里解释项目为什么这样设计、每天做了什么、遇到什么问题、怎么解决、下一步是什么。

## Verification：给机器和验收看

位置：`reports/verification/`

用于保存 JSON、日志、PowerShell transcript、Docker 输出、plugin-daemon 输出、Workflow 输出和自动化验证结果。

## Project Cockpit：统一入口

位置：`reports/html_reports/2026-06-24/project_dashboard.html`

这是整个项目的驾驶舱。第一次接触项目的人可以从这里进入 Documentation、Verification、Timeline、Architecture、Assets、Knowledge Base 和 Recovery。

## 使用建议

- 想理解项目过程：先读 Documentation。
- 想证明功能通过：查看 Verification。
- 想快速总览全局：打开 Project Cockpit。
