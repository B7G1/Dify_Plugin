USE [plugin_test];
GO

SET NOCOUNT ON;

IF OBJECT_ID(N'plugin_test.plugin_test_users', N'U') IS NULL
BEGIN
    CREATE TABLE [plugin_test].[plugin_test_users] (
        [id] int NOT NULL PRIMARY KEY,
        [username] nvarchar(100) NOT NULL,
        [display_name] nvarchar(100) NOT NULL,
        [department] nvarchar(100) NULL,
        [created_at] datetime2(3) NOT NULL
    );
END;

IF OBJECT_ID(N'plugin_test.plugin_test_orders', N'U') IS NULL
BEGIN
    CREATE TABLE [plugin_test].[plugin_test_orders] (
        [id] int NOT NULL PRIMARY KEY,
        [user_id] int NOT NULL,
        [product_name] nvarchar(100) NOT NULL,
        [amount] decimal(18,2) NOT NULL,
        [status] nvarchar(30) NOT NULL,
        [created_at] datetime2(3) NOT NULL,
        CONSTRAINT [FK_plugin_test_orders_users]
            FOREIGN KEY ([user_id]) REFERENCES [plugin_test].[plugin_test_users]([id])
    );
END;

IF OBJECT_ID(N'plugin_test.plugin_test_logs', N'U') IS NULL
BEGIN
    CREATE TABLE [plugin_test].[plugin_test_logs] (
        [id] int NOT NULL PRIMARY KEY,
        [event_type] nvarchar(50) NOT NULL,
        [message] nvarchar(max) NOT NULL,
        [created_at] datetime2(3) NOT NULL
    );
END;

DELETE FROM [plugin_test].[plugin_test_orders];
DELETE FROM [plugin_test].[plugin_test_logs];
DELETE FROM [plugin_test].[plugin_test_users];

INSERT INTO [plugin_test].[plugin_test_users]
    ([id], [username], [display_name], [department], [created_at])
VALUES
    (1, N'alice', N'Alice', N'Engineering', '2026-01-01T09:00:00.000'),
    (2, N'zhang_wei', N'张伟', N'研发部', '2026-01-02T09:00:00.000'),
    (3, N'li_na', N'李娜', N'财务部', '2026-01-03T09:00:00.000'),
    (4, N'emoji_user', N'测试用户🚀', NULL, '2026-01-04T09:00:00.000'),
    (5, N'readonly', N'只读账号测试', N'Quality', '2026-01-05T09:00:00.000'),
    (6, N'limit_probe', N'TOP 截断验证', N'Quality', '2026-01-06T09:00:00.000');

INSERT INTO [plugin_test].[plugin_test_orders]
    ([id], [user_id], [product_name], [amount], [status], [created_at])
VALUES
    (1, 1, N'Laptop', 1200.50, N'completed', '2026-02-01T10:00:00.000'),
    (2, 2, N'数据库课程', 299.00, N'completed', '2026-02-02T10:00:00.000'),
    (3, 2, N'Keyboard', 88.80, N'pending', '2026-02-03T10:00:00.000'),
    (4, 3, N'财务报表', 520.25, N'completed', '2026-02-04T10:00:00.000'),
    (5, 4, N'Emoji Pack 🚀', 9.99, N'completed', '2026-02-05T10:00:00.000'),
    (6, 5, N'Read-only Test', 1.00, N'cancelled', '2026-02-06T10:00:00.000');

INSERT INTO [plugin_test].[plugin_test_logs]
    ([id], [event_type], [message], [created_at])
VALUES
    (1, N'LOGIN', N'Alice logged in', '2026-03-01T11:00:00.000'),
    (2, N'查询', N'中文日志测试', '2026-03-02T11:00:00.000'),
    (3, N'UNICODE', N'Unicode 与 Emoji 🚀', '2026-03-03T11:00:00.000');
GO

