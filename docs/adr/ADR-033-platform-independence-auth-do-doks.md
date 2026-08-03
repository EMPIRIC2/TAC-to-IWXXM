# ADR-033: Platform independence — Auth-only Supabase, DO Postgres, DOKS (F30 / F31)

> **Status**: **Proposed** (01-requirements; accept at 04-tech-plan / Gate B)  
> **Date**: 2026-08-03  
> **Deciders**: User (E31-*; `D-S038-*` Phase 0 locks)  
> **Stage**: 01-requirements (draft)  
> **Related**: Partially supersedes **ADR-031** (Auth deletion + server sessions gone);
> amends **ADR-006** (Render-only topology), **ADR-018** (F8 store credentials),
> **ADR-010** (keys still Auth-scoped); restores **ADR-002** / **M4** Auth-in-API pattern;
> guest IndexedDB + F22 privacy + public convert + abuse controls from ADR-031 **retained**;
> feature-list F30/F31; #842 / #830 amend / #712  
> **Session**: S038-platform-independence-842 / EV-031  
> **Decision ids**: E31-1..E31-uj; `D-S038-tp`

## Context

EV-017 / ADR-031 removed operator Auth and server work sessions so the app could be fully
public with IndexedDB history. Epic #842 / #830 / #712 require reducing platform lock-in:
Supabase must not own product data; compute must move Render → DOKS; operators still need
**optional** login for **long-term** work storage. Convert must stay public.

## Decision

1. **Supabase = Auth only** — JWT issue/verify for optional operator login. No product
   PostgREST / hosted Postgres app tables on the default path. Amend #830 acceptance
   accordingly (Auth-kept; data-plane stripped).
2. **DigitalOcean Postgres = product DB** — Single `DATABASE_URL` for logged-in
   `tac_work_sessions` and F8 store/quarantine. Alembic (or backend migration path) targets
   `DATABASE_URL` — not Supabase CLI as product SoT.
3. **Hybrid sessions (F31)** — Guests: IndexedDB + **persistent** loss-of-progress notice +
   F22 privacy gates. Logged-in: JWT → `/api/v1/work-sessions*` on DO Postgres. On login:
   **auto-upload** all eligible local drafts (no merge prompt).
4. **Public convert retained (F21 Amended)** — Convert/lint/validate/preview/disseminate
   require **no** JWT. Abuse controls (slowapi / body limits) from ADR-031 remain.
5. **Restore `packages/auth` + `/auth/*`** — Mount on `apps/backend` (M4). FE may bootstrap
   Supabase Auth publishable config for login UX only.
6. **DOKS production cutover (F30 / #712)** — API + worker + static move to DigitalOcean
   Kubernetes; Render decommissioned after soak (`D-S038-doks-depth`=3). Live H0–H5
   (including **H4–H5**) required against DOKS URLs this cycle.
7. **One-time legacy migrate** — Export/import historical Supabase product rows into DO
   Postgres this cycle; no long-lived dual-write.
8. **ADR number** — This document is **ADR-033**.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Strip Auth entirely (#830 original) | User chose Auth-kept for long-term storage (`D-S038-830-amend`) |
| 2 | Keep product DB on Supabase | Contradicts #842 / #830 data-plane strip |
| 3 | Dual Render+DOKS production long-term | User chose full cutover + retire after soak |
| 4 | Prompted merge of guest drafts | User chose auto-upload (`D-S038-guest-merge`=2) |
| 5 | Waive H4–H5 behind FE flag | User required live H4–H5 (`D-S038-tp` Q2=1) |

## Consequences

- FE: restore optional login; keep IndexedDB guest path; persistent guest notice; privacy
  disclosures for Auth cookies; auto-upload on login.
- BE: restore `packages/auth` + work-sessions routers (pydantic); session store via SQL on
  `DATABASE_URL`; convert stays public.
- Worker: writers use `DATABASE_URL` (amend ADR-018 service-role PostgREST assumption).
- Deploy: IaC + cutover runbook for DOKS; update `LIVE_*` / CORS / env-contract; Render
  decommission checklist.
- Tests: TC-F30-*; TC-F31-*; TC-EV031-*; amend TC-F21-auth-gone (public convert, not Auth-404).
- Docs: config / env-contract / api-contract / deploy / CORPUS deltas this cycle.

## Supersession map

| Prior ADR | Effect under ADR-033 |
|-----------|----------------------|
| ADR-031 | **Partially superseded** — Auth deletion + “no server sessions” reversed; public convert, IndexedDB guest, F22, rate limits **kept** |
| ADR-020 | Remains historical shape reference for `tac_work_sessions`; storage host = DO Postgres |
| ADR-006 | **Amended** — production topology target becomes DOKS (Render transitional until soak) |
| ADR-018 | **Amended** — F8 persistence via `DATABASE_URL` / DO Postgres (not Supabase DB) |
