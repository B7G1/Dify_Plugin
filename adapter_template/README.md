# Adapter Development Template

Copy this directory to a feature workspace and replace every `<database>` placeholder. The template is intentionally not imported by the v1.0 plugin, so it cannot change accepted behavior.

## Contents

- `provider/credential_fields.yaml.template`: credential design worksheet.
- `adapter/adapter.py.template`: non-executable adapter skeleton.
- `verify/verify_<database>.ps1.template`: verification entry skeleton.
- `REGRESSION_CHECKLIST.md`: release gate for the new adapter.

## Workflow

1. Complete the database capability/risk notes.
2. Implement the adapter against `utils/adapters/base.py`; do not copy Tool or shared SQL validation.
3. Add only required credential fields and keep secrets as secret inputs.
4. Add driver pins and confirm Linux `amd64` packaging/licensing.
5. Build Provider, Tool, Workflow, API, Unicode, type, timeout, and security tests.
6. Add the database to `TEST_MATRIX.md` only after real evidence exists.
