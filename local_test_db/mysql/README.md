# MySQL 初始化

`init.sql` 由官方 `mysql:8.4` 镜像仅在数据卷首次创建时自动执行。它创建三个表、索引、外键和确定性测试数据。

重跑初始化请从 `local_test_db` 目录执行 `docker compose down -v` 后再执行 `docker compose up -d`；不要在运行中的数据库中手工重复执行脚本。
