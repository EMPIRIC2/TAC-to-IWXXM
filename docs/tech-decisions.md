# Technical Decision Log

> Extends [product-decisions.md](product-decisions.md) with 05-verify-tech audit verdicts.
> Last updated: 2026-06-15

## 04-tech-plan (pre-audit)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| TECH-001 | 2026-06-15 | Python runtime | Pin 3.12 everywhere | confirmed |
| TECH-002 | 2026-06-15 | Node runtime | Pin 22 for frontend/e2e | confirmed |
| TECH-003 | 2026-06-15 | Frontend deploy | Render Static Site (CDN) | confirmed |
| TECH-004 | 2026-06-15 | Observability | Remove Loki/Prometheus/Grafana | confirmed |
| TECH-005 | 2026-06-15 | Connectivity origins | onrender.com URLs; VITE_API_BASE_URL + METAR_CORS_ORIGINS | confirmed |
| TECH-006 | 2026-06-15 | Typechecker | basedpyright strict | confirmed |
| TECH-007 | 2026-06-15 | GIFTs lint | Migrate to ruff | confirmed |
| TECH-008 | 2026-06-15 | JS package manager | pnpm workspaces | confirmed |
| TECH-009 | 2026-06-15 | CI path filters | Defer to post-migration P2 | confirmed |
| TECH-010 | 2026-06-15 | Vendor sync schedule | Weekly Action for wmo-im only | confirmed |
| TECH-011 | 2026-06-15 | Coverage gate | 95% all packages/apps | confirmed |
| TECH-012 | 2026-06-15 | Production auth | DISABLE_AUTH=false in production | confirmed |

## 05-verify-tech (audit resolutions)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| TAUDIT-001 | 2026-06-15 | Phase 3 docker-compose gate | Move compose update to T6.6 (Phase 3); M8 retains Dockerfile only | confirmed |
| TAUDIT-002 | 2026-06-15 | F2–F4 regression | Add T5.8 product regression smoke post-move (no feature rewrites) | confirmed |
| TAUDIT-003 | 2026-06-15 | TC-002 coverage | Add T7.4 validation pass verification | confirmed |
| TAUDIT-004 | 2026-06-15 | Big-bang gate | test-plan includes H4/H5 alongside H0c | confirmed |
| TAUDIT-005 | 2026-06-15 | Coverage metrics | test-plan Metrics aligned to ADR-007 95% universal | confirmed |
| TAUDIT-006 | 2026-06-15 | packages/shared coverage | Add T1.10 for 95% coverage | confirmed |
| TAUDIT-007 | 2026-06-15 | staging-secrets-matrix | T9.6 verify/update (pre-written in 04-tech-plan) | confirmed |
| TAUDIT-008 | 2026-06-15 | Makefile targets | T1.6 includes test-unit and tests:e2e | confirmed |
| TAUDIT-009 | 2026-06-15 | Config env wiring | Explicit subtasks on T6.3 and T9.1 for Supabase/frontend env | confirmed |
| TAUDIT-010 | 2026-06-15 | connectivity-gates.md | Replace placeholders with VITE_API_BASE_URL / METAR_CORS_ORIGINS | confirmed |
| TAUDIT-011 | 2026-06-15 | H0i integration tier | Add T5.7 integration test suite | confirmed |
| TAUDIT-012 | 2026-06-15 | Milestone naming | Feature↔milestone mapping table in execution plan | confirmed |
| TAUDIT-013 | 2026-06-15 | TDD exceptions | Document migration-move exceptions (T2.3, T2.4, T5.3, T7.1) | confirmed |
| TAUDIT-014 | 2026-06-15 | TC-M004 source | Label as Phase 4 finalize / T11.1 | confirmed |
