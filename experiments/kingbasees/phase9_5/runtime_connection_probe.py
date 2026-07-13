import importlib
import importlib.metadata
import json
import os
import sys

import ksycopg2
from sqlalchemy import URL, create_engine, text
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.pool import NullPool


required = ("KINGBASE_HOST", "KINGBASE_PORT", "KINGBASE_DATABASE", "KINGBASE_USERNAME", "KINGBASE_PASSWORD")
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise SystemExit(json.dumps({"status": "BLOCKED", "missing_environment": missing}))

result = {
    "status": "FAIL",
    "credential_source": "container environment; value redacted",
    "password": "***REDACTED***",
    "dbapi": {},
    "official_dialect": {},
    "compatibility_shim": {},
}

connection = ksycopg2.connect(
    host=os.environ["KINGBASE_HOST"],
    port=int(os.environ["KINGBASE_PORT"]),
    database=os.environ["KINGBASE_DATABASE"],
    user=os.environ["KINGBASE_USERNAME"],
    password=os.environ["KINGBASE_PASSWORD"],
    connect_timeout=10,
)
try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    select_1 = cursor.fetchone()[0]
    cursor.execute("SELECT '金仓数据库'")
    unicode_value = cursor.fetchone()[0]
    cursor.execute("SELECT %s", ("参数绑定",))
    parameter_value = cursor.fetchone()[0]
    cursor.close()
finally:
    connection.close()

result["dbapi"] = {
    "status": "PASS",
    "select_1": select_1,
    "unicode": unicode_value,
    "parameter_binding": parameter_value,
    "paramstyle": ksycopg2.paramstyle,
    "connection_closed": connection.closed != 0,
}

entry_points = [
    {"name": entry.name, "value": entry.value}
    for entry in importlib.metadata.entry_points(group="sqlalchemy.dialects")
    if "king" in entry.name.lower() or "ksy" in entry.name.lower()
]
try:
    registry.load("kingbase.ksycopg2")
    official_status = "PASS"
    official_error = None
except Exception as exc:
    official_status = "NOT_FOUND"
    official_error = type(exc).__name__
result["official_dialect"] = {
    "status": official_status,
    "entry_points": entry_points,
    "error_type": official_error,
}

# Experimental and process-local: SQLAlchemy's PostgreSQL dialect imports the
# psycopg2 namespace internally. These aliases disappear when this probe exits.
sys.modules["psycopg2"] = ksycopg2
for submodule in ("extensions", "extras", "errors"):
    sys.modules[f"psycopg2.{submodule}"] = importlib.import_module(f"ksycopg2.{submodule}")


class KingbaseDialect(PGDialect_psycopg2):
    name = "kingbase"
    driver = "ksycopg2"
    supports_statement_cache = False

    @classmethod
    def import_dbapi(cls):
        return ksycopg2

    def _get_server_version_info(self, connection):
        return (9, 1, 10)


registry.register("kingbase.ksycopg2", "__main__", "KingbaseDialect")
url = URL.create(
    "kingbase+ksycopg2",
    username=os.environ["KINGBASE_USERNAME"],
    password=os.environ["KINGBASE_PASSWORD"],
    host=os.environ["KINGBASE_HOST"],
    port=int(os.environ["KINGBASE_PORT"]),
    database=os.environ["KINGBASE_DATABASE"],
)
engine = create_engine(url, poolclass=NullPool, connect_args={"connect_timeout": 10})
try:
    with engine.connect() as sql_connection:
        select_1_sa = sql_connection.execute(text("SELECT 1")).scalar_one()
        unicode_sa = sql_connection.execute(text("SELECT '金仓数据库'")).scalar_one()
        parameter_sa = sql_connection.execute(text("SELECT :value"), {"value": "参数绑定"}).scalar_one()
        sql_connection.rollback()
    result["compatibility_shim"] = {
        "status": "PASS",
        "scope": "single probe process only",
        "select_1": select_1_sa,
        "unicode": unicode_sa,
        "parameter_binding": parameter_sa,
        "connection_closed": True,
        "engine_disposed": True,
    }
    result["status"] = "PASS"
finally:
    engine.dispose()

print(json.dumps(result, ensure_ascii=False))
