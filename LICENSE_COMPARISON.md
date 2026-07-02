# Open-Source License Decision

No license has been selected. Until the owner approves one and adds a root `LICENSE`, the repository is **not licensed for public reuse**.

| License | Advantages | Trade-offs | Typical fit |
| --- | --- | --- | --- |
| MIT | short, familiar, permissive, easy commercial adoption | minimal patent language; derivatives need not publish changes | maximize reuse with low governance overhead |
| Apache-2.0 | permissive plus explicit patent grant and contribution protections | longer notice obligations; more complex than MIT | enterprise/open ecosystem where patent clarity matters |
| GPL-3.0 | strong copyleft keeps distributed derivatives open | limits proprietary integration; network use alone does not trigger source release | owner wants reciprocal source-sharing for distributed software |

## Decision questions

1. Should commercial proprietary products be allowed to embed the plugin?
2. Is an explicit patent grant important to the organization?
3. Must modified distributed versions publish source code?
4. Does the DM8 driver/package distribution impose compatible license constraints?
5. Who owns the copyright and has authority to license all contributed code?

## Required owner action

Record the selected license, copyright holder, and year. Then add the official unmodified license text as root `LICENSE`, update package notices, and rerun package/license review. Do not rename this comparison file to `LICENSE`.
