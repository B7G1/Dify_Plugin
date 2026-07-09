USE [plugin_test];
GO

SET NOCOUNT ON;

SELECT @@VERSION AS [sqlserver_version];
SELECT 1 AS [select_one];
SELECT TOP 5 * FROM [plugin_test].[plugin_test_users] ORDER BY [id];
SELECT COUNT(*) AS [user_count] FROM [plugin_test].[plugin_test_users];
SELECT N'中文测试 🚀' AS [unicode_text];

SELECT u.[username], o.[product_name], o.[amount]
FROM [plugin_test].[plugin_test_users] AS u
JOIN [plugin_test].[plugin_test_orders] AS o ON o.[user_id] = u.[id]
ORDER BY o.[id];

SELECT u.[department], COUNT(*) AS [user_count]
FROM [plugin_test].[plugin_test_users] AS u
GROUP BY u.[department]
ORDER BY u.[department];

DECLARE @user_count int = (SELECT COUNT(*) FROM [plugin_test].[plugin_test_users]);
DECLARE @order_count int = (SELECT COUNT(*) FROM [plugin_test].[plugin_test_orders]);
DECLARE @log_count int = (SELECT COUNT(*) FROM [plugin_test].[plugin_test_logs]);

IF @user_count <> 6 THROW 51001, 'Expected 6 users.', 1;
IF @order_count <> 6 THROW 51002, 'Expected 6 orders.', 1;
IF @log_count <> 3 THROW 51003, 'Expected 3 logs.', 1;

DECLARE @can_select int = HAS_PERMS_BY_NAME(N'plugin_test.plugin_test_users', N'OBJECT', N'SELECT');
DECLARE @can_insert int = HAS_PERMS_BY_NAME(N'plugin_test.plugin_test_users', N'OBJECT', N'INSERT');
DECLARE @can_update int = HAS_PERMS_BY_NAME(N'plugin_test.plugin_test_users', N'OBJECT', N'UPDATE');
DECLARE @can_delete int = HAS_PERMS_BY_NAME(N'plugin_test.plugin_test_users', N'OBJECT', N'DELETE');

SELECT
    @can_select AS [can_select],
    @can_insert AS [can_insert],
    @can_update AS [can_update],
    @can_delete AS [can_delete];

IF @can_select <> 1 THROW 51004, 'Readonly user must have SELECT.', 1;
IF @can_insert <> 0 THROW 51005, 'Readonly user must not have INSERT.', 1;
IF @can_update <> 0 THROW 51006, 'Readonly user must not have UPDATE.', 1;
IF @can_delete <> 0 THROW 51007, 'Readonly user must not have DELETE.', 1;

-- Prove the effective permissions with real write attempts. Every statement
-- runs inside a transaction and must fail with a permission error. Nothing is
-- persisted even if a future permission regression accidentally allows it.
DECLARE @insert_blocked bit = 0;
BEGIN TRY
    BEGIN TRANSACTION;
    INSERT INTO [plugin_test].[plugin_test_logs] ([id], [event_type], [message], [created_at])
    VALUES (9999, N'PERMISSION_PROBE', N'must not persist', SYSUTCDATETIME());
    ROLLBACK TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    IF ERROR_NUMBER() IN (229, 230)
        SET @insert_blocked = 1;
    ELSE
        THROW;
END CATCH;
IF @insert_blocked <> 1 THROW 51008, 'Readonly user unexpectedly allowed INSERT.', 1;

DECLARE @update_blocked bit = 0;
BEGIN TRY
    BEGIN TRANSACTION;
    UPDATE [plugin_test].[plugin_test_users] SET [display_name] = N'must not persist' WHERE [id] = 1;
    ROLLBACK TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    IF ERROR_NUMBER() IN (229, 230)
        SET @update_blocked = 1;
    ELSE
        THROW;
END CATCH;
IF @update_blocked <> 1 THROW 51009, 'Readonly user unexpectedly allowed UPDATE.', 1;

DECLARE @delete_blocked bit = 0;
BEGIN TRY
    BEGIN TRANSACTION;
    DELETE FROM [plugin_test].[plugin_test_orders] WHERE [id] = 1;
    ROLLBACK TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    IF ERROR_NUMBER() IN (229, 230)
        SET @delete_blocked = 1;
    ELSE
        THROW;
END CATCH;
IF @delete_blocked <> 1 THROW 51010, 'Readonly user unexpectedly allowed DELETE.', 1;

SELECT
    @insert_blocked AS [insert_blocked],
    @update_blocked AS [update_blocked],
    @delete_blocked AS [delete_blocked];

SELECT N'PHASE11_SQLSERVER_VERIFY_PASS' AS [verification_status];
GO
