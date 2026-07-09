# Environment validation

时间：2026-06-23（真实检查）

- `dify-plugin_daemon-1`：Up，端口 5002/5003；管理接口和 `management/tool` 返回 200。
- `dify-api-1`、`dify-worker-1`、`dify-web-1`、`dify-nginx-1`：Up。
- 本地插件：`li_zijun/db_query_extended` 已被 daemon 的管理接口识别。
- Provider：此前 PostgreSQL Provider validation 已成功；本轮 `SELECT 1` Workflow 成功进一步证明当前凭据可用。
- `db-query-extended-postgres`：Up (healthy)，宿主机 5433→5432。
- 注意：同时存在 `docker-*` 重复环境；本验收使用的是 `dify-*` 平台和 `db-query-extended-postgres` 测试库。
