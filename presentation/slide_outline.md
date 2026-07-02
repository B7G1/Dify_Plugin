# 20-Minute Slide Outline

1. **Database access is the missing bridge in many Dify workflows**  
   Establish the user problem and why unrestricted SQL is unacceptable.

2. **v1.0 delivers one read-only contract across three databases**  
   MySQL, PostgreSQL, DM8; state the exact scope and exclusions.

3. **The design separates workflow stability from database variation**  
   Show Overall Architecture.

4. **Provider and Tool divide secrets from execution policy**  
   Explain credential validation, stable inputs, and no-secret logging.

5. **Adapters absorb driver, timeout, and type differences**  
   Show Adapter Architecture and extension contract.

6. **A three-node Workflow keeps the user experience simple**  
   Start → Tool → Output; real DM8 JSON.

7. **Read-only safety is enforced before the database**  
   Single statement, SELECT/WITH, dangerous SQL rejection, bounded rows/time.

8. **Verification is layered so failures identify the broken contract**  
   Provider 6, Tool 27, Workflow 12.

9. **Forty-five checks passed with no failure or skip**  
   Interpret the result rather than merely displaying it.

10. **Cold boot proves the environment is the same system after restart**  
    Unchanged identifier, named volumes, persisted objects, daemon restart 0.

11. **The Dashboard connects claims to evidence and recovery**  
    Show release, baseline, architecture, verification entrances.

12. **v1.0 is ready for public presentation with truthful evidence**  
    Screenshot Review is PASS; license selection, governance contacts, CI runners, and official Marketplace submission remain follow-up work.

13. **Phase 10 can add KingbaseES without rewriting the Tool**  
    Adapter template and regression contract; no other new database in current scope.

14. **The durable contribution is the evidence-backed extension method**  
    Close on maintainability, reproducibility, and explicit next decision.
