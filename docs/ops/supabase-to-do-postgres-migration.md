# Ops: Supabase product DB → DigitalOcean Postgres (S038 / EV-031)

> **Status**: **T5.1 table/column map finalized** (2026-08-03)  
> **Features**: F30 / F31  
> **Related**: ADR-033; TC-EV031-001/002; `D-S038-spec-data` Q3=2; Alembic
> `apps/backend/alembic/versions/20260803_0001_initial_product_schema.py`

## Goal

One-time migration of legacy **product** rows from Supabase hosted Postgres into the single
DigitalOcean Postgres instance used by API sessions + F8 (`DATABASE_URL`). After cutover,
Supabase is **Auth/JWT only** — no product PostgREST reads/writes on the default path.

## Target schema (DO / Alembic head)

Apply `alembic upgrade head` on DO **before** data load (**TC-EV031-002**). Revision
`20260803_0001` creates:

| Table | Purpose |
|-------|---------|
| `tac_work_sessions` | Logged-in F5/F7/F31 work history (ADR-020 shapes + `swxa`) |
| `iwxxm_ingest_results` | F8 successful ingest store |
| `iwxxm_ingest_quarantine` | F8 quarantine |

**Do not** recreate Supabase RLS, `auth.users` FKs, or `pg_cron` purge jobs on DO — ownership
is enforced by API JWT (`user_id` claim), not Postgres RLS.

## Table / column map (T5.1)

### `tac_work_sessions`

| Column | Legacy Supabase | DO Alembic | Transform |
|--------|-----------------|------------|-----------|
| `id` | UUID PK | UUID PK (`gen_random_uuid`) | Copy as-is |
| `user_id` | UUID **FK → `auth.users`** | UUID **no FK** | Copy UUID (Auth users stay in Supabase) |
| `product` | TEXT CHECK (… + `swxa`) | Same CHECK incl. `swxa` | Copy; reject unknown products |
| `status` | `draft`/`wip`/`finished`/`failed` | Same | Copy |
| `title` | TEXT | TEXT | Copy |
| `manual_tac` | TEXT | TEXT | Copy |
| `pending_files` | JSONB | JSONB | Copy |
| `converted_results` | JSONB | JSONB | Copy |
| `errors` | JSONB | JSONB | Copy |
| `issues` | JSONB | JSONB | Copy |
| `conversion_params` | JSONB | JSONB | Copy |
| `kv_upload_key` | TEXT NULL | TEXT NULL | Copy (metadata only — never destination secrets) |
| `deleted_at` | TIMESTAMPTZ NULL | TIMESTAMPTZ NULL | Copy |
| `created_at` | TIMESTAMPTZ | TIMESTAMPTZ | Copy |
| `updated_at` | TIMESTAMPTZ | TIMESTAMPTZ | Copy |

**Indexes (recreated by Alembic — do not dump):**
`idx_tac_work_sessions_user_updated`, `idx_tac_work_sessions_user_product`,
`tac_work_sessions_one_wip_per_user`.

**Drop on load (Supabase-only):** RLS policies, `REFERENCES auth.users`, triggers
(`tac_work_sessions_touch`), `purge_stale_tac_work_sessions` / cron.

**Legacy `metar_work_sessions`:** Already expand-cutover into `tac_work_sessions` on Supabase
(`20260714000010`). If any environment still has only `metar_work_sessions`, map via the same
INSERT…SELECT product inference as that migration, then load into DO `tac_work_sessions`.

### `iwxxm_ingest_results` / `iwxxm_ingest_quarantine`

| Column | Legacy Supabase | DO Alembic | Transform |
|--------|-----------------|------------|-----------|
| `id` | UUID PK | UUID PK | Copy |
| `job_id` | TEXT | TEXT | Copy |
| `product` | TEXT | TEXT | Copy |
| `profile` | TEXT default `annex3` | Same | Copy |
| `source_url` | TEXT | TEXT | Copy |
| `tac_input` | TEXT | TEXT | Copy |
| `iwxxm_xml` | TEXT (nullable on quarantine) | Same | Copy |
| `issues` | JSONB | JSONB | Copy |
| `stage_failed` | TEXT NULL | TEXT NULL | Copy |
| `created_at` | TIMESTAMPTZ | TIMESTAMPTZ | Copy |

**Drop on load:** RLS (service-role-only on Supabase). Indexes recreated by Alembic.

## Out of scope

- Migrating Auth users (remain in Supabase Auth)
- Long-lived dual-write between Supabase DB and DO
- Convert/validate engine changes
- Recreating Supabase RLS / `auth.users` FK / cron purge on DO

## Tooling (locked for T5.2+)

| Step | Tool |
|------|------|
| Schema | `alembic upgrade head` against `DATABASE_URL` |
| Export | `pg_dump --data-only --table=…` from Supabase DB URI (ops secret) **or** SQL `COPY` |
| Load | `pg_restore` / `psql` into DO after schema; prefer `INSERT … ON CONFLICT (id) DO NOTHING` for idempotent dry-runs |
| Verify | T5.2 script — row counts + sample checksum (**TC-EV031-001**) |

Recommended dump order: `tac_work_sessions` → `iwxxm_ingest_results` → `iwxxm_ingest_quarantine`.

## High-level steps

1. Provision DO Postgres; set `DATABASE_URL` on API + worker.
2. Apply Alembic migrations to empty (or baseline) DO schema (**TC-EV031-002**).
3. Export legacy Supabase product tables (DB dump — ops only; not service-role as product SoT).
4. Transform/load into DO per column map above (strip `auth.users` FK / RLS).
5. Dry-run checksum / row-count sample (**TC-EV031-001** / T5.2).
6. Cut API/worker to DO-only; confirm zero Supabase DB product traffic (**TC-F30-001/002**).
7. Archive or delete Supabase product tables per #830 amend (retain Auth project).

## Verification

- TC-EV031-001 / TC-EV031-002
- TC-F30-001..003
- Login session CRUD against DO (**TC-EV031-004**)
- Public convert still JWT-free (**TC-EV031-003**)

## Soak / cutover note

Data migrate (M5) is independent of the **7-day** DOKS dual-traffic soak (M6 / `D-S038-04-b2`).
Render decommission follows soak checklist — not this data move alone.
