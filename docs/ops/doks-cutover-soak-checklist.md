# DOKS cutover — 7-day soak checklist (F30 / EV-031)

> **Status**: **Closed early** (2026-08-03) — soak waived day 0/7 under **`D-S038-t65-waive`**; Render suspended (TC-F30-005)  
> **Decision**: `D-S038-04-b2` Q2=1 — **7 days** dual-traffic / soak before Render decommission (**waived** by `D-S038-t65-waive`)  
> **DNS waive**: `D-S038-t63-waive` — real DNS deferred; pin via LB `168.144.12.70` + Host-header / `/etc/hosts` placeholders  
> **Session**: S038-platform-independence-842 / EV-031  
> **Archive**: [render-decommission-archive.md](render-decommission-archive.md)  
> **Related**: ADR-033; TC-F30-004..005; UJ-048; [deploy.md](../deploy.md); `scripts/deploy/doks_host_header_smoke.sh`

## Provisional LIVE_* pin (until real DNS)

```bash
# /etc/hosts
# 168.144.12.70  api.doks.placeholder.metar-iwxxm.local app.doks.placeholder.metar-iwxxm.local

export LIVE_API_URL=http://api.doks.placeholder.metar-iwxxm.local
export LIVE_FRONTEND_URL=http://app.doks.placeholder.metar-iwxxm.local
export VITE_API_BASE_URL="${LIVE_API_URL}"

# Host-header smoke (no /etc/hosts required):
bash scripts/deploy/doks_host_header_smoke.sh
```

| Surface | Value |
|---------|-------|
| LB | `168.144.12.70` |
| API Host | `api.doks.placeholder.metar-iwxxm.local` |
| FE Host | `app.doks.placeholder.metar-iwxxm.local` |
| `config/prod.json` `liveE2e.*` | Provisional DOKS placeholders (above) |
| `config/prod.json` `api.baseUrl` / `frontendUrl` | Provisional DOKS placeholders (T6.5; Render suspended) |
| DOKS FE `/config.json` | ConfigMap `metar-frontend-runtime-config` → DOKS API host |

## Preconditions (start of soak = day 0)

- [x] DNS pin waived (`D-S038-t63-waive`) — placeholders + LB retained; residual: real DNS → re-pin
- [x] `alembic upgrade head` applied on DO Postgres (idempotent; initContainer)
- [x] Legacy Supabase product migrate verified (T5.x VERIFY PASS)
- [x] DOKS API + FE + worker healthy; Host-header H0/H3 convert green
- [ ] Auth login + work-sessions smoke (UJ-046) — optional during provisional HTTP
- [x] `LIVE_*` / `liveE2e` / `api.baseUrl` / `frontendUrl` → provisional DOKS (T6.5)
- [x] Render marked **suspended / non-primary** — T6.5 under `D-S038-t65-waive`
- [x] Full H4–H5 via `make test-live-connectivity-doks-provisional` (T7.2) — H0c 6/6, H4 2/2, H5 PASS on Host-header path; HTTPS + real DNS still deferred (`D-S038-t63-waive`)

## Daily checks (days 1–7)

| Day | Date | Health `/health` | H3 convert smoke | Auth session smoke | F8 store (if on) | Notes / incidents |
|-----|------|------------------|------------------|--------------------|------------------|-------------------|
| 0 | 2026-08-03 | PASS (Host-header) | PASS (metars JSON) | — | worker Running | `D-S038-t63-waive`; smoke script green |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

## Exit criteria (after day 7) — **waived early** (`D-S038-t65-waive`)

- [x] No open P0/P1 incidents attributable to DOKS primary (day 0 exit; risk accepted)
- [x] TC-F30-005 — Render decommission checklist (T6.5) — see [t6.5-render-decommission.md](../sessions/S038-platform-independence-842/reports/t6.5-render-decommission.md)
- [x] Archive Render `LIVE_*` as historical; CORPUS/deploy reflect DOKS-primary
- [x] Close soak in evolve-summary / deploy-report
- [ ] **Residual**: pin real DNS + retire placeholders before calling public cutover complete

## Abort / rollback

If DOKS primary fails soak: revert `LIVE_*` + CORS + FE runtime ConfigMap to Render transitional;
file BUG + pause T6.5. Do not delete Render until exit criteria pass.
