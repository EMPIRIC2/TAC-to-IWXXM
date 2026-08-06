# Technical specification hub

> **Corpus ID:** `tech-spec` — see [CORPUS.md](CORPUS.md).  
> **Architecture / components:** [spec.md](spec.md) (`system-spec`).  
> **Last updated:** 2026-08-06 (S047 / EV-039 — mock-byoc live SQL e2e pointer; prior 2026-07-12 S007)

This file is the **entry point** for runtime, configuration, deployment, and dependency
truth. Detail lives in the satellites below — do not duplicate long tables here.

## Satellites

| Doc | What it owns |
|-----|----------------|
| [config-spec.md](config-spec.md) | `config/{env}.json` fields, defaults, precedence, non-secret vs secret |
| [env-contract.md](env-contract.md) | Env var names, who consumes them (API / frontend / CI) |
| [deploy.md](deploy.md) | Render (and related) topology, deploy commands, integration checklist |
| [dependency-inventory.md](dependency-inventory.md) | Allowed packages; new deps need `[Decision]` + inventory update |

## Related corpus

| Doc | Role |
|-----|------|
| [spec.md](spec.md) | System architecture, component map, hard constraints |
| [api-contract.md](api-contract.md) | HTTP routes and payloads |
| [adr/](adr/) | Architecture decisions that constrain tech choices |
| [decisions/tech-decisions.md](decisions/tech-decisions.md) | Interview / stage tech decision log |

## Parity checklist (quick)

When changing runtime behavior or deploy/config:

1. Config key or env name exists in **config-spec** / **env-contract** (exact spelling).
2. Deploy topology and service names match **deploy.md**.
3. New library appears in **dependency-inventory** (or AskQuestion before adding).
4. Component boundaries still match **spec.md** §Component Overview.
5. If the change is a non-obvious trade-off, add or cite an **ADR**.

## Local mock BYOC / live SQL e2e (F16 — S047 / EV-039)

Disposable multi-DB destinations for operator dissemination tests live in Compose — **not**
production or DOKS services:

| Piece | Location |
|-------|----------|
| Overlay | `docker-compose.mock-byoc.yml` (profile `mock-byoc`) — Postgres, MySQL, SQL Server (+ MailHog / F19 harness) |
| Compose project | `-p metar-iwxxm-mock-byoc` (via `BYOC_COMPOSE`) so `down -v` cannot tear down backend/frontend |
| Make | `compose-mock-byoc-up` / `compose-mock-byoc-down` (`down -v --remove-orphans`); `*-all-*` with wis2box |
| Live suite | `make test-e2e-f16-live-sql` — up → Playwright `uj027-f16-live-sql.e2e.spec.ts` → always down |
| Flag | `F16_LIVE_SQL` — default **1** locally, **0** when `CI` is set; `test-live-e2e` / local `test-live` invoke LIVE when `1` |
| Allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` — see [env-contract.md](env-contract.md); local recipe below ([Corpus: adr/ADR-029]) |
| Fixtures | `docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json` |
| Live Playwright | TC-F16-LIVE-001..004 / UJ-027 live path — [test-plan.md](test-plan.md); separate from mocked H6′ |

### Local harness recipe (CORS + allowlist — H4–H5 local)

For TC-F16-LIVE against **local** API + FE + Compose DBs (host-published ports):

```bash
# API allowlist (hosts/CIDRs only — never secrets)
export DISSEMINATION_EGRESS_ALLOWLIST=wis2box,127.0.0.1,127.0.0.0/8,localhost

# Browser → API (local FE origin must be listed; Compose FE defaults to :18000)
export METAR_CORS_ORIGINS=http://localhost:18000,http://127.0.0.1:18000
# Or rely on config/local.json corsOrigins: ["http://localhost:18000"]

# Dedicated LIVE suite (Compose up/down included)
make test-e2e-f16-live-sql

# Or fold into local test-live / test-live-e2e (F16_LIVE_SQL defaults on when CI unset)
make test-live-e2e
# CI / opt-out:
F16_LIVE_SQL=0 make test-live-e2e
```

SQL Server may be skipped in CI (opt-in / heavy image); **local close** still requires all four
dialects (AC2 / AC7 / `D-S047-04` Q4).

**Teardown:** `compose-mock-byoc-down` removes the isolated project’s containers and volumes;
Playwright/pytest fixtures must not leave SQLite temp files or lingering processes after
pass/fail/skip.
