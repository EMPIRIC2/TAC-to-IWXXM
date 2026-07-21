# dissemination

MIT package for F16–F19 operator dissemination: multi-DB writer-contract, WIS2/EDIS/AMHS
sink adapters, and SSRF/allowlist helpers ([ADR-030](../../docs/adr/ADR-030-dissemination-package-architecture.md)).

**Boundaries**

- No FastAPI or Supabase imports
- HTTP routers stay in `apps/backend` (thin)

**Coverage**

- Local/CI: `make test-unit-dissemination` (95% branch gate)

**Multi-DB integration (T2.5–T2.6 / TC-F16-003)**

- `make test-integration-dissemination` (or `pytest packages/dissemination/tests -m integration`)
- Postgres + MySQL via Testcontainers (requires Docker); SQLite in-process
- SQL Server via Testcontainers + **aioodbc** (requires Docker **and** a system ODBC
  SQL Server driver). Without ODBC, SQL Server cases **skip** (E14-06)
- Without Docker, PG/MySQL/SQL Server cases skip; SQLite still runs

**SQL Server ODBC (T2.7 / E14-06)**

| Item                    | Detail                                                                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Async driver            | `aioodbc` → SQLAlchemy URL prefix `mssql+aioodbc://`                                                                  |
| Preferred system driver | Microsoft **ODBC Driver 18** for SQL Server (then 17)                                                                 |
| Fallback                | FreeTDS / legacy “SQL Server” ODBC names                                                                              |
| Probe API               | `dissemination.odbc.list_sqlserver_odbc_drivers()`, `odbc_sqlserver_available()`, `preferred_sqlserver_odbc_driver()` |

Install a system driver before live SQL Server tests or BYOC send:

```bash
# Debian/Ubuntu — see Microsoft docs for the current repo snippet, then:
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# Verify (from repo root with uv env):
uv run python -c "from dissemination.odbc import list_sqlserver_odbc_drivers; print(list_sqlserver_odbc_drivers())"
```

Example URI (spaces in the driver name must be URL-encoded as `+` or `%20`):

```text
mssql+aioodbc://sa:Your_password123@127.0.0.1:1433/master?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

Deploy / image notes (CI skip policy, stock API Dockerfile without `msodbcsql18`):
[docs/deploy.md](../../docs/deploy.md) §Local Development → SQL Server ODBC.

**WIS2 sink (T3.1–T3.4 / F17)**

- `dissemination.wis2` — `wis2_preflight` / `wis2_publish` with injectable MQTT + HTTP
  clients (unit-tested with mocks)
- `dissemination.transports` — `HttpxDatasetClient` + `AiomqttClient` (httpx / aiomqtt)
- Compose wis2box harness: MQTT + HTTP dataset stand-in under
  `packages/dissemination/docker/wis2box-harness`
- Staging publish: `make compose-wis2box-harness` runs TC-F17-001 pytest
- Live BYOC remains the cycle-close gate (TC-F17-002)

**EDIS sink (T4.1–T4.3 / F18)**

- `dissemination.edis` — WMO AHL formatting (ASCII-only) + `edis_preflight` /
  `edis_submit` with injectable SMTP (mocked in unit tests; live BYOC = TC-F18-002)
- `dissemination.transports.AiosmtpClient` — `aiosmtplib` SMTP client; preflight is
  connect/login only (never `send_message` in CI)

- Env: `DISSEMINATION_EGRESS_ALLOWLIST` (see `.env.example`, ADR-029)
- Empty ⇒ fail-closed
- Compose wis2box harness: `make compose-wis2box-up` / `compose-wis2box-harness`
  (allowlist `wis2box,127.0.0.1,localhost` when calling the sink)
