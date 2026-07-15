# ADR-021: BYO credentials and admin product-surface removal

> **Status**: Accepted  
> **Date**: 2026-07-13  
> **Deciders**: User (S011 Phase 0 R6; config/env Batch 1 option B)  
> **Stage**: 01-requirements  
> **Related**: ADR-010, ADR-002; feature-list F7/M4; api-contract; env-contract  
> **Session**: S011-f7-operator-ui / EV-008  
> **Decision id**: D-S011-01-cfg-B

## Context

Corpus and UI assumed a shared hosted Supabase project plus an **admin dashboard**
(`/admin/*`, approvals, toggle-admin, cross-user session browse). Issue #697 and Phase 0 R6
require **operator-owned** (BYO) credentials and removal of that admin product surface.

## Decision

1. **BYO**: Operators supply Supabase URL (config) + publishable/secret keys + `DATABASE_URL`
   via deploy/env. No in-app paste-keys UI.
2. **Remove** product `/admin/*` routes and AdminDashboard; prefer HTTP 404.
3. **Deprecate and remove** `ADMIN_EMAIL` / `ADMIN_PASSWORD`; live/E2E login uses
   `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` for an ordinary user (not an admin role).
4. Keep local/CI `DISABLE_AUTH` / `api.disableAuth` (G1).
5. Signup vs invite remains **operator Supabase policy** (G2). No product data migration of
   former shared-project users (G3).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep admin dashboard for shared tenancy | Contradicts #697 / R6 |
| 2 | Keep `ADMIN_*` names for live tests | Confuses admin product role with test user |
| 3 | In-app paste-keys UI | Explicit non-goal |

## Consequences

- Auth shrinks (M4 delta); admin E2E retired (TC-F7-006).
- Docs and `.env.example` must rename harness credentials; 04/07 update scripts and Playwright.
- `create_admin_user.py` (if kept) must not imply dashboard admin UX.
