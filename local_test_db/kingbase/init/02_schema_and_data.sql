-- Run as a KingbaseES administrator while connected to database plugin_test.

CREATE SCHEMA plugin_test;

CREATE TABLE plugin_test.plugin_test_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO plugin_test.plugin_test_users (id, username, display_name) VALUES
    (1, 'alice', 'Alice'),
    (2, 'zhang_wei', '张伟'),
    (3, 'li_na', '李娜'),
    (4, 'emoji_user', '测试用户🚀'),
    (5, 'readonly', '只读账号测试'),
    (6, 'limit_probe', '截断验证');

REVOKE ALL ON SCHEMA plugin_test FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA plugin_test FROM PUBLIC;
GRANT USAGE ON SCHEMA plugin_test TO plugin_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA plugin_test TO plugin_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA plugin_test GRANT SELECT ON TABLES TO plugin_readonly;

ALTER ROLE plugin_readonly SET search_path TO plugin_test;
