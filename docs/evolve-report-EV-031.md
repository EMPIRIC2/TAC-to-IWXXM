# Evolve report — EV-031

| Field | Value |
|-------|-------|
| Cycle | EV-031 |
| Session | S038-platform-independence-842 |
| Status | **completed** |
| Started | 2026-08-03 |
| Completed | 2026-08-03 |
| Features | **F30**, **F31** (deepen F5/F7/F8/F21/F22/M4) |
| Issues | [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842), [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830), [#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712) |
| ADR | [ADR-033](adr/ADR-033-platform-independence-auth-do-doks.md) Accepted |
| Branch | `evolve/EV-031-platform-independence-842` |
| Deploy smoke (13) | **PASS** — provisional DOKS Host-header 5/5; H0c/H4/H5; topology 3/3; Render 503 |
| Close decision | `D-S038-13` = **1** (approve 13; close Phase D / cycle closeout) |

## Scope

Platform independence epic: Supabase **Auth-only**; DigitalOcean Postgres product DB;
DOKS production cutover with Render suspended; hybrid guest IndexedDB + Auth→DO sessions
with auto-upload and F22 gates. Placeholders for public DNS (`D-S038-t63-waive`); soak
waived day 0 (`D-S038-t65-waive`).

## Routing

Standard: `00→16→01→02→04→07→08→09→10→11→12→13` (skip 03/05/06).

## Results

| Gate | Result |
|------|--------|
| A→B | passed (`D-S038-02-phase-a`) |
| B→C | passed (`D-S038-04-plan`; ADR-033 Accepted) |
| C→D | passed (M0–M7; 08 PASS `67a482a1`) |
| Deploy (13) | passed (`D-S038-13` = 1) — provisional DOKS |

## Verification

- 08-verify-build: pass
- 09-qa: pass (advisories) · 10-e2e: pass (T0 8/8 + T7 T3)
- 11-verify-impl: approved F30+F31 (`D-S038-11` = 1; UI preview skipped)
- 12-verify-deploy: approved (`D-S038-12` = 1)
- 13-deploy-smoke: pass — [deploy-smoke.md](sessions/S038-platform-independence-842/reports/deploy-smoke.md)

## Topology (post-cutover)

| Layer | Target |
|-------|--------|
| Compute | DOKS `metar-iwxxm` (primary) |
| LB | `168.144.12.70` + placeholder Hosts |
| Product DB | DigitalOcean Postgres (`DATABASE_URL`) |
| Auth | Supabase Auth (JWKS-only) |
| Render | Suspended |

## Follow-ups

- Real public DNS + HTTPS — lift `D-S038-t63-waive`
- GHCR republish `backend:ev031-doks` + `frontend:ev031-doks` (drop ConfigMap sslmode / FE hot-copy)
- Close/update GitHub issues #842 / #830 / #712 after PR merge as appropriate
- Optional: 15-service-health / 17-retrospective

## Session artifacts

- [evolve-summary.md](sessions/S038-platform-independence-842/reports/evolve-summary.md)
- [deploy-smoke.md](sessions/S038-platform-independence-842/reports/deploy-smoke.md)
- [verify-impl.md](sessions/S038-platform-independence-842/reports/verify-impl.md)
- [deploy-checklist.md](sessions/S038-platform-independence-842/reports/deploy-checklist.md)
- [evolve-decisions.md](decisions/evolve-decisions.md) §Cycle EV-031
