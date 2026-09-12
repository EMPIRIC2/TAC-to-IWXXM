# Requirements delta — S038 / EV-031

**Stage:** 01-requirements (delta)  
**Features:** F30, F31 (deepen F5/F7/F8/F21/F22/M4)  
**Issues:** #842, #830 (amended), #712  
**Updated:** 2026-08-03

## Locked product decisions

| ID | Decision |
|----|----------|
| Topology | Supabase Auth-only; DO Postgres product DB; DOKS compute |
| Convert APIs | Public (no JWT) |
| Sessions | Guest IndexedDB + notice; logged-in DO Postgres; auto-upload on login |
| F21 | Amended (optional Auth for long-term storage) |
| Auth package | Restore `packages/auth` |
| Session API | Restore `/api/v1/work-sessions*` (JWT) |
| Schema | Single DO Postgres (sessions + F8); Alembic on `DATABASE_URL` |
| Legacy | One-time migrate Supabase product rows → DO this cycle |
| Test Plan | TC-F30-001..006; TC-F31-001..006; TC-EV031-001..004; H4–H5 **required** (`D-S038-tp`) |

## Documents touched

- [x] Feature List — F30/F31 + amends
- [x] Spec — runtime, components, F5–F31, constraints, security
- [x] User Journeys — UJ-045..048; deepen 001/004/033; UJ-003 restored via 046
- [x] Test Plan — TC-F30/F31/EV031; UJ map; H4–H5 required; TC-F21-auth-gone amended
- [x] Config / env-contract — Auth restore; `DATABASE_URL` required; DOKS live URLs
- [x] API Contract — `/auth/*` + work-sessions restored; convert public
- [x] Deploy docs — DOKS target; Render transitional; cutover checklist
- [x] Dependency inventory — `packages/auth`, alembic, supabase-js restore notes
- [x] ADRs — ADR-033 Proposed; ADR-031 partially superseded; index updated
- [x] Data / migration note — `docs/ops/supabase-to-do-postgres-migration.md`

## Standing doc paths

- `docs/feature-list.md`
- `docs/spec.md`
- `docs/user-journeys.md`
- `docs/test-plan.md`
- `docs/config-spec.md`
- `docs/env-contract.md`
- `docs/api-contract.md`
- `docs/deploy.md`
- `docs/dependency-inventory.md`
- `docs/adr/ADR-033-platform-independence-auth-do-doks.md`
- `docs/ops/supabase-to-do-postgres-migration.md`
- `docs/decisions/evolve-decisions.md` §EV-031
- `docs/decisions/requirements-decisions.md` §EV-031

## Deferred to 04-tech-plan — **resolved in 04 Batches 1–2**

| Gap | Resolution |
|-----|------------|
| DOKS hostnames / DNS | Placeholder until M6 (`D-S038-04-b2` Q1=1) |
| Alembic + session repo | `apps/backend/` Alembic + SQLAlchemy; CI auto idempotent `upgrade head` |
| JWT verify | **JWKS-only** (`D-S038-04-b1` Q2=2) |
| Soak | **7 days** after DOKS primary |
| Work-session wire | Restore ADR-020 shapes; ADR-033 accept at Gate B |
