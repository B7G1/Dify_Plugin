SELECT version() AS kingbase_version;
SHOW server_encoding;
SHOW client_encoding;
SHOW search_path;

SELECT 1 AS select_one;
SELECT * FROM plugin_test.plugin_test_users ORDER BY id LIMIT 5;
SELECT COUNT(*) AS user_count FROM plugin_test.plugin_test_users;
SELECT '中文测试' AS unicode_text;
SELECT CURRENT_TIMESTAMP AS current_timestamp;

SELECT has_database_privilege(current_user, 'plugin_test', 'CONNECT') AS can_connect;
SELECT has_schema_privilege(current_user, 'plugin_test', 'USAGE') AS can_use_schema;
SELECT has_schema_privilege(current_user, 'plugin_test', 'CREATE') AS can_create_in_schema;
