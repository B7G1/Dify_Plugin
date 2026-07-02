# Compatibility Matrix

| Component | Frozen/tested version | Notes |
| --- | --- | --- |
| Dify | 1.13.3 | accepted Console/API baseline |
| Dify Plugin SDK | 0.6.2 | pinned in `requirements.txt` |
| Python | 3.12 plugin runtime; 3.11 development environment | manifest runtime and local tooling |
| Docker Compose | 5.1.3 | fixed project name `dify` |
| PostgreSQL (Dify) | 15 Alpine | persistent Console/plugin metadata |
| PostgreSQL (adapter test) | 16 | local regression database |
| MySQL | 8.4 | local regression database |
| DM8 | server-specific deployment; `dmPython` 2.5.32 / `dmSQLAlchemy` 2.0.12 | real acceptance target |
| Plugin Daemon | `langgenius/dify-plugin-daemon:0.5.3-local` | stable after cold boot |
| SQLAlchemy | 2.0.51 | pinned adapter layer |

The package manifest requires Dify `>=1.0.0`, but v1.0 acceptance was performed only against Dify 1.13.3.
