# Technical Decision Log

> Extends [product-decisions.md](product-decisions.md) with 05-verify-tech audit verdicts.
> Last updated: 2026-07-21 (S019 / EV-014 04 Batch 1)

## S019 / EV-014 04-tech-plan Batch 1 (2026-07-21)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| E14-01 | 2026-07-21 | Package layout | `packages/dissemination` + thin backend routers | confirmed |
| E14-02 | 2026-07-21 | DB stack | SQLAlchemy 2 async + dialect drivers; writer-contract DDL | confirmed |
| E14-03 | 2026-07-21 | API | `/api/v1/dissemination/preflight` + `/send` | confirmed |
| E14-04 | 2026-07-21 | wis2box | Docker Compose / CI harness (not Render web service) | confirmed |
| E14-05 | 2026-07-21 | EDIS/F19 | `aiosmtplib` + shared sink adapter interface | confirmed |
| D-S019-EV014-Q32A-04-batch1 | 2026-07-21 | Gate | Lock Batch 1 mapping; ADR-030 Accepted | confirmed |

## S015 / EV-011 05-verify-tech (2026-07-19)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| TAUDIT-S015-01 | 2026-07-19 | Task count | 35 tasks (was miscounted 31; +T2.2a) | confirmed |
| TAUDIT-S015-02 | 2026-07-19 | HARD R1–R8 | Product docs: no R-theme deferral | confirmed |
| TAUDIT-S015-03 | 2026-07-19 | Guard timing | T6.0 warn; T2.2a error after migrate | confirmed |
| TAUDIT-S015-04 | 2026-07-19 | ADR/FE/HTTP | ADR-028 R1–R8+GET; msgspec catalog; H0c on T5.10 | confirmed |

Session report: `docs/sessions/S015-metar-lint-quality/reports/05-verify-tech-audit.md`.

## S014 / EV-010 05-verify-tech (2026-07-18)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| TAUDIT-S014-01 | 2026-07-18 | F11 codegen wording | Align feature-list to ADR-027 xsdata (44A) | confirmed |
| TAUDIT-S014-02 | 2026-07-18 | PyPI workflow docs | deploy + config-spec: one workflow + matrix (45A) | confirmed |
| TAUDIT-S014-03 | 2026-07-18 | CORS connectivity | Add T5.6 H0c re-verify after msgspec HTTP (46B) | confirmed |
| TAUDIT-S014-04 | 2026-07-18 | T3.7/T3.8 TDD | Add T3.7a + T3.8a preceding tests (47A) | confirmed |

Session report: `docs/sessions/S014-package-publish-validation/reports/05-verify-tech-audit.md`.

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

## S008 05-verify-tech (2026-07-12)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| TAUDIT-S008-01 | 2026-07-12 | F8 corpus | Align standing docs to ADR-018 (C01=1) | confirmed |
| TAUDIT-S008-02 | 2026-07-12 | F6.e + H4–H6 | Add M8 T8.1–T8.4 (C02/C03=2) | confirmed |
| TAUDIT-S008-03 | 2026-07-12 | Template rules | Update to `static+api+worker` + new packages (C04=1) | confirmed |
| TAUDIT-S008-04 | 2026-07-12 | PyO3 | Required at cutover in standing docs (C05=1) | confirmed |
| TAUDIT-S008-05 | 2026-07-12 | iwxxm-us pin | NWS HTTP 3.0 + URL/hash (C07=1) | confirmed |
| TAUDIT-S008-06 | 2026-07-12 | TC-F6-010–012 | T5.6 + T8.4 UJ-008 (C09a=1) | confirmed |
| TAUDIT-S008-07 | 2026-07-12 | Cutover E2E | T4.6 requires UJ-001/Playwright (C09c=1) | confirmed |
| TAUDIT-S008-08 | 2026-07-12 | F6.b order | US METAR/SPECI in M4 T4.10–11 (M01=2) | confirmed |
| TAUDIT-S008-09 | 2026-07-12 | Phase 1 gate | Include T1.6 (M02=1) | confirmed |

See session report: `docs/sessions/S008-general-tac-iwxxm-converter/reports/05-verify-tech.md`.
| TECH-ADR-023 | 2026-07-15 | Convert multipart wiring | UI sends bulletin_id/issuing_center/stop_on_error/validate_*; Log Level is client console filter only | confirmed |
