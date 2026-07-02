# Workflow Architecture

![Workflow architecture](workflow_architecture.svg)

## Published path

```mermaid
sequenceDiagram
    participant C as API client / Dify UI
    participant A as Dify Workflow API
    participant S as Start node
    participant T as Read-only SQL Tool
    participant D as DM8
    participant O as Output node
    C->>A: SQL and max_rows
    A->>S: create workflow run
    S->>T: validated inputs
    T->>D: one read-only statement
    D-->>T: columns and rows
    T-->>O: normalized JSON
    O-->>A: workflow output
    A-->>C: HTTP 200 + result
```

The accepted Workflow is `DM8 Readonly SQL Acceptance`, ID `ec11fbde-d77c-4818-bcdf-b2b483dffe3d`, with Start → Tool → Output. Its API URL is `http://localhost/v1/workflows/run`; the API key is never stored in the repository.

## Acceptance contract

- Workflow status must be success.
- DM8 `SELECT 1`, Unicode text, and current timestamp must survive JSON serialization.
- Row limits and truncation metadata must be correct.
- Dangerous SQL must be rejected before reaching the database.
