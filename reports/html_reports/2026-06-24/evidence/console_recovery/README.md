# Console Recovery Evidence

Status: PASS

- `http://localhost/` initially failed because nginx was exited.
- `dify-nginx-1` was recreated.
- `curl.exe -I http://localhost/` returned:

```text
HTTP/1.1 307 Temporary Redirect
location: /apps
```

Primary archive: `reports/verification/2026-06-25/api_logs.txt`.
