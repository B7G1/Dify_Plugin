# Phase 2 Lessons Learned

- SQL validation should be conservative and SQL-aware; simple substring checks are too noisy.
- Local database fixtures are essential because result formatting bugs often appear only with real driver values.
- Verification scripts should report SKIP honestly when an external service is not configured.
