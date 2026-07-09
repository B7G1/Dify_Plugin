SET NOCOUNT ON;

IF DB_ID(N'plugin_test') IS NULL
BEGIN
    CREATE DATABASE [plugin_test];
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'plugin_readonly')
BEGIN
    DECLARE @create_login nvarchar(max) =
        N'CREATE LOGIN [plugin_readonly] WITH PASSWORD = ' + QUOTENAME(N'$(ReadonlyPassword)', '''') +
        N', CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF;';
    EXEC sys.sp_executesql @create_login;
END;
GO

USE [plugin_test];
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'plugin_test')
BEGIN
    EXEC(N'CREATE SCHEMA [plugin_test] AUTHORIZATION [dbo];');
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'plugin_readonly')
BEGIN
    CREATE USER [plugin_readonly] FOR LOGIN [plugin_readonly];
END;
GO

GRANT CONNECT TO [plugin_readonly];
-- Remove the overly broad legacy DENY. CONTROL includes SELECT, and an
-- explicit DENY overrides the schema-level GRANT SELECT below.
REVOKE CONTROL ON SCHEMA::[plugin_test] FROM [plugin_readonly];
GRANT SELECT ON SCHEMA::[plugin_test] TO [plugin_readonly];
DENY INSERT ON SCHEMA::[plugin_test] TO [plugin_readonly];
DENY UPDATE ON SCHEMA::[plugin_test] TO [plugin_readonly];
DENY DELETE ON SCHEMA::[plugin_test] TO [plugin_readonly];
DENY ALTER ON SCHEMA::[plugin_test] TO [plugin_readonly];
GO
