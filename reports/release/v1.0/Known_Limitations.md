# Known Limitations

1. The plugin is deliberately read-only. DDL, DML, multi-statement input, and other dangerous SQL are rejected.
2. KingbaseES, Oracle, SQL Server, and SQLite are roadmap items, not v1.0 capabilities.
3. DM8 requires its vendor driver packages and a reachable DM8 server; the database server is not bundled in the plugin.
4. The accepted package architecture is `amd64`.
5. Query output is bounded by `max_rows`; large datasets are truncated intentionally.
6. Query timeout behavior ultimately depends on the target driver and database.
7. Workflow API credentials are external runtime secrets and must be re-created or securely transferred on another machine.
8. UI screenshot evidence is maintained separately from machine verification. It is not embedded with credentials.
9. The baseline worktree contained pre-existing uncommitted material; release must use the checklist before committing or tagging.
