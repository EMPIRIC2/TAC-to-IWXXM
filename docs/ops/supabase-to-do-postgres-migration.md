# Ops: Supabase product DB → DigitalOcean Postgres (S038 / EV-031)

> **Status**: **T5.3 migrate runner landed** (2026-08-03); T5.2 verify + T5.1 map  
> **Features**: F30 / F31  
> **Related**: ADR-033; TC-EV031-001/002; `D-S038-spec-data` Q3=2; Alembic
> `apps/backend/alembic/versions/20260803_0001_initial_product_schema.py`  
> **Migrate**: `scripts/ops/run_supabase_to_do_migrate.py`  
> **Verify**: `scripts/ops/verify_supabase_to_do_migrate.py`

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
| Schema | `alembic upgrade head` against DO `DATABASE_URL` |
| Export / load | `scripts/ops/run_supabase_to_do_migrate.py` — SQLAlchemy `SELECT` + idempotent `INSERT … ON CONFLICT (id) DO NOTHING` (**T5.3** default). Optional `--use-pg-dump` when `pg_dump`/`pg_restore` are on `PATH`. |
| Verify | `scripts/ops/verify_supabase_to_do_migrate.py` — row counts + sample checksum (**TC-EV031-001** / T5.2) |

Recommended order: `tac_work_sessions` → `iwxxm_ingest_results` → `iwxxm_ingest_quarantine`.

**Safety:** the migrate script **refuses** when source and target resolve to the same
host/db/user (guards against a still-Supabase `DATABASE_URL`).

### Migrate commands (T5.3)

```bash
# Source = legacy Supabase Postgres; target = DO Postgres (not Supabase)
export MIGRATE_SOURCE_DATABASE_URL="postgresql://…"   # or SUPABASE_DB_URL
export MIGRATE_TARGET_DATABASE_URL="postgresql://…"   # DO — prefer over DATABASE_URL

# 1) Dry-run (default) — plan only; no writes
make migrate-supabase-to-do MODE=dry-run
# or:
uv run python scripts/ops/run_supabase_to_do_migrate.py \
  --source-url "$MIGRATE_SOURCE_DATABASE_URL" \
  --target-url "$MIGRATE_TARGET_DATABASE_URL" \
  --mode dry-run --json

# 2) Apply cut (idempotent) + T5.2 verify
make migrate-supabase-to-do MODE=apply VERIFY=1
# or:
uv run python scripts/ops/run_supabase_to_do_migrate.py \
  --source-url "$MIGRATE_SOURCE_DATABASE_URL" \
  --target-url "$MIGRATE_TARGET_DATABASE_URL" \
  --mode apply --verify --json
```

Optional dump path (requires Homebrew `libpq` / `pg_dump` on `PATH`):

```bash
uv run python scripts/ops/run_supabase_to_do_migrate.py \
  --source-url "$MIGRATE_SOURCE_DATABASE_URL" \
  --target-url "$MIGRATE_TARGET_DATABASE_URL" \
  --mode apply --use-pg-dump --verify
```

### Verify command (T5.2)

```bash
uv run python scripts/ops/verify_supabase_to_do_migrate.py \
  --source-url "$MIGRATE_SOURCE_DATABASE_URL" \
  --target-url "$MIGRATE_TARGET_DATABASE_URL" \
  --json
```

Compares `tac_work_sessions`, `iwxxm_ingest_results`, and `iwxxm_ingest_quarantine`:
full **row counts** plus a SHA-256 **sample checksum** (first N rows by `id`, default
N=100) over the T5.1 fingerprint columns. Exit `0` = match; `1` = mismatch; `2` = DB error.

## High-level steps

1. Provision DO Postgres; set `MIGRATE_TARGET_DATABASE_URL` / `DATABASE_URL` on API + worker
   (must **not** still point at Supabase).
2. Apply Alembic migrations to empty (or baseline) DO schema (**TC-EV031-002** /
   `make db-migrate`).
3. Dry-run migrate plan (**T5.3**): `make migrate-supabase-to-do MODE=dry-run`.
4. Apply idempotent load (**T5.3**): `make migrate-supabase-to-do MODE=apply VERIFY=1`
   (column map above; no `auth.users` FK / RLS on DO).
5. Confirm T5.2 verify PASS (row counts + sample checksum) (**TC-EV031-001**).
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
