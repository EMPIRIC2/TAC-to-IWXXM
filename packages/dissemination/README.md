# iwxxm-dissemination

Library helpers for publishing IWXXM / bulletin payloads to operator destinations:
multi-database writer-contract DDL, WIS2 and EDIS sinks, AMHS/SWIM/AFS staging stubs, and
egress host allowlisting. MIT licensed.

PyPI name: **`iwxxm-dissemination`**. Import path: **`dissemination`** (unchanged for monorepo
and library callers).

This package has **no** FastAPI or Supabase imports. HTTP APIs that call it live in the
host application. One-shot destination credentials are **caller-owned and memory-only**;
do not persist them in this library.

## Install

```bash
pip install iwxxm-dissemination
# or from the monorepo root:
uv sync --package iwxxm-dissemination
```

Requires Python ≥ 3.12.

### System dependencies (not in the wheel)

SQL Server via `aioodbc` needs a host ODBC driver (prefer Microsoft ODBC Driver 18).
Other dialects use the declared async drivers (`asyncpg`, `aiomysql`, `aiosqlite`).

Optional `[integration]` extra pulls Testcontainers for Compose/harness tests only.

## Allowlist / SSRF helpers

Egress is fail-closed when the allowlist is empty. Load from an environment variable or
parse an explicit host/CIDR list:

```python
from dissemination import load_allowlist_from_env, parse_allowlist, validate_egress_host

allow = load_allowlist_from_env()  # DISSEMINATION_EGRESS_ALLOWLIST
# or: allow = parse_allowlist("example.org,10.0.0.0/8")
validate_egress_host("example.org", allowlist=allow)
```

## Writer contract

```python
from dissemination import writer_contract_ddl, apply_writer_contract, diff_writer_contract

ddl = writer_contract_ddl("sqlite")
# apply_writer_contract / diff_writer_contract against a SQLAlchemy async engine
```

Supported database dialects include PostgreSQL, MySQL, SQLite, and SQL Server (via
`aioodbc`).

## Sinks

| Module                     | Role                                           |
| -------------------------- | ---------------------------------------------- |
| `dissemination.wis2`       | WIS2 preflight / publish (MQTT + HTTP dataset) |
| `dissemination.edis`       | EDIS / WMO AHL formatting + SMTP submit        |
| `dissemination.f19_stubs`  | Staging stubs for AMHS / SWIM / AFS            |
| `dissemination.transports` | Injectable HTTP, MQTT, and SMTP clients        |

Preflight and send share a common `SinkAdapter` protocol. Unit tests mock transports;
integration tests can use the Compose wis2box harness under
`packages/dissemination/docker/wis2box-harness`. That harness is a local MQTT
and HTTP stand-in. The reference WIS2 node is
[World-Meteorological-Organization/wis2box](https://github.com/World-Meteorological-Organization/wis2box).

## COLLECT / multi-version namespaces

`dissemination.collect_namespaces` helps detect `collect:MeteorologicalBulletin` and list
per-member IWXXM namespace URIs for multi-version bulletins.

## Release tags

Publish is tag-driven via `.github/workflows/pypi-publish.yml`:

- Tag: `iwxxm-dissemination-v0.1.0` (must match `pyproject.toml` version)
- Auth: PyPI OpenID Connect trusted publisher for project `iwxxm-dissemination`
  (no long-lived API token when OIDC is configured)

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related published packages: [`tac2iwxxm`](https://pypi.org/project/tac2iwxxm/),
  [`tac-validate`](https://pypi.org/project/tac-validate/),
  [`iwxxm-validate`](https://pypi.org/project/iwxxm-validate/)
