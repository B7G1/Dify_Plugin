import importlib.metadata
import json
import platform
import time


started = time.perf_counter()
import ksycopg2
import sqlalchemy

entry_points = [
    {"name": entry.name, "value": entry.value}
    for entry in importlib.metadata.entry_points(group="sqlalchemy.dialects")
    if "king" in entry.name.lower() or "ksy" in entry.name.lower()
]

print(
    json.dumps(
        {
            "status": "PASS",
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "module": ksycopg2.__name__,
            "module_file": ksycopg2.__file__,
            "version": ksycopg2.__version__,
            "apilevel": ksycopg2.apilevel,
            "threadsafety": ksycopg2.threadsafety,
            "paramstyle": ksycopg2.paramstyle,
            "connect_callable": callable(ksycopg2.connect),
            "error_is_exception": issubclass(ksycopg2.Error, Exception),
            "sqlalchemy_version": sqlalchemy.__version__,
            "kingbase_sqlalchemy_entry_points": entry_points,
            "import_elapsed_seconds": time.perf_counter() - started,
        },
        ensure_ascii=False,
    )
)
