# Requirements Decisions Log

> Stage: 01-requirements | Last updated: 2026-06-14

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| REQ-001 | Monorepo direction | Single git; reduce submodule complexity; preserve upstream pull for iwxxm | confirmed |
| REQ-002 | iwxxm-* upstream | Vendored snapshots from wmo-im; no git submodules for schemas | confirmed |
| REQ-003 | GIFTs placement | `packages/gifts` — full source; manual merge from mgoberfield when chosen | confirmed |
| REQ-004 | Auth shape | `packages/auth` library merged into backend; single deployable API | confirmed |
| REQ-005 | Workspace tooling | Makefile + uv workspace + pnpm workspaces | confirmed |
| REQ-006 | Migration approach | Big-bang — one PR removes all submodules | confirmed |
| REQ-007 | Target layout | `apps/{backend,frontend,e2e}` + `packages/{auth,gifts,shared}` + `vendor/schemas/*` | confirmed |
| REQ-008 | Legacy repos | Archive after stable deploy; monorepo sole active dev target | confirmed |
| REQ-009 | Vendor sync trigger | Scheduled GitHub Action opens PR on wmo-im new tags | confirmed |
| REQ-010 | Deploy topology | Two Render services — API (backend+auth) + static frontend | confirmed |
| REQ-011 | Big-bang scope | Structure + auth merge + docs + test reorganization | confirmed |
| REQ-012 | Shared package | `packages/shared` — types + cross-app utils | confirmed |
| REQ-013 | E2E location | `apps/e2e/` dedicated workspace | confirmed |
| REQ-015 | Vendor pinning | `vendor/manifest.json` — repo + tag/SHA per bundle | confirmed |
| REQ-016 | Non-goals | No product feature rewrites during migration | confirmed |
| REQ-014 | GIFTs sync | Manual merge from mgoberfield when chosen — no scheduled Action (audit 02-verify-plan) | confirmed |
| REQ-017 | Auth route prefix | `/auth/*` at API root after merge | confirmed |
| REQ-018 | Golden regression | TC-M003 normalized canonical XML diff | confirmed |
| REQ-019 | Legacy repo archive | After stable production deploy, not at merge | confirmed |
| REQ-020 | JS workspace | pnpm workspaces (frontend + packages/shared) | confirmed |

## Open Questions (for 04-tech-plan)

1. ~~Exact auth route prefix after merge~~ — resolved: `/auth/*` (REQ-017)
2. ~~pnpm vs npm~~ — resolved: pnpm (REQ-020)
3. ~~Golden file strategy for TC-M003~~ — resolved: normalized XML (REQ-018)
