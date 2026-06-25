# BUG-2026-06-25-docker-db-connect-localhost-5432

| Field | Value |
|-------|-------|
| Status | verifying |
| Severity | high |
| Feature | F3 / infra (Docker Compose local-dev stack) |
| Remediation path | local-first |
| GitHub issue | [#671](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671) |
| Session | S005-issue-671-docker-db |

## Error description

A user following the README "Quick Start with Docker Compose" reports the backend logging
`Failed to create database tables: Multiple exceptions: [Errno 111] Connect call failed
('::1', 5432, 0, 0), [Errno 111] Connect call failed ('127.0.0.1', 5432)`.

The backend resolves its database URL via `get_database_url()`, which falls back to
`postgresql+asyncpg://postgres:@localhost:5432/postgres` when `DATABASE_URL` (and
`SUPABASE_DB_URL` / `POSTGRES_*`) are unset. In `docker-compose.yml` the backend receives
`DATABASE_URL=${DATABASE_URL:-}` — an **empty string**, which is falsy in Python, so it falls
through to the localhost default. There is **no Postgres listener inside the backend container**,
so the connect call is refused. `create_tables()` catches and does not re-raise the error, so
the app still reaches `Application startup complete` and `/health` returns 200 — but the
alarming traceback reads as a hard failure and DB-backed features (statistics/evaluation) do
not work.

## Error logs

```
metar-iwxxm-backend  | {"level": "WARNING", "logger": "src.services.database", "message": "No PostgreSQL password configured, using passwordless connection"}
metar-iwxxm-backend  | {"level": "INFO", "logger": "src.services.database", "message": "Initializing database engine with URL: postgresql+asyncpg://postgres:@localhost:5432/post..."}
metar-iwxxm-backend  | {"level": "ERROR", "logger": "src.services.database", "message": "Failed to create database tables: Multiple exceptions: [Errno 111] Connect call failed ('::1', 5432, 0, 0), [Errno 111] Connect call failed ('127.0.0.1', 5432)", ...}
```

## Symptoms & reproduction

- **Where:** Local `docker compose up --build` (reporter on Docker 29.5.2 / Rocky Linux 9.7)
- **Frequency:** Every startup when `DATABASE_URL` is not set in `.env`
- **Trigger:** Backend container has no Postgres; empty `DATABASE_URL` → localhost:5432 default

## Investigation

| Time | Finding |
|------|---------|
| 2026-06-25 | `get_database_url` (`apps/backend/src/services/database.py` L37–60) falls back to `localhost:5432` when env unset |
| 2026-06-25 | `docker-compose.yml` passes `DATABASE_URL=${DATABASE_URL:-}` → empty string → falsy → localhost default |
| 2026-06-25 | Empty/whitespace `DATABASE_URL` is mishandled: `""` is falsy (silent localhost), `"   "` is truthy (returned as a broken URL) |
| 2026-06-25 | No `db`/postgres service exists in `docker-compose.yml`; project uses managed Supabase in prod |
| 2026-06-25 | `create_tables()` logs but does not raise (L259–262), so the traceback is non-fatal but alarming |

**Root cause:** Config/infra — the local-dev Docker Compose stack ships no database and passes an
empty `DATABASE_URL`, so the backend falls back to `localhost:5432` where nothing listens. The
empty-string env is also not normalized in `get_database_url`.

## Spec conformance

| Spec | Result |
|------|--------|
| `docs/feature-list.md` (F3 / infra) | In scope — local-dev Docker quick start must work out of the box |
| `docs/DEVELOPMENT.md` L100 (`DATABASE_URL` required) | Implementation drift — compose did not provide a DB; now bundles one |
| Constraint R3 | Bundled bare Postgres serves ORM tables only; auth + F5 work-history still need Supabase |
| REQ-016 | No conversion/validation behavior change |

## Repro test

| Field | Value |
|-------|------|
| Path | `tests/bugs/test_bug_2026_06_25_docker_db_connect.py` |
| Assertions | (1) blank/whitespace `DATABASE_URL` is treated as unset + actionable warning; (2) `docker-compose.yml` defines a Postgres `db` service with a non-empty backend `DATABASE_URL` default pointing at it and `depends_on` service_healthy |

## TDD iteration log

| # | Action | Result |
|---|--------|--------|
| 1 | Add repro test (env normalization + compose contract) | RED |
| 2 | Bundle Postgres `db` service + default `DATABASE_URL`; normalize blank env in `get_database_url` | GREEN |

## Fix

**Files:** `docker-compose.yml`, `apps/backend/src/services/database.py`, `.env.example`,
`README.md`, `docs/DEVELOPMENT.md`

1. Add a `db` (`postgres:16`) service with `pg_isready` healthcheck + named volume on `metar-network`.
2. Default backend `DATABASE_URL` to `postgresql+asyncpg://postgres:postgres@db:5432/postgres`
   (still `${DATABASE_URL:-...}` overridable); add `depends_on: db: condition: service_healthy`.
3. Normalize `DATABASE_URL` / `SUPABASE_DB_URL` in `get_database_url` — treat blank/whitespace as
   unset and emit an actionable warning naming the variable.
4. Docs: compose now ships a DB; Supabase still required for auth + F5 work-history (R3).

## Verification plan

- **Success:** `docker compose up --build` reaches DB and logs "Database tables initialized
  successfully" (no `Connect call failed` error); `/health` 200.
- **Checks:** Unit/repro tests + CI parity (local); optional live `docker compose` smoke.
- **Monitoring:** Reporter re-pulls `main` post-fix; reply on #671.

## Verification

### Layer 1 — Automated

- [x] Repro test red (7 failed) → green (8 passed)
- [x] `make test-bugs` — 37 passed, 1 deselected
- [x] Backend unit suite — 1154 passed @ 98.04% coverage (`database.py` 100%)
- [x] CI parity (local): ruff format-check, ruff lint-py, prettier, yamllint, actionlint, gitleaks, basedpyright (0 errors)
- [x] PR branch CI green — [run 28194159287](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/28194159287) `success` on `2ff9a42` (PR #692)

### Layer 2 — Reproduction

- [x] `docker compose up -d db` → healthy; bundled Postgres reachable via `db:5432`
  with default `postgres:postgres` creds; DDL round-trip (CREATE/INSERT/SELECT/DROP)
  succeeds from a container on `metar-network` — proves backend default
  `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres` resolves #671.
- [ ] Full backend image `docker compose up --build` end-to-end — not run; local `.env`
  carries a real Supabase `DATABASE_URL` that overrides the bundled default, so the
  bundled-DB path is verified via the db-only smoke above. Reporter to confirm on re-pull.

## Prevention & countermeasures

(pending Phase 5)

## Cursor rule

Created: `.cursor/rules/optional/docker-compose-db-url-defaults.mdc`

- Compose: no empty `${DATABASE_URL:-}` defaults; use in-network `@db:5432` default + `depends_on` health gate.
- Python: blank/whitespace connection env vars treated as unset with named warning (`_clean_env` pattern).
- Regression: `tests/bugs/test_bug_2026_06_25_docker_db_connect.py`

## Follow-ups

- Post-merge: confirm `main` CI green after merge (#692).
- Reporter validation on Rocky Linux 9 / Docker 29 after re-pull.
