# 04-tech-plan — S038 / EV-031

**Started**: 2026-08-03  
**Completed**: 2026-08-03  
**Mode**: evolve delta  
**Features**: **F30**, **F31** (deepen F5/F7/F8/F21/F22/M4)  
**Branch**: `evolve/EV-031-platform-independence-842`  
**Status**: **completed** — Gate B PASS (`D-S038-04-plan`=1); ADR-033 **Accepted**  
**Prior Gate A**: `6b7fd0e`

## Toolchain baseline

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Auth | Restore `packages/auth` from pre-delete (`c9cebfa^`); strip admin; Auth-only |
| JWT verify | **JWKS-only** from day one (`D-S038-04-b1` Q2=2) |
| DB | DigitalOcean Postgres via `DATABASE_URL` |
| Migrations | Alembic under `apps/backend/`; **CI auto `upgrade head`**; **idempotent** |
| Data migrate | `pg_dump`/`pg_restore` + verify script |
| Session wire | ADR-020 JSON shapes |
| F8 | Same `DATABASE_URL` schema |
| Deploy | DOKS cutover; **7-day** soak; Render decommission |
| Hostnames | Placeholder until M6 |
| Connectivity | H4–H5 **required** |

## Interview locks

| Batch | Decision |
|-------|----------|
| Batch 1 `1,2,1,1` | M0–M7; **JWKS-only**; Alembic in backend; restore `packages/auth` from git + strip admin |
| Batch 2 `1,1,1(+CI),1` | Placeholder DNS; **7d soak**; pg_dump + **CI auto idempotent Alembic**; ADR-020 wire; ADR-033 @ Gate B |
| Gate B `1` | Approve plan + accept ADR-033 → **07-build** @ T0.1 (`D-S038-04-plan`) |

## Milestone skeleton

| M | Focus | Tasks |
|---|--------|-------|
| M0 | ADR-033 / #830 / deps / placeholder DNS / soak stub | T0.1–T0.4 |
| M1 | Auth restore JWKS | T1.1–T1.4 |
| M2 | Alembic + CI migrate + work-sessions | T2.1–T2.6 |
| M3 | F8 → `DATABASE_URL` | T3.1–T3.3 |
| M4 | FE hybrid + F22 | T4.1–T4.5 |
| M5 | Supabase → DO one-time migrate | T5.1–T5.4 |
| M6 | DOKS IaC + cutover + 7d soak | T6.1–T6.5 |
| M7 | H4–H5 / live verify | T7.1–T7.4 |

**Total:** 38 tasks — see `reports/execution-plan.md`

## Artifacts

- `reports/execution-plan.md` — **approved** (Gate B)
- This report — **completed**
- ADR-033 — **Accepted**

## Next

**07-build** @ T0.1 (M0 — ADR supersession notes / #830 amend / deps / placeholder DNS).
