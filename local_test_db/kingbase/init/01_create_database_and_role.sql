-- Run as a KingbaseES administrator against the default administrative database.
-- PostgreSQL compatibility mode is required.

CREATE USER plugin_readonly WITH PASSWORD 'plugin_readonly_123';
CREATE DATABASE plugin_test;

REVOKE CREATE ON DATABASE plugin_test FROM PUBLIC;
GRANT CONNECT ON DATABASE plugin_test TO plugin_readonly;
