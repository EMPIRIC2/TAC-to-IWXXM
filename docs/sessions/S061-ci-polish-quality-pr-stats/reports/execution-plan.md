# Execution plan — S061 / EV-052 (CI polish + #900)

> **Generated**: 2026-08-09  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-052-ci-polish-quality-pr-stats`  
> **Issues**: [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950),
> [#900](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/900),
> epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841)  
> **Build Plan Card**: `docs/sessions/S061-ci-polish-quality-pr-stats/build-plan-card.md`

**Corpus**: [Corpus: product §F29] [Corpus: product §F6] [Corpus: product §F21]
[Corpus: product §F30] [Corpus: product §M5] [Corpus: tests] [Corpus: tech-spec]
[Corpus: deploy] [Corpus: adr/ADR-007] [Corpus: adr/ADR-006] [Corpus: adr/ADR-031]
[Corpus: decisions §EV-052]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: CI polish + #900 |
| **Active milestone** | M5: Docs parity + tip CI (next) |
| **Active task** | T5.1 |
| **Tasks completed** | 17 / 22 |
| **Stage** | 07-build |
| **Last updated** | 2026-08-09 |
| **Build Plan Card** | `docs/sessions/S061-ci-polish-quality-pr-stats/build-plan-card.md` |
| **Plan approval** | `D-S061-04-plan=1` — approved as drafted |

## Tech decisions (locked `D-S061-04-plan=1`)

| ID | Choice |
|----|--------|
| D-S061-orval | **1 — `openapi-typescript`** (types only) + thin FE wrappers for convert/validate; **not** full Orval client gen |
| D-S061-codegen | Commit `apps/frontend/src/generated/openapi.d.ts` (or equiv.); CI `pnpm openapi:check` fails on drift |
| D-S061-openapi-src | **Committed OpenAPI snapshot** + `make openapi-refresh` from FastAPI `/openapi.json`; CI drift check (not live-fetch in PR CI) |
| D-S061-redis-env | **`REDIS_URL`** (Upstash `rediss://…`); unset → in-memory slowapi + warning log (dev only) |
| D-S061-sentry-env | API/worker: **`SENTRY_DSN`**; FE: **`sentryDsn` (or equiv.) in `/config.json`** with `VITE_SENTRY_DSN` local fallback (matches runtime-config pattern) |
| D-S061-sentry-sample | Traces/profiles **off or ≤0.05**; errors-only default under Developer 5k/mo |
| D-S061-quality-marker | Sticky HTML comment marker distinct from EV-036 coverage (e.g. `<!-- quality-pr-comment -->`) |
| D-S061-quality-job | New `ci-cd.yml` job `quality-pr-comment` (parallel to `coverage-pr-comment`); reuse github-script update-in-place pattern |
| D-S061-cov-fe | Vitest **lines/statements/functions ≥95**; branches per `D-S061-cov-branches` |
| D-S061-cov-branches | **3** — lines/stmts/funcs ≥95 now; branches child issue + explicit waiver (threshold 84) |
| D-S061-m-order | M1 coverage → M2 quality comment → M3 Sentry+Redis → M4 openapi-ts → M5 docs/CI closeout |
| D-S061-12-13 | Keep **skipped** unless multi-replica Redis needs live DOKS proof mid-build |

### Locked (prior)

| ID | Choice |
|----|--------|
| D-S061-redis | **1** — Upstash Redis free (no DOKS Redis Deployment) |
| D-S061-comment | Second sticky (≠ coverage) |
| D-S061-01-ac | AC1–AC12 |
| D-S061-gateA | **1** — PASS → 04 |
| D-S061-04-plan | **1** — approve as drafted (openapi-typescript) |
| D-S061-route | Standard; skip 03/06/10/12/13 |

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Language | Python 3.11+ / TS (Vite) | template + monorepo |
| Coverage | pytest `fail_under` / `--cov-fail-under` + Vitest thresholds | ADR-007 / #950 |
| Quality PR | Python formatter + github-script sticky | EV-036 pattern / F29 |
| Sentry | `sentry-sdk[fastapi]` + `@sentry/react` | #900 / ADR-006 amend |
| Rate limit store | slowapi + `redis` URL (Upstash) / `fakeredis` tests | #900 / ADR-031 amend |
| FE types | `openapi-typescript` (devDependency) | #900 / M5 |
| CI | `.github/workflows/ci-cd.yml` | TC-EV052-012 |
| Deploy secrets | Document only this cycle (12/13 waived) | routing |
| Connectivity H4–H5 | N/A (no UJ delta) | routing |

## Data Dependencies

None (in-repo fixtures / goldens / quality-matrix packs).

## Implementation Phases

### Phase 1: CI polish + #900 platform

**Entry**: `D-S061-04-plan=1` approved.  
**Exit**: AC1–AC12 green; tip PR CI green; docs/env/ADR accurate; PR → `stage` ready after 11.

#### M1: Coverage inventory + ≥95% enforce + fill — P0

**Goal**: Every coverage surface documented and gated at ≥95%; suite green with gates.  
**Acceptance**: AC1–AC3; TC-EV052-001..003.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Inventory test: enumerate CI coverage surfaces + assert doc/table matches fail_under/Vitest thresholds | Test | **completed** | TC-EV052-001; AC1 | — | — |
| T1.2 | Write inventory artifact (session report or docs table) + wire assert in T1.1 | Docs/Code | **completed** | AC1; #950 | T1.1 | — |
| T1.3 | Contract tests: soft/deferred gates absent; all listed surfaces ≥95 in config/workflow | Test | **completed** | TC-EV052-002; AC2 | T1.2 | — |
| T1.4 | Raise Vitest thresholds to ≥95; align pytest fail_under / CI `--cov-fail-under` | Config | **completed** | AC2; D-S061-cov-fe | T1.3 | — |
| T1.5 | Fill tests until suite green under gates; document intentional excludes only | Test/Code | **completed** | TC-EV052-003; AC3; D-S061-cov-branches=3; #968 | T1.4 | — |

