# Evolve summary — EV-031 / S038 (platform independence #842 / #830 / #712)

> Date: 2026-08-03  
> Status: **Phase D deploy smoke green** — awaiting 13 result approval / cycle close  
> Branch: `evolve/EV-031-platform-independence-842`  
> Features: **F30**, **F31**; deepen F5 / F7 / F8 / F21 / F22 / M4  
> ADR: [ADR-033](../../../adr/ADR-033-platform-independence-auth-do-doks.md) (Accepted)

## Outcomes (to date)

| Issue / Fn | Result |
|------------|--------|
| [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842) | Platform independence — DOKS primary; Render suspended (`D-S038-t65-waive`) |
| [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830) | Amended Auth-kept; Supabase data plane stripped (Auth-only) |
| [#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712) | DOKS IaC + provisional Host-header LIVE_* |
| **F30** | DO Postgres product DB; DOKS API/FE/worker; H4–H5 provisional PASS; TC-F30-005 PASS |
| **F31** | Hybrid sessions — guest notice + Auth restore + auto-upload path |

## Milestones

| M | Scope | Result |
|---|-------|--------|
| M0–M5 | Auth restore, Alembic, F8→DATABASE_URL, migrate | completed (verification reports M1–M5) |
| M6 | DOKS IaC + cutover + soak | T6.1–T6.5 completed (`D-S038-t65-waive`) |
| M7 | H4–H5 / live verify / close docs | T7.1–T7.4 completed |

## Live verify (provisional DOKS)

| Task | Result | Report |
|------|--------|--------|
| T7.1 Playwright F31 | 13/13 PASS | [t7.1-playwright-live-provisional.md](t7.1-playwright-live-provisional.md) |
| T7.2 H4–H5 | H0c 6/6, H4 2/2, H5 PASS | [t7.2-h4-h5-connectivity-provisional.md](t7.2-h4-h5-connectivity-provisional.md) |
| T7.3 TC-EV031 topology | unit 31 + live 3/3 PASS | [t7.3-tc-ev031-topology.md](t7.3-tc-ev031-topology.md) |
| T6.5 Render decommission | Suspend API+FE+worker; archive LIVE_* | [t6.5-render-decommission.md](t6.5-render-decommission.md) |

LB `168.144.12.70` · Hosts `api|app.doks.placeholder.metar-iwxxm.local`

## Residuals

- GHCR `write:packages` — republish `backend:ev031-doks` + `frontend:ev031-doks`; remove ConfigMap sslmode mount + FE hot-copy
- Real DNS / HTTPS — lift `D-S038-t63-waive`
- Evolve PR → `main` after Phase D / cycle close

## CORPUS parity

See [corpus-parity-note.md](corpus-parity-note.md).
