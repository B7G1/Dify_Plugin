# Phase 1 Architecture Notes

## Initial Boundaries

- Provider: validates credentials and connection readiness.
- Tool: receives SQL and returns a structured result.
- Utilities: hold reusable validation, database, and formatting logic.

## Design Principle

Keep the public Tool contract stable even when database adapters change later.
