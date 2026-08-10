# Technical Decision Log

> Extends [product-decisions.md](product-decisions.md) with 05-verify-tech audit verdicts.
> Last updated: 2026-08-08 (S057 / EV-048)

## S057 / EV-048 05-verify-tech (2026-08-08)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| D-S057-04-plan | 2026-08-08 | Plan | Approve M1–M3 / T1.1–T3.3 → 05 then 07 | confirmed |
| D-S057-04-guard-ext | 2026-08-08 | Guard | Also fail on `TC-*`, `E##-##`, `#NNN` in scanned surfaces | confirmed |
| S5.M1 | 2026-08-08 | Patterns | Duplicate BE pytest + FE Vitest lists (no shared pkg) | confirmed |
| S5.M2 | 2026-08-08 | `#NNN` | Allowlist path if domain false positive | confirmed |
| S5.M3 | 2026-08-08 | ADR in exceptions | OK if never HTTP `detail` (T2.3 spot-check) | confirmed |
| D-S057-gateB | 2026-08-08 | Gate B | PASS → 07-build M1 | confirmed |

Session report: `docs/sessions/S057-strip-internal-doc-refs/reports/05-verify-tech.md`.

## S054 / EV-045 05-verify-tech (2026-08-08)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| D-S054-04-plan | 2026-08-08 | Plan | Approve execution-plan + Build Plan Card → 05 | confirmed |
| S2.1 | 2026-08-08 | AC7 / TC-EV045-007 | Always-on default CI (not path-filter-only) | synced |
| S2.2 | 2026-08-08 | TC-EV045-005 | `make rust-check` includes both maturin smokes | synced |
| S3.1 | 2026-08-08 | T1.7 deps | Depends on T1.2–T1.6 | synced |
| S3.2 | 2026-08-08 | F13 AC5 | Docs merge-block; ops rulesets waived | synced |
| D-S054-gateB | 2026-08-08 | Gate B | PASS → 07-build (06 skipped) | confirmed |

Session report: `docs/sessions/S054-rust-ci-crates/reports/05-verify-tech.md`.

## S020 / EV-015 04-tech-plan (2026-07-22)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| E15-12 | 2026-07-22 | Milestones | TAF lint → TAF goldens → SPECI → C1 → smoke | confirmed |
| E15-13 | 2026-07-22 | Research | Full mining pass + session catalog | confirmed |
| E15-14 | 2026-07-22 | FE | Catalog panel TAF tag filters/copy | confirmed |
| E15-15 | 2026-07-22 | Deps | AskQuestion per new dep (prefer none) | confirmed |
| E15-16 | 2026-07-22 | CI | Existing pytest + ci.yml only | confirmed |
| E15-17 | 2026-07-22 | Mining | Full dig TAF+SPECI only | confirmed |
| E15-18 | 2026-07-22 | Deploy | API+FE; H1–H3 + H4–H5 required | confirmed |
| E15-19 | 2026-07-22 | Plan | Approve M0–M5 (28 tasks) | confirmed |
| S9.M1 | 2026-07-22 | 05 skip | 04-exit consistency substitutes for 05 | confirmed |
| D-S020-EV015-plan-1 | 2026-07-22 | Gate | Execution plan approved | confirmed |

Session plan: `docs/sessions/S020-aerodrome-quality/reports/execution-plan.md`.

## S019 / EV-014 05-verify-tech (2026-07-21)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| S1 | 2026-07-21 | Task count | **29** unique tasks (mislabeled 32) | confirmed |
| S2 | 2026-07-21 | Git strategy | Build off `main` post-#753; do not reopen e25c | confirmed |
| S3 | 2026-07-21 | Secrets matrix | Add `DISSEMINATION_EGRESS_ALLOWLIST` API row | confirmed |
| S4 | 2026-07-21 | ADR-030 | SQL Server = `aioodbc` (E14-06); drop TBD | confirmed |
| S5 | 2026-07-21 | ADR-029 L1 | Allowlist docs resolved at 04; consequence updated | confirmed |
| S6 | 2026-07-21 | api-contract | Field names finalize before 07 (04 done) | confirmed |
| S7 | 2026-07-21 | Rate limit | Cover in T2.3/T2.4 (ADR-029 §5) | confirmed |
| S8 | 2026-07-21 | F17 harness | Compose/CI not long-lived Render web (align FL) | confirmed |
| D-S019-EV014-Q35A-05 | 2026-07-21 | Gate | 05 PASS; Assumed cloud (AskQuestion waived) | confirmed |

Session report: `docs/sessions/S019-dissemination-upload/reports/05-verify-tech-audit.md`.

## S019 / EV-014 04-tech-plan Batch 1 (2026-07-21)

| ID | Date | Topic | Decision | Status |
|----|------|-------|----------|--------|
| E14-01 | 2026-07-21 | Package layout | `packages/dissemination` + thin backend routers | confirmed |
| E14-02 | 2026-07-21 | DB stack | SQLAlchemy 2 async + dialect drivers; writer-contract DDL | confirmed |
| E14-03 | 2026-07-21 | API | `/api/v1/dissemination/preflight` + `/send` | confirmed |
| E14-04 | 2026-07-21 | wis2box | Docker Compose / CI harness (not Render web service) | confirmed |
| E14-05 | 2026-07-21 | EDIS/F19 | `aiosmtplib` + shared sink adapter interface | confirmed |
| D-S019-EV014-Q32A-04-batch1 | 2026-07-21 | Gate | Lock Batch 1 mapping; ADR-030 Accepted | confirmed |
| E14-06 | 2026-07-21 | SQL Server | `aioodbc` + ODBC docs | confirmed |
| E14-07 | 2026-07-21 | HTTP encode | msgspec on dissemination routes | confirmed |
| E14-08 | 2026-07-21 | Allowlist env | env-contract + Render; empty fail-closed | confirmed |
| E14-09 | 2026-07-21 | Tests | Unit + Compose/Testcontainers + mocks; live BYOC close-only | confirmed |
| D-S019-EV014-T34-transports | 2026-07-21 | WIS2 | httpx + aiomqtt≥2.3,<3 transports for TC-F17-001 | confirmed |
| E14-10 | 2026-07-21 | FE / H4–H5 | Ship drawer this cycle; H4–H5 required | confirmed |
| D-S019-EV014-Q33A-04-batch2 | 2026-07-21 | Gate | Lock Batch 2 (all A) | confirmed |
| D-S019-EV014-Q34A-04-approve | 2026-07-21 | Plan | Approve execution-plan M1–M6 (**29** tasks; 05 fixed miscount from 32); 04 complete | confirmed |

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
