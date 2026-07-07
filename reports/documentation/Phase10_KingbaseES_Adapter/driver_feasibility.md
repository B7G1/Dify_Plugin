# Phase 10.1 — KingbaseES Driver Feasibility Gate

Date: 2026-07-02  
Baseline: v1.0.0, commit `f7b26b1`, `45 PASS / 0 FAIL / 0 SKIP`  
Decision: **B. CONDITIONAL GO**

## Scope and integrity

This gate inspected the current host, Docker inventory, Dify plugin-daemon runtime, official KingbaseES documentation, and current PyPI package metadata. It did not modify Provider, Tool, Adapter, Workflow, `verify_all.ps1`, requirements, packaging, or v1.0 regression logic.

An isolated probe was added at `driver_feasibility_probe.py`. It is not imported by the plugin and was not executed against a database because no KingbaseES server or credentials are present.

The probe passed Python 3.12 syntax compilation inside plugin-daemon. Its no-credential self-test returned the expected `BLOCKED` result and listed only missing environment-variable names, not secret values.

## 1. Current runtime facts

| Item | Observed value | Status |
| --- | --- | --- |
| plugin-daemon image | `langgenius/dify-plugin-daemon:0.5.3-local` | PASS |
| container OS | Ubuntu 24.04.3 LTS | PASS |
| architecture | Linux `x86_64` | PASS |
| glibc | 2.39 | PASS |
| Python | 3.12.3 | PASS |
| global `sqlalchemy` import | not installed in daemon base environment | EXPECTED/BLOCKED |
| global `ksycopg2` import | not installed | BLOCKED |
| `libkci.so` in daemon | not found | BLOCKED |
| KingbaseES container/service | not found | BLOCKED |
| Kingbase artifacts in repository | no driver, dialect, client library, or server package found | BLOCKED |

SQLAlchemy is normally installed inside the plugin dependency environment, not necessarily the daemon's global Python. Therefore the global import result does not prove incompatibility; it proves that a clean isolated dependency installation is still required.

## 2. KingbaseES server identification

No running or stopped KingbaseES Docker container was found. No Windows KingbaseES service or common installation directory was found. Consequently these required facts could not be measured:

- exact database version/build;
- PostgreSQL compatibility mode and compatibility flags;
- `SELECT version()` output;
- server/client character encoding;
- default schema and `search_path`;
- read-only user privileges.

The official documentation states that KingbaseES offers PostgreSQL, Oracle, MySQL, and SQL Server compatibility modes. Phase 10 must use and record a PostgreSQL-compatible instance; a generic KingbaseES product label is insufficient evidence.

Status: **BLOCKED — server must be provided or provisioned.**

## 3. Driver availability

### PyPI finding

PyPI currently lists `ksycopg2 2.9.1`, uploaded 2026-07-01, including:

- `ksycopg2-2.9.1-cp312-cp312-manylinux1_x86_64.whl`;
- CPython 3.12 classifier;
- Linux/Unix and Python 3.12 support metadata;
- SHA-256 `59d2d19439fa0d8ae66a7972ef9ef1fe461e84389d50bc3e90c59abb4962287a` for the required x86_64 wheel;
- LGPL classifier.

The wheel tag is compatible in principle with the current CPython 3.12 x86_64/glibc 2.39 runtime.

### Download/import attempt

Two real download attempts were made:

1. `pip install --target /tmp/kingbase_gate ksycopg2==2.9.1` inside plugin-daemon;
2. direct PyPI JSON lookup/download from the Windows host temporary directory.

Both timed out under the current network conditions. No partial importable installation remained. Therefore wheel availability is **confirmed by registry metadata**, but download integrity and runtime import are **not yet PASS**.

### Native client library

Official documentation describes `ksycopg2` as a wrapper around Kingbase native client capability and older installation guidance requires the directory containing `libkci` in `LD_LIBRARY_PATH`. The current wheel is approximately 4.4 MB, but it was not downloaded and inspected, so this gate cannot claim whether `libkci` is bundled or must be supplied separately.

Required follow-up:

```text
unzip/list wheel contents
locate extension modules and bundled .so files
run ldd on every native extension
import ksycopg2 in plugin-daemon Python 3.12
record missing shared libraries without changing the base image
```

Status: **CONDITIONAL — the wheel exists, but the actual wheel/client library must be supplied or made downloadable.**

## 4. SQLAlchemy compatibility

The official and current documented URL is:

```text
kingbase+ksycopg2://username:password@host:54321/database
```

The shorthand `kingbase://...` is also documented, with `ksycopg2` as the default driver.

However, public older Kingbase SQLAlchemy documentation says its dialect was based on SQLAlchemy 1.3.17 and other SQLAlchemy versions were not fully tested. No standalone current Kingbase dialect package was found in the workspace, and the `ksycopg2` wheel could not be inspected to determine whether it now registers or bundles a SQLAlchemy 2.x dialect.

