# ADR-030: Dissemination package + sink architecture (F16–F19)

> **Status**: Accepted (S019 / EV-014; 04-tech-plan Batch 1 — Q32=A)  
> **Date**: 2026-07-21  
> **Deciders**: User (D-S019-EV014-Q32A-04-batch1)  
> **Stage**: 04-tech-plan  
> **Related**: ADR-021 (destination paste); ADR-029 (SSRF / allowlist); feature-list F16–F19; #729 / #2 / #6  
> **Session**: S019-dissemination-upload / EV-014

## Context

EV-014 adds operator dissemination sinks (multi-DB upload, WIS2, EDIS, AMHS/SWIM/AFS) with
one-shot BYOC credentials, preflight, and backend-only egress. Logic must not live only as
ad-hoc FastAPI handlers, and multi-engine DDL/writer contracts need a single home.

## Decision

1. **New package** `packages/dissemination/` — sinks, writer-contract DDL, SSRF/allowlist
   helpers, protocol adapters. **No** FastAPI or Supabase imports. MIT; workspace member.
2. **`apps/backend`** — thin routers only: auth, request DTO assembly, call package, encode
   responses. Hold destination secrets in memory for the request / short-lived handle.
3. **DB stack** — SQLAlchemy 2 **async** + dialect drivers:
   Postgres (`asyncpg` / existing stack), MySQL/MariaDB (`aiomysql`), SQL Server (async
   dialect TBD in Batch 2/deps), SQLite (`aiosqlite`). Versioned **writer-contract** DDL per
   engine; create-if-missing when preflight requests DDL (Q20=A).
4. **HTTP API** — unified:
   - `POST /api/v1/dissemination/preflight`
   - `POST /api/v1/dissemination/send`  
   Sink-typed JSON body; optional short-lived opaque handle after green preflight (memory-only).
5. **WIS2 test harness** — project **Docker Compose / CI** wis2box (not a long-lived Render
   web service). Live WIS2 remains user BYOC (Q12/Q17).
6. **EDIS** — `aiosmtplib` for SMTP submit to RTH Washington (BYOC settings from drawer).
7. **F19** — AMHS / SWIM / AFS behind the same sink adapter interface; staging/test path
   required this cycle; live F19 demo optional (S-EV014-M2).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Backend-only modules (no package) | Harder reuse/test; muddies apps/backend |
| 2 | Raw drivers without SQLAlchemy | Four engines × DDL/preflight duplication |
| 3 | Per-sink HTTP routes | Drawer needs one contract; more FE/OpenAPI churn |
| 4 | Long-lived Render wis2box service | Cost/ops; Q17 is test harness only |
| 5 | Heavier mail framework | Unnecessary for BYOC SMTP submit |

## Consequences

- Update `[Corpus: system-spec]` Component Overview, plan-adherence, template-conformance.
- Back-add planned deps to `docs/dependency-inventory.md` (aiomysql, aiosqlite, aiosmtplib,
  SQL Server async driver — pin in Batch 2/3).
- API sketch lands in `[Corpus: api]` as Planned; wire shapes finalized before 07-build.
- Execution plan milestones: M1 package scaffold + SSRF; M2 F16 DB; M3 F17; M4 F18; M5 F19;
  M6 FE drawer + H4–H5 (exact tasks after remaining 04 batches).
