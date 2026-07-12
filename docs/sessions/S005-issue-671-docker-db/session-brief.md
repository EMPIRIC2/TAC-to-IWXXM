---
session_id: S005-issue-671-docker-db
type: hotfix
status: in_progress
branch: fix/S005-issue-671-docker-db
started_at: 2026-06-25
intent: "Fix #671 — Docker Compose backend cannot create DB tables (localhost:5432 connection refused)"
orchestrator: 14-hotfix
context_briefs:
  - docs/context/issue-671-docker-db.md
github_issue: https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671
supersedes_session: S004-issue-555-feedback
---

# Session S005 — Issue #671 Docker DB table creation failure

## Intent

Resolve [GitHub #671](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671): the
Docker Compose backend logs `Failed to create database tables: ... Connect call failed
('127.0.0.1', 5432)` because `DATABASE_URL` is unset and the engine defaults to `localhost:5432`,
where no Postgres listens inside the container.

## Scope

**In scope**

- Add a **bundled Postgres service** to `docker-compose.yml` (approved approach R2).
- Default the backend `DATABASE_URL` to the bundled DB (`db:5432`), kept overridable.
- `depends_on` DB health before backend; healthcheck + named volume.
- Address the empty-string `${DATABASE_URL:-}` footgun in `get_database_url`.
- README / `docs/ops/DEVELOPMENT.md` Docker note; reply on #671.
- Repro + regression test per bug-investigation skill.

**Out of scope**

- Migrating off Supabase; replicating Supabase auth/RLS/work-history into the bundled DB (R3).
- Render/production topology (Supabase-managed; compose is local-only).
- Frontend Docker build (#688, closed) and conversion/validation behavior (REQ-016).

## Key decisions (2026-06-25)

| Topic | Decision |
|-------|----------|
| Session | Close merged S004; open hotfix S005 (R1) |
| Fix approach | Bundle Postgres in compose, self-contained `docker compose up` (R2) |
| Constraint | Bundled bare PG serves ORM tables only; auth + F5 still need Supabase (R3) |
| Duplicate? | Not a dup of #688 (frontend build bug) (R4) |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- [issue-671-docker-db.md](../../context/issue-671-docker-db.md)
- [GitHub #671](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/671)
