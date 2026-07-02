# Privacy and Data Handling

`db_query_extended` executes user-supplied read-only SQL against a database configured by the Dify workspace administrator.

## Data processed

- Database connection settings supplied through Dify Provider credentials.
- SQL text and query controls such as row limit and timeout.
- Database result columns, rows, metadata, timing, warnings, and errors.

## Processing and storage

The plugin sends queries only to the configured database endpoint and returns normalized results to the invoking Dify runtime. The plugin does not intentionally transmit data to an independent analytics or advertising service. Credential storage, Workflow history, logs, and result retention are controlled by the deployed Dify environment and its operators.

## Credentials

Passwords and secrets are Provider credentials. They must not be placed in SQL, Workflow variables, screenshots, reports, scripts, or source control. The plugin is designed not to log connection URLs or plaintext credentials, but deployment operators remain responsible for platform logging and access controls.

## Operator responsibility

Before use, the operator must ensure that queried data is authorized for the workspace, the database account has least privilege, retention complies with applicable policy/law, and Dify/database transport security is configured appropriately.

## Contact

Privacy and security contact ownership must be published by the repository owner before Marketplace submission. Until then, do not use this plugin for regulated or personal data without an approved organizational review.
