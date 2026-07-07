"""Isolated KingbaseES driver feasibility probe.

This script is not imported by the plugin. It reads credentials only from the
current process environment and never writes them to output or disk.
"""

from __future__ import annotations

import json
import os
import platform
import sys
from typing import Any


REQUIRED_ENV = (
    "KINGBASE_HOST",
    "KINGBASE_DATABASE",
    "KINGBASE_USERNAME",
    "KINGBASE_PASSWORD",
)


def main() -> int:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        print(json.dumps({"status": "BLOCKED", "missing_environment": missing}, ensure_ascii=False))
        return 2

    try:
        import ksycopg2  # type: ignore[import-not-found]
        import sqlalchemy
        from sqlalchemy import URL, create_engine, text
        from sqlalchemy.pool import NullPool
    except Exception as exc:  # noqa: BLE001 - probe must preserve import failure class
        print(
            json.dumps(
                {"status": "FAIL", "stage": "import", "error_type": type(exc).__name__},
                ensure_ascii=False,
            )
        )
        return 1

    if sqlalchemy.__version__ != "2.0.51":
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "stage": "sqlalchemy_version",
                    "actual": sqlalchemy.__version__,
                    "required": "2.0.51",
                },
                ensure_ascii=False,
            )
        )
        return 1

    schema = os.getenv("KINGBASE_SCHEMA", "public")
    timeout = int(os.getenv("KINGBASE_CONNECT_TIMEOUT", "10"))
    url = URL.create(
        "kingbase+ksycopg2",
        username=os.environ["KINGBASE_USERNAME"],
        password=os.environ["KINGBASE_PASSWORD"],
        host=os.environ["KINGBASE_HOST"],
        port=int(os.getenv("KINGBASE_PORT", "54321")),
        database=os.environ["KINGBASE_DATABASE"],
    )
    engine = create_engine(
        url,
        poolclass=NullPool,
        connect_args={"connect_timeout": timeout},
    )

    checks: list[dict[str, Any]] = []
    try:
        with engine.connect() as connection:
            with connection.begin():
                checks.append(_scalar(connection, text("SELECT version()"), "version"))
                checks.append(_scalar(connection, text("SHOW server_encoding"), "server_encoding"))
                checks.append(_scalar(connection, text("SHOW client_encoding"), "client_encoding"))
                checks.append(_scalar(connection, text("SHOW search_path"), "search_path_before"))
                connection.execute(
                    text("SELECT set_config('search_path', :schema, true)"),
                    {"schema": schema},
                )
                checks.append(_scalar(connection, text("SHOW search_path"), "search_path_after"))
                checks.append(_scalar(connection, text("SELECT 1"), "select_1"))
                checks.append(_scalar(connection, text("SELECT '中文测试'"), "unicode"))
                checks.append(
                    _scalar(connection, text("SELECT CURRENT_TIMESTAMP"), "current_timestamp")
                )
                checks.append(
                    _scalar(
                        connection,
                        text("SELECT :value"),
                        "parameter_binding",
                        {"value": "参数绑定"},
                    )
                )
                checks.append(
                    _scalar(
                        connection,
                        text(
                            "SELECT has_schema_privilege(current_user, :schema, 'USAGE')"
                        ),
                        "schema_usage",
                        {"schema": schema},
                    )
                )
                checks.append(
                    _scalar(
                        connection,
                        text(
                            "SELECT has_schema_privilege(current_user, :schema, 'CREATE')"
                        ),
                        "schema_create_should_be_false",
                        {"schema": schema},
                    )
                )
    except Exception as exc:  # noqa: BLE001 - probe reports controlled metadata only
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "stage": "connection_or_query",
                    "error_type": type(exc).__name__,
                    "runtime": _runtime(),
                },
                ensure_ascii=False,
                default=str,
            )
        )
        return 1
    finally:
        engine.dispose()

    print(
        json.dumps(
            {
                "status": "PASS",
                "runtime": _runtime(),
                "ksycopg2_version": getattr(ksycopg2, "__version__", "unknown"),
                "sqlalchemy_version": sqlalchemy.__version__,
                "url_driver": "kingbase+ksycopg2",
                "checks": checks,
                "connection_timeout_configured_seconds": timeout,
                "note": "Network timeout requires a separate unreachable-host invocation.",
            },
            ensure_ascii=False,
            default=str,
        )
    )
    return 0


def _scalar(connection: Any, statement: Any, name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    value = connection.execute(statement, params or {}).scalar()
    return {"name": name, "value": value}


def _runtime() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "system": platform.system(),
        "machine": platform.machine(),
    }


if __name__ == "__main__":
    raise SystemExit(main())
