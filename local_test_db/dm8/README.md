# DM8 本地测试环境

本目录为 Phase 7.1 准备真实 DM8 验收数据。表结构、行数和数值/时间数据与 MySQL/PostgreSQL 保持一致：users 12、orders 24、logs 10。当前 Windows DIsql 环境对非 ASCII 脚本内容存在编码问题，因此姓名临时使用等价 ASCII 文本；Unicode 将在驱动参数绑定阶段单独验证。

## 安全模型

| 用户 | 用途 | 密码 | 权限 |
| --- | --- | --- | --- |
| `PLUGIN_TEST_OWNER` | 持有测试 Schema 和三张表 | `PluginOwner_2026!` | 不用于 Adapter |
| `PLUGIN_TEST_USER` | Provider/Tool/Workflow 真实验收 | `PluginRead_2026!` | `CREATE SESSION` + 三张表 SELECT |

这些凭据只用于本机测试。Adapter、Dify Provider 和自动化脚本只能使用 `PLUGIN_TEST_USER`。

DM8 每个用户有同名默认 Schema，因此表放在 `PLUGIN_TEST_OWNER`，只读用户查询时使用 Schema 前缀，或由 Adapter 设置当前 Schema。

## 当前实例

```text
Service: DmServiceDMSERVER
Host: 127.0.0.1
Port: 5236
DM_HOME: C:\dmdbms
```

## 执行顺序

### 方式一：disql

启动交互式客户端，按提示输入你自己的管理员账号和密码：

```powershell
& 'C:\dmdbms\bin\disql.exe'
```

进入 `SQL>` 后执行：

```sql
START E:\Dify_Plugin\local_test_db\dm8\01_admin_setup.sql
START E:\Dify_Plugin\local_test_db\dm8\02_admin_audit.sql
```

退出管理员会话，不要把管理员密码写入命令或脚本。重新启动 `disql.exe`，使用：

```text
用户名：PLUGIN_TEST_USER
密码：PluginRead_2026!
地址：127.0.0.1:5236
```

登录后执行：

```sql
START E:\Dify_Plugin\local_test_db\dm8\03_readonly_verify.sql
```

### 方式二：DM Manager

使用管理员连接打开并执行 `01_admin_setup.sql`、`02_admin_audit.sql`；再新建 `PLUGIN_TEST_USER` 连接执行 `03_readonly_verify.sql`。

## 验收标准

- `PLUGIN_TEST_USERS`：12 行。
- `PLUGIN_TEST_ORDERS`：24 行，其中 completed 14 行。
- `PLUGIN_TEST_LOGS`：10 行。
- 权限审计只显示 `CREATE SESSION` 系统权限和三条 `SELECT` 对象权限。
- 只读脚本的 SELECT 1、LIMIT、COUNT、WHERE、JOIN、NULL、DECIMAL、TIMESTAMP、Unicode 全部成功。
- 不使用 SYSDBA 或其他管理员账号运行 Adapter、Provider、Tool、Workflow。

## 重跑说明

`01_admin_setup.sql` 可重复执行。开头按顺序运行 `DROP USER IF EXISTS ... CASCADE`，先删除 reader，再删除 owner 及其 Schema 对象，随后重建确定性数据。此清理仅针对名称固定的本地测试用户。

三个 SQL 文件均执行 `SET DEFINE OFF`，防止 DIsql 把字符串中的 `&` 解释为变量；当前数据同时使用 `Emma and Co.`，不再依赖该特殊字符。

官方参考：

- [用户与模式的关系](https://eco.dameng.com/document/dm/zh-cn/start/dm-user-mode-relation.html)
- [dmPython 安装](https://eco.dameng.com/document/dm/zh-cn/pm/dmpython-installation)
- [SQLAlchemy 框架](https://eco.dameng.com/document/dm/zh-cn/app-dev/python-SQLAlchemy.html)
