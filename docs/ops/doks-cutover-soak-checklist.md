# DOKS cutover — 7-day soak checklist (F30 / EV-031)

> **Status**: **Stub** (T0.4) — fill dates/owners at **T6.4** when DOKS is primary  
> **Decision**: `D-S038-04-b2` Q2=1 — **7 days** dual-traffic / soak before Render decommission  
> **Session**: S038-platform-independence-842 / EV-031  
> **Related**: ADR-033; TC-F30-004..005; UJ-048; [deploy.md](../deploy.md)

## Preconditions (start of soak = day 0)

- [ ] Real DNS pinned (T6.3) — placeholders retired
- [ ] `alembic upgrade head` applied on DO Postgres (idempotent)
- [ ] Legacy Supabase product migrate verified (T5.x) or explicitly N/A
- [ ] DOKS API + FE + worker healthy; H0–H5 green against DOKS URLs
- [ ] Auth login + work-sessions smoke (UJ-046); public convert still works
- [ ] `LIVE_*` / `config/prod.json` point at DOKS primary
- [ ] Render marked **drain / non-primary** (or read-only) for the soak window

## Daily checks (days 1–7)

| Day | Date | Health `/health` | H3 convert smoke | Auth session smoke | F8 store (if on) | Notes / incidents |
|-----|------|------------------|------------------|--------------------|------------------|-------------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

## Exit criteria (after day 7)

- [ ] No open P0/P1 incidents attributable to DOKS primary
- [ ] TC-F30-004..005 path ready; Render decommission checklist (T6.5)
- [ ] Archive Render `LIVE_*` as historical; CORPUS/deploy reflect DOKS-only
- [ ] Close soak in evolve-summary / deploy-report

## Abort / rollback

If DOKS primary fails soak: revert `LIVE_*` + CORS + DNS to Render transitional;
file BUG + pause T6.5. Do not delete Render until exit criteria pass.
