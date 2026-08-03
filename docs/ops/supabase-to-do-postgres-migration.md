# Ops: Supabase product DB → DigitalOcean Postgres (S038 / EV-031)

> **Status**: Requirements draft (01) — detailed scripts/DDL in **04-tech-plan**  
> **Features**: F30 / F31  
> **Related**: ADR-033; TC-EV031-001/002; `D-S038-spec-data` Q3=2

## Goal

One-time migration of legacy **product** rows from Supabase hosted Postgres into the single
DigitalOcean Postgres instance used by API sessions + F8 (`DATABASE_URL`). After cutover,
Supabase is **Auth/JWT only** — no product PostgREST reads/writes on the default path.

## In scope

| Asset | Notes |
|-------|-------|
| `tac_work_sessions` (and related F5/F7 session tables if any remain) | Owner = Supabase Auth `user_id` (UUID) preserved |
| F8 store / quarantine tables (if currently on Supabase) | Same DO database as sessions |
| Schema | Alembic (or backend migration path) against `DATABASE_URL` before/with data load |

## Out of scope

- Migrating Auth users (remain in Supabase Auth)
- Long-lived dual-write between Supabase DB and DO
- Convert/validate engine changes

## High-level steps

1. Provision DO Postgres; set `DATABASE_URL` on API + worker.
2. Apply Alembic migrations to empty (or baseline) DO schema (**TC-EV031-002**).
3. Export legacy Supabase product tables (service-role / DB dump — ops only).
4. Transform/load into DO (preserve `user_id`, timestamps, soft-delete flags).
5. Dry-run checksum / row-count sample (**TC-EV031-001**).
6. Cut API/worker to DO-only; confirm zero Supabase DB product traffic (**TC-F30-001/002**).
7. Archive or delete Supabase product tables per #830 amend (retain Auth project).

## Verification

- TC-EV031-001 / TC-EV031-002
- TC-F30-001..003
- Login session CRUD against DO (**TC-EV031-004**)
- Public convert still JWT-free (**TC-EV031-003**)

## Open for 04-tech-plan

- Exact table list + column map
- Tooling (pg_dump / custom script / ETL)
- Soak window before Render decommission (separate from this data move)
