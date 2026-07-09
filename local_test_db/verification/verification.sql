-- Run unchanged in both MySQL and PostgreSQL after selecting database plugin_test.
-- Required acceptance checks
SELECT * FROM plugin_test_users ORDER BY id LIMIT 5;
SELECT COUNT(*) AS user_count FROM plugin_test_users;
SELECT * FROM plugin_test_orders WHERE status = 'completed' ORDER BY id;
SELECT u.username, o.product_name, o.amount
FROM plugin_test_users AS u
JOIN plugin_test_orders AS o ON u.id = o.user_id
ORDER BY o.id;

-- Additional reproducible checks
SELECT department, AVG(salary) AS average_salary
FROM plugin_test_users
GROUP BY department
ORDER BY department;
SELECT * FROM plugin_test_logs
WHERE created_at >= '2025-02-05 00:00:00'
ORDER BY created_at DESC
LIMIT 5;
