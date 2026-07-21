# ADR-021: BYO credentials and admin product-surface removal

> **Status**: Accepted (amended 2026-07-21 — S019 / EV-014 destination paste)  
> **Date**: 2026-07-13  
> **Deciders**: User (S011 Phase 0 R6; config/env Batch 1 option B; EV-014 Q10)  
> **Stage**: 01-requirements  
> **Related**: ADR-010, ADR-002, ADR-029; feature-list F7/M4/F16–F19; api-contract; env-contract  
> **Session**: S011-f7-operator-ui / EV-008; amend S019-dissemination-upload / EV-014  
> **Decision id**: D-S011-01-cfg-B; amend D-S019-EV014-Q10

## Context

Corpus and UI assumed a shared hosted Supabase project plus an **admin dashboard**
(`/admin/*`, approvals, toggle-admin, cross-user session browse). Issue #697 and Phase 0 R6
require **operator-owned** (BYO) credentials and removal of that admin product surface.

## Decision

1. **BYO (app auth)**: Operators supply Supabase URL (config) + publishable/secret keys via
   deploy/env. **No** in-app paste of **Supabase Auth** keys. Optional deploy `DATABASE_URL`
   may remain for legacy primary upload defaults.
2. **Remove** product `/admin/*` routes and AdminDashboard; prefer HTTP 404.
3. **Deprecate and remove** `ADMIN_EMAIL` / `ADMIN_PASSWORD`; live/E2E login uses
   `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` for an ordinary user (not an admin role).
4. Keep local/CI `DISABLE_AUTH` / `api.disableAuth` (G1).
5. Signup vs invite remains **operator Supabase policy** (G2). No product data migration of
   former shared-project users (G3).
6. **Amendment (EV-014)**: In-app paste of **one-shot dissemination destination** credentials
   (DB URI / WIS2 / EDIS SMTP / AMHS params) is **allowed** for F16–F19. Credentials are
   backend memory-only, never saved as profiles, never stored on work sessions. Governed by
   ADR-029 (SSRF + required allowlist). This does **not** reintroduce paste of Supabase auth keys.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep admin dashboard for shared tenancy | Contradicts #697 / R6 |
| 2 | Keep `ADMIN_*` names for live tests | Confuses admin product role with test user |
| 3 | In-app paste of Supabase auth keys | Remains non-goal |
| 4 | No destination paste (deploy-only sinks) | Rejected for EV-014 / #729 self-hosted send |

## Consequences

- Auth shrinks (M4 delta); admin E2E retired (TC-F7-006).
- Docs and `.env.example` must rename harness credentials; 04/07 update scripts and Playwright.
- `create_admin_user.py` (if kept) must not imply dashboard admin UX.
- Dissemination drawer + ADR-029 env (`DISSEMINATION_EGRESS_ALLOWLIST`) required for F16–F19.
