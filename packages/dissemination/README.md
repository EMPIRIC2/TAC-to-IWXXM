# dissemination

Library helpers for publishing IWXXM / bulletin payloads to operator destinations:
multi-database writer-contract DDL, WIS2 and EDIS sinks, AMHS/SWIM/AFS staging stubs, and
egress host allowlisting. MIT licensed.

**Not yet on PyPI** — install from this monorepo (a public `iwxxm-dissemination` release is
planned separately). Import path remains `dissemination`.

This package has **no** FastAPI or Supabase imports. HTTP APIs that call it live in the
host application.

## Install (from source)

```bash
# from the monorepo root
uv sync --package dissemination
# or
pip install -e packages/dissemination
```

Requires Python ≥ 3.12.

## Allowlist / SSRF helpers

Egress is fail-closed when the allowlist is empty. Load from an environment variable or
parse an explicit host/CIDR list:

```python
from dissemination import load_allowlist_from_env, parse_allowlist, validate_egress_host

allow = load_allowlist_from_env()  # DISSEMINATION_EGRESS_ALLOWLIST
# or: allow = parse_allowlist("example.org,10.0.0.0/8")
validate_egress_host("broker.example.org", allow)
```

One-shot destination credentials are **caller-owned and memory-only** — do not persist
them in this library.

## Writer contract

```python
from dissemination import writer_contract_ddl, apply_writer_contract, diff_writer_contract

ddl = writer_contract_ddl()
# apply_writer_contract / diff_writer_contract against a SQLAlchemy async engine
```

Supported database dialects include PostgreSQL, MySQL, SQLite, and SQL Server (via
`aioodbc`). SQL Server needs a system ODBC driver (prefer Microsoft ODBC Driver 18).

## Sinks

| Module                     | Role                                           |
| -------------------------- | ---------------------------------------------- |
| `dissemination.wis2`       | WIS2 preflight / publish (MQTT + HTTP dataset) |
| `dissemination.edis`       | EDIS / WMO AHL formatting + SMTP submit        |
| `dissemination.f19_stubs`  | Staging stubs for AMHS / SWIM / AFS            |
| `dissemination.transports` | Injectable HTTP, MQTT, and SMTP clients        |

Preflight and send share a common `SinkAdapter` protocol. Unit tests mock transports;
integration tests can use the Compose wis2box harness under
`packages/dissemination/docker/wis2box-harness`.

## COLLECT / multi-version namespaces

`dissemination.collect_namespaces` helps detect `collect:MeteorologicalBulletin` and list
per-member IWXXM namespace URIs for multi-version bulletins.

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related published packages: [`tac2iwxxm`](https://pypi.org/project/tac2iwxxm/),
  [`tac-validate`](https://pypi.org/project/tac-validate/),
  [`iwxxm-validate`](https://pypi.org/project/iwxxm-validate/)
