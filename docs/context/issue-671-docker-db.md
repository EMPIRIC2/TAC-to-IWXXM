# Context — Issue #671 Docker DB Table Creation Failure

> **Mode**: scoped | **Slug**: issue-671-docker-db | **Generated**: 2026-06-25
> **Feature / workflow**: [GitHub #671](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671) — Docker Compose backend fails to create database tables | **Status**: active

## Executive Summary

A user following the README "Quick Start with Docker Compose" reports the backend logging
`Failed to create database tables: Multiple exceptions: [Errno 111] Connect call failed
('127.0.0.1', 5432)`. Root cause: on startup `database_lifespan` → `create_tables()` resolves
its URL via `get_database_url()`, which **falls back to `postgresql+asyncpg://postgres:@localhost:5432/postgres`**
whenever `DATABASE_URL` (and `SUPABASE_DB_URL` / `POSTGRES_*`) are unset. In `docker-compose.yml`
the backend receives `DATABASE_URL=${DATABASE_URL:-}` — an **empty string**, which is falsy in
Python, so it falls through to the localhost default. There is **no Postgres listener inside the
backend container**, so the connect call is refused. The error is **caught and not re-raised**
(`create_tables` swallows it), so the app still reaches `Application startup complete` and `/health`
returns 200 — but the alarming traceback reads as a hard failure and DB-backed features
(statistics/evaluation) do not work.

Two contextual facts shape the fix:
1. **The reporter is on a pre-monorepo build** — their logs show three containers
   (`metar-iwxxm-auth`, `-backend`, `-frontend`) and `src/...` paths. The current monorepo
   `docker-compose.yml` has only `backend` + `frontend` (no `auth`, no `postgres`), and the
   project now uses **managed Postgres (Supabase)** — there is no DB container at all.
2. **Still reproducible on `main`** — `docker compose up --build` without `DATABASE_URL` in `.env`
   produces the same backend traceback today.

**Approved scope (user, 2026-06-25):** add a **bundled Postgres service** to `docker-compose.yml`
so `docker compose up` is self-contained out of the box, wiring `DATABASE_URL` to it by default.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | **Session** — close merged S004; open hotfix session **S005** for #671 |
| R2 | Decision | **Fix approach** — bundle a Postgres service in `docker-compose.yml` and default the backend `DATABASE_URL` to that service so `docker compose up --build` is self-contained (vs. fail-fast+docs only, or issue-reply only) |
| R3 | Constraint | **Bundled PG covers ORM tables only** — `create_tables()` builds SQLAlchemy ORM models (statistics/evaluation). Auth + F5 `metar_work_sessions` live in **Supabase** (RLS + supabase migrations) and are **not** provisioned by a bare local Postgres. Login/work-history still require Supabase config locally. |
| R4 | Scope | **#671 is not a duplicate of #688** — #688 (CLOSED) was a frontend `npm install` vs `workspace:*` build failure; #671 is a backend DB-connection issue. |

## Scope & Constraints

**In scope (#671)**

| Item | Component | Notes |
|------|-----------|-------|
| Add Postgres service to compose | `docker-compose.yml` | image (e.g. `postgres:16`), healthcheck, named volume, `metar-network` |
| Default backend `DATABASE_URL` to bundled DB | `docker-compose.yml` | e.g. `postgresql+asyncpg://postgres:postgres@db:5432/postgres`; keep `${DATABASE_URL:-<default>}` override |
| `depends_on` DB health before backend | `docker-compose.yml` | mirror existing frontend→backend `service_healthy` gate |
| Confirm/handle empty-string env footgun | `apps/backend/src/services/database.py` | `${DATABASE_URL:-}` → empty string is falsy; ensure default or clearer log when unset |
| README / DEVELOPMENT Docker note | `README.md`, `docs/DEVELOPMENT.md` | document that compose now ships a DB; Supabase still needed for auth/work-history |
| Repro + regression test | `tests/bugs/` + integration compose smoke | per bug-investigation skill |
| Issue reply | GitHub #671 | explain new layout + fix |

**Out of scope (unless user expands)**

- Migrating the app off Supabase, or replicating Supabase auth/RLS/work-history schema into the
  bundled Postgres (R3 — bundled DB serves ORM tables only).
- Production / Render topology changes — prod uses Supabase; compose is local-dev only.
- Frontend Docker build (#688, already closed).
- Behavioral rewrites of conversion/validation (REQ-016).

**Linked issues**

- [#688](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/688) (CLOSED) — frontend Docker `workspace:*` build bug (related theme, distinct root cause).

## Environment / Topology

Local Docker Compose only. Current services: `backend` (`:18001→8000`) + `frontend`
(`:18000→8000`) on bridge network `metar-network`. No DB service today. Fix adds a `db`
(Postgres) service on the same network; backend connects via service DNS name (e.g. `db:5432`),
not `localhost`. No change to deployed Render topology (Supabase-managed Postgres).

## Existing Infrastructure

| Asset | Path | Relevance |
|-------|------|-----------|
| DB URL resolution | `apps/backend/src/services/database.py` `get_database_url` L37–60 | Falls back to `postgresql+asyncpg://postgres:@localhost:5432/postgres` when env unset |
| Engine + table create | `apps/backend/src/services/database.py` `database_lifespan` L220–238, `create_tables` L241–262 | `create_tables` logs error but does **not** raise |
| App lifespan wiring | `apps/backend/src/api.py` L82 | `lifespan=database_lifespan` runs DB init on startup |
| Compose services | `docker-compose.yml` L1–63 | `backend` + `frontend` only; `DATABASE_URL=${DATABASE_URL:-}` (empty default) |
| Env template | `.env.example` L6 | `DATABASE_URL=` (blank) |
| Required-env doc | `docs/DEVELOPMENT.md` L100 | `DATABASE_URL` marked **Yes** (Postgres pooler for evaluation/statistics) |
| DB service tests | `apps/backend/tests/unit/test_database_service_unit.py`, `tests/services/test_database_service.py` | Cover URL precedence + lifespan; extend for new default |
| Bug report template | `docs/bug-reports/_template.md` | New BUG report per bug-investigation skill |

## Cross-Reference Matrix

| Source | Postgres in compose | Backend `DATABASE_URL` default | Auth/work-history store | Startup hard-fails? |
|--------|---------------------|--------------------------------|-------------------------|---------------------|
| Reporter (pre-monorepo) | auth+backend+frontend, no pg | unset → `localhost:5432` | local PG (old design) | No (caught) — perceived fail |
| Current `main` | none | `${DATABASE_URL:-}` → empty → `localhost:5432` | Supabase | No (caught) |
| Approved fix (R2) | `db` service | `db:5432` default, overridable | Supabase (unchanged) | No |
| `docs/DEVELOPMENT.md` | n/a | required (pooler) | Supabase | n/a |

## Implementation Backlog

1. **Repro (bug-investigation)** — script/test that `docker compose up` (no `.env` `DATABASE_URL`)
   triggers the `Connect call failed ('127.0.0.1', 5432)` log; expect red.
2. **Add `db` service (R2)** — `postgres:16` (pin), env `POSTGRES_PASSWORD`, named volume,
   `pg_isready` healthcheck, on `metar-network`.
3. **Wire backend** — set compose `DATABASE_URL` default to `postgresql+asyncpg://postgres:postgres@db:5432/postgres`
   (still `${DATABASE_URL:-...}` overridable); add `depends_on: db: condition: service_healthy`.
4. **Empty-string footgun** — decide whether to treat blank `DATABASE_URL` like unset in
   `get_database_url` and/or emit an actionable warning naming the missing env var.
5. **Tests** — extend `test_database_service_unit.py` for the new precedence/default; add an
   integration compose smoke (backend reaches DB, `/health` 200, no table-create error).
6. **Docs** — README Quick Start + `docs/DEVELOPMENT.md`: compose ships a DB; Supabase still
   required for login + F5 work-history (R3).
7. **Issue reply** — post on #671: new monorepo layout (no auth/pg containers in old sense),
   the bundled-DB fix, and the Supabase requirement for auth features.

## Data & Credentials

No production secrets. Bundled Postgres uses a local dev password (compose-scoped, non-secret).
Auth/work-history features still need real Supabase `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`
in `.env` (never commit). Reporter attached full logs; no sample data needed.

## Unresolved Gaps

- **Auth/work-history locally** — bundled bare Postgres does not provision Supabase auth or
  `metar_work_sessions` RLS schema (R3); 14-hotfix must document the residual Supabase requirement
  or decide whether to point compose at a local `supabase start` stack instead.
- **`statement_cache_size=0` connect_args** — tuned for PgBouncer/Supabase pooler; harmless against
  vanilla Postgres but worth a sanity check.
- **Reporter version drift** — fix targets current `main`; reporter should re-pull post-fix.

## Sources

- [GitHub #671](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671) — issue body + full logs (2026-05-28)
- [GitHub #688](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/688) — related frontend Docker bug (CLOSED)
- [Repo: apps/backend/src/services/database.py](apps/backend/src/services/database.py) — `get_database_url`, `database_lifespan`, `create_tables`
- [Repo: docker-compose.yml](docker-compose.yml) — backend/frontend services, `DATABASE_URL=${DATABASE_URL:-}`
- [Repo: apps/backend/src/api.py](apps/backend/src/api.py) L82 — `lifespan=database_lifespan`
- [Repo: .env.example](.env.example), [Repo: docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) L100 — required env
