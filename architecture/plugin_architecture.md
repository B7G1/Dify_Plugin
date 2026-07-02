# Plugin Architecture

![Plugin architecture](plugin_architecture.svg)

## Responsibility

The plugin exposes one read-only database query capability to Dify. Provider configuration owns connection credentials; the Tool owns request validation and result presentation; adapters isolate database-specific behavior.

```mermaid
flowchart LR
    U["Dify workspace user"] --> W["Workflow tool node"]
    W --> PD["Plugin daemon"]
    PD --> P["db_query_extended Provider"]
    P --> T["Read-only SQL Tool"]
    T --> V["SQL and input validation"]
    V --> A["Adapter registry"]
    A --> M["MySQL adapter"]
    A --> G["PostgreSQL adapter"]
    A --> D["DM8 adapter"]
    M --> R["Normalized JSON result"]
    G --> R
    D --> R
    R --> W
```

## Boundaries

- `provider/`: credential schema and credential validation entry.
- `tools/`: Dify Tool input/output contract and orchestration.
- `utils/validation.py` and `utils/sql_validator.py`: read-only policy.
- `utils/adapters/`: database dialect and driver behavior.
- `utils/result_formatter.py`: stable JSON-safe response contract.

Credentials never enter logs or reports. Runtime failures are translated into controlled plugin errors rather than leaking connection URLs.
