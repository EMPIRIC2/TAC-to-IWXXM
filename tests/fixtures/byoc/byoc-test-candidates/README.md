# BYOC test candidates — all drawer sinks

Paste-ready destinations for every DisseminationDrawer option.
**Not real credentials.** Memory-only on preflight/send (ADR-021 / ADR-029).

## Bring up all mocks

```bash
make compose-mock-byoc-all-up    # PG, MySQL, SQL Server, MailHog, F19, wis2box
make test-mock-byoc-all-sinks    # preflight+send for all 9 sinks
```

| Sink | Mock | Host port / note |
|------|------|------------------|
| sqlite | in-process file | no container |
| postgres | `byoc-postgres` | `:25432` |
| mysql | `byoc-mysql` | `:13306` |
| sqlserver | `byoc-sqlserver` | `:11433` (needs ODBC Driver 18) |
| wis2 | `wis2box` harness | MQTT `:1883`, HTTP `:9080` |
| edis | `byoc-mailhog` | SMTP `:11025`, UI `:18025` |
| amhs / swim / afs | `byoc-f19` | HTTP `:19099` (`/amhs`, `/swim`, `/afs`) |

Allowlist:

```bash
export DISSEMINATION_EGRESS_ALLOWLIST=wis2box,127.0.0.1,127.0.0.0/8,localhost
```

Fixture file: `../mock-byoc-destinations.json`

## Candidates C1–C9

| ID | Sink | Fixture key |
|----|------|-------------|
| C1 | sqlite | `postgres_sqlite_standin` / live `live_api_sqlite_standin` |
| C2 | postgres | `postgres_compose` |
| C3 | mysql | `mysql_compose` |
| C4 | sqlserver | `sqlserver_compose` |
| C5 | wis2 | `wis2_compose_host` |
| C6 | edis | `edis_mailhog` |
| C7 | amhs | `f19_compose.params_by_sink.amhs` |
| C8 | swim | `f19_compose.params_by_sink.swim` |
| C9 | afs | `f19_compose.params_by_sink.afs` |

Payloads: `sample-metar.tac`, `sample-metar.iwxxm.xml` (Send requires IWXXM).

## Drawer paste cheatsheet

Send requires **IWXXM XML** (convert first, or drag-drop `sample-metar.iwxxm.xml`).

**SQLite (live smoke)**

- Sink: SQLite  
- URI: `sqlite+aiosqlite:////tmp/live-mock-byoc.db`  
- DDL: on  

**Postgres (local compose)**

- Sink: Postgres  
- URI: `postgresql+asyncpg://byoc:byoc-mock-password-not-real@127.0.0.1:25432/byoc`  
- DDL: on  

**MySQL**

- URI: `mysql+aiomysql://byoc:byoc-mock-password-not-real@127.0.0.1:13306/byoc`

**SQL Server**

- URI: `mssql+aioodbc://sa:Byoc_Mock_Passw0rd!@127.0.0.1:11433/master?TrustServerCertificate=yes`

**WIS2 BYOC JSON**

```json
{
  "mqtt_host": "127.0.0.1",
  "mqtt_port": 1883,
  "mqtt_topic": "origin/a/wis2/test-centre/data/core/weather/aviation/metar",
  "dataset_url": "http://127.0.0.1:9080/datasets/mock-metar.xml",
  "centre_id": "test-centre",
  "use_tls": false
}
```

**EDIS MailHog JSON**

```json
{
  "smtp_host": "127.0.0.1",
  "smtp_port": 11025,
  "mail_from": "mock-sender@example.test",
  "mail_to": "mock-rth@example.test",
  "use_tls": false,
  "tt": "SA",
  "aa": "US",
  "ii": "31",
  "cccc": "KXXX",
  "yygggg": "211200"
}
```

Omit `username` / `password` — MailHog has no AUTH.

**F19 (AMHS / SWIM / AFS) BYOC JSON**

```json
{
  "host": "127.0.0.1",
  "port": 19099,
  "endpoint": "/amhs",
  "username": "mock-f19",
  "password": "mock-f19-password-not-real"
}
```

Use `/swim` or `/afs` for the other sinks. Live HTTP API may still return 501 for non-DB sinks; package + harness cover local verification.

## Automated smokes

```bash
make test-mock-byoc-smoke          # unit/mocks
make compose-mock-byoc-all-up
make test-mock-byoc-all-sinks      # all 9 sinks
```
