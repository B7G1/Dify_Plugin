# KingbaseES Workflow Status

Status: **CONFIGURATION SPEC COMPLETE / REAL WORKFLOW BLOCKED**

The intended contract is recorded at `db_query_extended/workflow_specs/kingbasees_workflow.yaml`:

```text
Start(sql, max_rows)
  -> db_query_extended(readonly=true, output_format=json)
  -> End(result=Tool.json)
```

The specification preserves the v1.0 Workflow and JSON contracts and lists the eventual SQL/API acceptance cases. It is deliberately not represented as a Dify DSL export because no real KingbaseES Provider can currently pass credential validation.

Still BLOCKED:

- create and validate Provider credentials;
- create/test/publish a real Workflow;
- create a Workflow API key;
- execute UI and API acceptance;
- collect screenshots and machine evidence.

No API key, password export, or fabricated Workflow result is stored in the repository.