#### M2: Quality / golden sticky PR comment — P0

**Goal**: Second sticky PR comment with match/soft-diff/fail/skip × product × profile.  
**Acceptance**: AC4–AC5; TC-EV052-004..005.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Unit tests for quality stats aggregator + markdown formatter (fixture JSON → tables) | Test | **completed** | TC-EV052-005; AC5 | — | — |
| T2.2 | Implement `scripts/ci/format_quality_pr_comment.py` (+ helpers); distinct sticky marker | Code | **completed** | AC4; D-S061-quality-marker | T2.1 | — |
| T2.3 | Wire `quality-pr-comment` job in `ci-cd.yml` (artifacts from quality-matrix / golden jobs) | Config | **completed** | TC-EV052-004; D-S061-quality-job | T2.2 | — |
| T2.4 | Idempotent sticky update test/doc (github-script pattern parity with coverage) | Test/Docs | **completed** | AC5 | T2.3 | — |

#### M3: Sentry + Upstash Redis slowapi — P0

**Goal**: Optional Sentry; shared Redis rate-limit store when `REDIS_URL` set.  
**Acceptance**: AC6–AC8, AC11; TC-EV052-006..008, TC-EV052-011.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Tests: Sentry no-op when DSN unset; init path when set (API/worker/FE smoke) | Test | **completed** | TC-EV052-006; AC6 | — | — |
| T3.2 | Wire `sentry-sdk` / `@sentry/react` behind env; low sample rates | Code | **completed** | AC6; D-S061-sentry-* | T3.1 | — |
| T3.3 | Tests: slowapi uses Redis storage when `REDIS_URL` set; fakeredis shared counters | Test | **completed** | TC-EV052-007..008; AC7–AC8 | — | — |
| T3.4 | `create_limiter()` → Redis storage URI when set; warn + memory fallback when unset (covers public + dissemination + mass-ingest via shared factory) | Code | **completed** | AC7; ADR-031; D-S061-redis-env | T3.3 | — |
| T3.5 | Env-contract / deploy / infra-free-tier secret stubs; no DOKS Redis Deployment | Docs | **completed** | AC11; TC-EV052-011 | T3.2, T3.4 | — |

#### M4: OpenAPI → typed FE client — P1

**Goal**: Generated types for high-churn convert/validate paths; CI drift check.  
**Acceptance**: AC9; TC-EV052-009.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T4.1 | Contract: generated types exist; `openapi:check` fails on drift; convert/validate import generated types | Test | **completed** | TC-EV052-009; AC9 | — | — |
| T4.2 | Add `openapi-typescript` + `make`/`pnpm` generate + check scripts; commit artifact | Config/Code | **completed** | D-S061-orval=1; D-S061-codegen | T4.1 | — |
| T4.3 | Wire FE convert/validate (high-churn) to generated types / thin wrappers | Code | **completed** | AC9; M5 | T4.2 | — |

#### M5: Docs parity + tip CI — P0

**Goal**: Standing docs accurate; PR CI green with new jobs/tests.  
**Acceptance**: AC10, AC12; TC-EV052-010, TC-EV052-012.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T5.1 | Back-add env names, dependency pins, ADR notes, feature-list/test-plan parity | Docs | pending | AC10; TC-EV052-010 | M1–M4 | — |
| T5.2 | Tip CI green on evolve branch (coverage gates + quality comment + new units) | Config | pending | AC12; TC-EV052-012 | T1.5, T2.4, T3.5, T4.3, T5.1 | — |

## Git Strategy

- Branch: `evolve/EV-052-ci-polish-quality-pr-stats` → PR to **`stage`**
- One task ≈ one atomic commit (`[T1.1] …`)
- Minor PR after Phase 1 complete (post 08/09/11); no stage→main this cycle

## Task Tracking (master)

| Task | Milestone | Status | Depends |
|------|-----------|--------|---------|
| T1.1–T1.5 | M1 | **completed** | chain |
| T2.1–T2.4 | M2 | **completed** | T2 internal; // M1 |
| T3.1–T3.5 | M3 | **completed** | T3 internal; // M1 |
| T4.1–T4.3 | M4 | **completed** | after M1 preferred |
| T5.1–T5.2 | M5 | pending | M1–M4 |

Parallelism: After T1.2 inventory lands, M2/M3/M4 may proceed in parallel; M5 last.

## Phase Gate Log

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| A→B (02) | **PASS** | 2026-08-09 | `D-S061-gateA=1` |
| B→C (05) | pending | — | after this plan approved + 05 |
| C→D (08) | pending | — | |
| Deploy | waived | — | 12/13 skipped |

## Handoff checklist (04)

- [x] AC / decisions mapped to tasks
- [x] Env params named (`REDIS_URL`, `SENTRY_DSN`, `VITE_SENTRY_DSN`)
- [x] TC-EV052 ↔ tasks
- [x] Build Plan Card for M1
- [x] User approves `D-S061-04-plan` (blocking) — **1**
- [x] Connectivity CORS tasks N/A (no browser origin change; 12/13 waived)
)
