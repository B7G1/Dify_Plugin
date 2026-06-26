# 2026-06-25 Architecture Notes

## Platform Path

User input entered Dify Workflow, reached the Tool node, called the installed plugin action, executed SQL against the configured database, and returned JSON through the Workflow output.

## Confirmed Boundaries

- Provider validates credentials and connection readiness.
- Tool executes only validated read-only SQL.
- Dify Workflow owns orchestration and user-facing flow.
- plugin-daemon dispatches plugin execution.
