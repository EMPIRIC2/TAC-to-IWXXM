# ADR-031: Public unauthenticated app + IndexedDB local history (F21 / F7.h)

> **Status**: **Partially superseded by ADR-033** (S038 / EV-031) — Auth deletion and
> “no server sessions” reversed; **public convert**, guest IndexedDB, F22 privacy, and abuse
> controls **retained**.  
> **Date**: 2026-07-28  
> **Deciders**: User (E17-12..25 / D-S023-04-batch3; plan approve D-S023-04-plan-approve-A)  
> **Stage**: 07-build (Accepted); drafted in 04-tech-plan; amend noted EV-031  
> **Related**: Supersedes **ADR-020** for operator persistence (pre-EV-031); ADR-002/M4 operator
> Auth restored under ADR-033; ADR-011/012 historical for server RLS/retention; ADR-018 (F8
> machine auth amended by ADR-033); ADR-021/029 (dissemination memory-only); feature-list
> F21/F22/F5/F7.h; #783; **ADR-033**  
> **Session**: S023-public-app-privacy / EV-017  
> **Decision ids**: E17-4..E17-25; D-S023-04-batch1-arch; D-S023-04-batch2-privacy-ops;
> D-S023-04-batch3; D-S023-04-plan-approve-A

## Context

EV-017 / #783 removes end-user Auth so convert → validate → download/send works without
login. Server-owned `tac_work_sessions` (ADR-020) and operator JWT gates contradict the
public-app model. Privacy Solution A + GPC require a preference center that discloses
local storage. Abuse controls are required once APIs are public.

## Decision

1. **Public operator API (F21)** — `/api/v1/*` (convert, validate, lint, decode, preview,
   dissemination) requires **no JWT**. Operator `/auth/*` and server work-session CRUD
   return **404**. Retire `DISABLE_AUTH` dual path.
2. **Local history (F7.h / F5 deepen)** — Persist sessions in **browser IndexedDB** via
   **`idb`**, reusing `workSessionPayload` / ConverterSnapshot shapes. My METARs =
   local `product IN (metar, speci)` filter. **One-time** migrate guest `sessionStorage`
   → IndexedDB on first F7.h load. Export/import JSON schema
   **`tac-work-sessions-export-v1`**.
3. **Prefs (F22)** — Privacy preferences in **`localStorage`**; work sessions stay in
   IndexedDB. Honor **`Sec-GPC: 1`** and `navigator.globalPrivacyControl` as opt-out of
   non-essential prefs. Solution A: notice + settings; no CMP/analytics.
4. **Abuse controls** — **`slowapi`** (in-memory; single Render instance baseline):
   **60 req/min/IP** on convert+lint+decode (+ related public convert paths);
   **10/min/IP** dissemination; **2 MB** max body (env-tunable). Keep ADR-029 allowlist.
5. **Cutover** — **Single deploy**: IndexedDB FE live and BE Auth/work-sessions gone in
   the same release train (IndexedDB implemented before Auth strip within the PR train —
   E17-10 / E17-18).
6. **`packages/auth`** — **Delete entirely** this cycle (E17-22=B). Inline any residual
   helpers into `apps/backend` / `apps/worker` if required; F8 continues on service-role
   env vars (ADR-018) without the auth package.
7. **Legacy server rows** — No public API to old `tac_work_sessions`; ~30-day archive then
   delete (E17-5). ADR-020 status → **Superseded by ADR-031**.
8. **ADR number** — This document is **ADR-031**.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Anonymous server sessions + optional accounts | User locked Auth model 1 (E17-8) |
| 2 | Dexie / native IDB only | User chose `idb` (E17-12) |
| 3 | Keep `packages/auth` for F8 | User chose full delete (E17-22=B); worker has no auth import today |
| 4 | Two-step Auth teardown | User chose single deploy (E17-18) |
| 5 | Amend ADR-020 in place | User chose supersede with ADR-031 (E17-23) |

## Consequences

- FE: remove login UX, JWT bootstrap, `workSessionApi` HTTP; add IndexedDB store + privacy UI.
- BE: remove auth routers / JWT middleware; add slowapi + body limits; 404 Auth/sessions.
- Workspace: drop `packages/auth` from uv/pnpm/Docker/CI coverage gates; update M4 to deprecated.
- Env: rewrite env-contract (no `E2E_USER_*` / `DISABLE_AUTH` / browser Auth keys).
- Tests: TC-004 IndexedDB; TC-F21-auth-gone; TC-F22-*; retire Auth E2E fixtures.
- Dissemination stays public + memory-only credentials (ADR-021/029).

## Rate-limit / body defaults (E17-19)

| Scope | Default | Env (canonical) |
|-------|---------|-----------------|
| Convert / lint / decode / validate / preview | 60/min/IP | `RATE_LIMIT_PUBLIC_PER_MIN` |
| Dissemination preflight/send | 10/min/IP | `RATE_LIMIT_DISSEMINATION_PER_MIN` |
| Max request body | 2 MiB | `MAX_REQUEST_BODY_BYTES` |

## Amendment — EV-052 / S061 (2026-08-09)

**Decision 4 (abuse controls)** is amended: when `REDIS_URL` (or approved Upstash env) is
set, **slowapi** uses a **shared Redis-compatible store** (Upstash free tier —
`D-S061-redis=1`) so multi-replica DOKS API pods share one counter. When unset (local
dev), keep **in-memory** limiter. Defaults in the table above are unchanged. No new
in-cluster Redis Deployment. See [Corpus: decisions §EV-052] and
`docs/sessions/S061-ci-polish-quality-pr-stats/reports/infra-free-tier.md`.
