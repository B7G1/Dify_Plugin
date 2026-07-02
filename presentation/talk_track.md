# 20-Minute Talk Track

## Opening

“今天汇报的不是一个只能演示一次的数据库插件，而是一套能恢复、能验证、能继续扩展的 Dify 数据库访问基线。” Explain the problem: workflows need data, but credentials, arbitrary SQL, vendor drivers, and container persistence create four different failure classes.

## Architecture

Walk left to right through the Overall Architecture. Emphasize that Workflow and Tool contracts do not change when a database adapter changes. Provider isolates secrets; shared validation is intentionally outside vendor adapters.

## Implementation

Explain the adapter lifecycle: normalize configuration, validate a minimal connection, apply timeout, execute one prevalidated statement, normalize values, clean resources, map controlled errors. Mention Python 3.12 runtime and pinned SDK/driver versions only when explaining reproducibility.

## Workflow evidence

Use the Workflow screenshot or live demo. Describe the input (`sql`, `max_rows`), three nodes, DM8 result, Unicode preservation, and stable JSON. Do not expose system IDs or credentials on screen.

## Verification evidence

Interpret the 6/27/12 split: Provider proves configuration behavior, Tool proves shared functional/security behavior, Workflow proves the published external chain. “零 SKIP” matters because an unavailable target cannot masquerade as a release pass.

## Persistence evidence

Explain why stopping all containers is stronger than reading current health. The same PostgreSQL system identifier, named volume, accounts/tenants, plugin installation, Provider/Workflow records, and zero daemon restarts jointly rule out accidental reinitialization.

## Product readiness

Show the Dashboard and repository structure. State the current boundary: technical acceptance and Screenshot Review are complete, so v1.0 Public Release is READY. License selection, governance contacts, and official Marketplace submission remain separate follow-up decisions.

## Close

“v1.0 冻结的是可复用方法：稳定 Tool、隔离 Adapter、真实 Workflow、机器证据和可恢复环境。Phase 10 的 KingbaseES 将验证这套方法能否在不破坏现有 45 项回归的前提下继续扩展。”

Invite questions on threat model, adapter abstraction, experiment validity, and recovery portability.
