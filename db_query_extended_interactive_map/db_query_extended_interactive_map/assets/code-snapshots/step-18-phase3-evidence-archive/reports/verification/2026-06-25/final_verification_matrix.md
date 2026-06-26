# Final Verification Matrix — 2026-06-25

| Verification Item | MySQL | PostgreSQL |
| --- | --- | --- |
| Provider Credential | PASS | PASS |
| Credential Validation | PASS | PASS |
| Workflow UI | PASS | PASS |
| Tool Node Invoke | PASS | PASS |
| SELECT LIMIT | PASS | PASS |
| JSON Output | PASS | PASS |
| Error Handling | PASS | PASS |
| plugin-daemon Dispatch | PASS | PASS |

## Confirmed evidence

- Dify Console restored at `http://localhost/`.
- `curl.exe -I http://localhost/` returned `HTTP/1.1 307 Temporary Redirect` with `location: /apps`.
- `dify_plugin` database was created for plugin-daemon.
- plugin-daemon reached `local runtime ready plugin=li_zijun/db_query_extended`.
- MySQL Workflow chain returned `outputs.result` with `row_count=5`.
- PostgreSQL Workflow UI validation was completed manually after switching credential to PostgreSQL.
- Wrong-password credential validation returned a readable PluginInvokeError / ToolProviderCredentialValidationError message without exposing Python traceback.
- `verify_plugin.ps1` returned `57 PASS / 0 FAIL / 0 SKIP`.

## Remaining future scope

- DM adapter: Future.
- KingbaseES adapter: Future.
- SSL certificate support: Pending.
- Markdown output: Pending.
