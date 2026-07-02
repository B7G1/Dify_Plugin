# Verification Architecture

![Verification architecture](verification_architecture.svg)

## Automated suites

```mermaid
flowchart TD
    E["Ephemeral environment variables"] --> A["verify_all.ps1"]
    A --> P["verify_provider.ps1\n6 checks"]
    A --> T["verify_tool.ps1\n27 checks"]
    A --> W["verify_workflow.ps1\n12 checks"]
    P --> R["verification_runner.py"]
    T --> R
    W --> R
    R --> PJ["provider_result.json"]
    R --> TJ["tool_result.json"]
    R --> WJ["workflow_result.json"]
    PJ --> S["summary.json\n45 / 0 / 0"]
    TJ --> S
    WJ --> S
```

## Full acceptance flow

```mermaid
flowchart LR
    I["Snapshot identity"] --> C["Cold stop"]
    C --> B["Start via start_dify.ps1"]
    B --> H["Health and persistence checks"]
    H --> UI["UI object checks"]
    H --> API["Fresh Workflow API queries"]
    API --> V["verify_all.ps1"]
    UI --> G["Evidence gate"]
    V --> G
    G --> F["Baseline freeze / release"]
```

Machine JSON is authoritative for counts. Human-readable reports summarize it and must never replace or silently reinterpret it.
