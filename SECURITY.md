# Security Policy

## Supported version

Security fixes target the current v1.0 baseline and the latest accepted release candidate.

## Reporting

Do not disclose vulnerabilities, credentials, internal hosts, or exploit details in a public issue. Use the repository host's private vulnerability-reporting feature or contact the owning organization privately. A dedicated security contact must be published before public launch.

Include affected version, reproduction steps using non-sensitive data, impact, and suggested mitigation. Never include a live API key, password, token, database dump, or private customer data.

## Scope priorities

- SQL read-only bypass or multi-statement execution.
- Credential or connection-string leakage.
- Unsafe driver/package loading.
- Cross-tenant Provider or Workflow access.
- API authorization bypass.
- Malicious result serialization or resource exhaustion.