SQLAlchemy 2.0.51 compatibility therefore remains **UNVERIFIED**. Required clean-runtime checks are:

1. install exactly SQLAlchemy 2.0.51 and the candidate driver/dialect in an isolated directory;
2. resolve `kingbase+ksycopg2` through SQLAlchemy's dialect registry;
3. construct the URL through `URL.create`;
4. connect, begin/rollback, execute parameterized `text()` statements, consume results, and dispose the engine;
5. confirm no patch to SQLAlchemy itself is required.

Status: **BLOCKED — current dialect artifact/support statement required.**

## 5. Minimal connection matrix

| Check | Result | Reason |
| --- | --- | --- |
| `SELECT 1` | NOT RUN | no server/driver |
| `SELECT '中文测试'` | NOT RUN | no server/driver |
| `SELECT CURRENT_TIMESTAMP` | NOT RUN | no server/driver |
| schema/search_path | NOT RUN | no server/driver |
| parameter binding | NOT RUN | no server/driver |
| connection timeout | NOT RUN | no importable driver |
| read-only account permissions | NOT RUN | no server/account |

The isolated probe covers version, encodings, `search_path`, parameterized `set_config`, scalar queries, parameter binding, and schema `USAGE`/`CREATE` privilege inspection. Secrets are accepted only through process environment variables and are never printed.

The timeout result must be collected in a separate invocation against a controlled unreachable endpoint. A successful import alone is not sufficient.

## 6. Offline packaging and redistribution risk

| Question | Finding |
| --- | --- |
| Is a CPython 3.12 Linux x86_64 wheel listed? | YES — PyPI `2.9.1` |
| Was it downloaded and hashed locally? | NO — network timeout |
| Can it import in plugin runtime? | UNVERIFIED |
| Does it need extra `.so` files? | UNVERIFIED; official guidance indicates native client dependency may apply |
| Is SQLAlchemy 2.0.51 supported? | UNVERIFIED |
| Is URL form confirmed? | YES — `kingbase+ksycopg2://...` in official docs |
| May the wheel be redistributed? | NOT APPROVED; PyPI declares LGPL, but vendor wheel/native client notices and bundled-library licenses must be reviewed |
| Can a Linux amd64 plugin technically carry wheels/native libs? | YES in principle, as demonstrated by the existing DM8 pattern, but Kingbase files and licenses require their own validation |

Do not copy vendor `.so`, wheel, license, or dialect files into the plugin until wheel inspection and redistribution review are complete.

## 7. Required human-provided inputs

To convert this gate to GO, provide:

1. reachable KingbaseES instance in PostgreSQL compatibility mode;
2. exact server version/build and deployment source;
3. read-only test credentials supplied only through the current process environment;
4. the PyPI wheel file or working network access to download it;
5. current Kingbase SQLAlchemy dialect artifact/documentation for SQLAlchemy 2.0.51;
6. required `libkci`/native client directory and license notices if not bundled;
7. authorization/decision for redistribution in an offline `.difypkg`.

## 8. Gate decision

### **B. CONDITIONAL GO**

The runtime architecture is promising: a matching CPython 3.12 Linux x86_64 `ksycopg2` wheel is now published, and the documented SQLAlchemy URL matches the proposed Adapter design. The gate cannot become GO because the wheel could not be imported, native dependencies could not be inspected, SQLAlchemy 2.0.51 compatibility is unproven, and no KingbaseES server is available for real queries.

Do not begin Adapter implementation yet. Once the seven inputs above are available, rerun the isolated probe and require every minimal connection check to pass before changing Provider, Adapter, requirements, or verification code.

## Sources

- [PyPI ksycopg2 2.9.1 files and classifiers](https://pypi.org/project/ksycopg2/)
- [Official KingbaseES Python driver overview and native-library setup](https://help.kingbase.com.cn/v8/development/client-interfaces/python/python-1.html)
- [Official KingbaseES parameter-binding behavior](https://help.kingbase.com.cn/v8/development/client-interfaces/python/python-3.html)
- [Official KingbaseES SQLAlchemy URL](https://help.kingbase.com.cn/v8/development/client-interfaces-frame/sqlalchemy/sqlalchemy-2.html)
- [Official KingbaseES SQLAlchemy compatibility notes](https://help.kingbase.com.cn/v8/development/client-interfaces-frame/sqlalchemy/sqlalchemy-1.html)
- [Official KingbaseES compatibility-mode overview](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/data_migration/migration_overview.html)
- [Official KingbaseES character-set behavior](https://help.kingbase.com.cn/v9.4.12/development/application-develop-guide/local/local-3.html)
