# Architecture Evolution

## 1. Single-database query logic

The earliest design focused on making one database query succeed. This was useful for learning the Dify plugin contract but coupled credentials, SQL execution, driver behavior, and result formatting. Adding another database would have multiplied conditionals and failure paths.

## 2. Common Tool contract

The Tool became the stable Workflow-facing boundary: SQL, row limit, timeout, read-only mode, and output format. This prevented database-specific controls from leaking into every Workflow and gave users one predictable node.

## 3. Shared Validation

SQL and input validation moved into shared components before adapter execution. This was essential: if each database implemented its own safety policy, one weaker adapter could bypass the project’s read-only guarantee. Shared Validation made security a framework invariant.

## 4. Adapter Registry

Connection construction, timeout syntax, driver exceptions, and vendor-specific types differed across MySQL and PostgreSQL. The Adapter Registry isolated those differences behind a common lifecycle. The Tool stopped asking how a database works and asked only which accepted adapter should execute.

## 5. Multi-database execution

MySQL and PostgreSQL proved the abstraction. DM8 then tested the design against a different vendor driver and runtime packaging model. DM8 acceptance demonstrated that extension did not require rewriting the Provider, Workflow, SQL policy, or JSON contract.

## 6. Unified JSON Contract

Rows, columns, counts, truncation, timing, warnings, and JSON-safe values became database-neutral output. Workflow and API clients could consume the same shape regardless of driver-specific date, decimal, binary, or Unicode types.

## 7. Unified Verification

Provider, Tool, and Workflow suites were combined by `verify_all.ps1`. Verification became part of architecture rather than an afterthought: adapters are accepted only when configuration, shared behavior, real Workflow/API execution, Unicode, and dangerous SQL all pass without skip.

## 8. Recoverable framework

Persistent PostgreSQL/Weaviate volumes, one Compose project, preflight, cold boot, snapshots, reports, and Dashboard extended the architecture beyond plugin code. The final system can prove it returned with the same identity and records after restart.

## Why the result is an Adapter Framework

The final architecture separates stable framework contracts from database extensions:

- Provider owns secret configuration and connection validation.
- Tool owns the Dify-facing interface.
- Shared Validation owns read-only security.
- Adapter Registry owns driver and dialect differences.
- JSON Contract owns interoperable results.
- Workflow owns orchestration without database-specific rewrites.
- Verification owns evidence and regression protection.

This structure lets Phase 10 add KingbaseES as a new adapter while treating every existing v1.0.0 behavior as immutable. That is the defining property of the framework: extension occurs at a designed boundary, not through repeated changes to the core.
