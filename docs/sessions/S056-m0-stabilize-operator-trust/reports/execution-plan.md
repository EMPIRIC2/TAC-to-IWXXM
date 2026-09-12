# Execution plan — S056 / EV-047 (M0 husky + converter perf + operator docs)

> **Generated**: 2026-08-08  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-047-m0-stabilize-operator-trust`  
> **Issues**: [#833](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/833),
> [#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834),
> [#956](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/956),
> [#957](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/957)  
> **Build Plan Card**: `docs/sessions/S056-m0-stabilize-operator-trust/build-plan-card.md`

**Corpus**: [Corpus: product §M5] [Corpus: product §F6] [Corpus: product §F7]
[Corpus: tests] [Corpus: tech-spec] [Corpus: journeys] [Corpus: decisions]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Stabilize + narrative |
| **Active milestone** | M4: Verify closeout |
| **Active task** | T4.1 tip CI + 08/09/10/11 |
| **Tasks completed** | 18 / 20 (M1–M3 done; T1.5 admin-blocked; T4.1 next) |
| **Stage** | 07-build |
| **Last updated** | 2026-08-08 |
| **Ruleset** | `D-S056-ruleset-defer=2` — require `Converter perf (tac2iwxxm)` **after** job ships in M2 (not before) |
| **Coverage** | `D-S056-cov95=2` + `D-S056-cov95-scope=2` + `D-S056-m3-order=2` — M2.5 (incl. auth+worker) before M3; T1.5 still admin-blocked |

## Tech decisions (proposed → confirm `D-S056-04-plan`)

| ID | Choice |
|----|--------|
| D-S056-04-baseline | **Standing YAML** `tests/perf/baselines/converter_pr.yaml` — convert-only p50/p95 per product; recorded on **ubuntu-latest CI** (not laptop); refresh via `make perf-converter-baseline` (explicit, never silent on fail) |
| D-S056-04-ceiling | Hard-fail if observed p95 > `max(baseline_p95 × 1.20, baseline_p95 + floor_s)` with `floor_s=0.000200` (200µs) after cross-host noise on T1.3; single-run + flake retry doc |
| D-S056-04-products | METAR, SPECI, TAF + thin SIGMET (+ VA smoke if fixture cheap); pure-Python `tac2iwxxm.convert` |
| D-S056-04-husky | Shape A: husky `pre-commit` runs **only** ruff/prettier/eslint (via `pre-commit run <ids>` or lint-only config); husky `pre-push` runs `make test-unit-fast` |
| D-S056-04-unit-fast | New `make test-unit-fast` := `test-unit-workspace` + `test-unit-tac2iwxxm` (fast converter-relevant; not full `ci-prepush`) |
| D-S056-04-ci-job | New job `name: Converter perf (tac2iwxxm)` in `ci-cd.yml`; gate job if matrix needed; then **apply ruleset** including this context |
| D-S056-04-docs | `docs/guides/operator-one-pager.md` + `operator-handbook.md`; README Quick start; Help = static link/modal to one-pager (no new API) |
| D-S056-ruleset-defer | **2** — do **not** require Converter perf in live rulesets until M2 job exists on `stage` |
| D-S056-cov95 | **2** — package + per-file ≥95% this cycle (all Python packages in CI) |
| D-S056-cov95-scope | **2** — literally every Python package including auth + worker; package + per-file ≥95% |
| D-S056-m3-order | **2** — resolve coverage first, then M3 docs/Help |

### Laptop spike (informational only — **not** the PR baseline)

Local macOS 2026-08-08, N=50, warmup=5, pure-Python convert annex3/2025-2:

| Product | p50 (s) | p95 (s) |
|---------|---------|---------|
| METAR | 1.38e-5 | 1.57e-5 |
| SPECI | 1.53e-5 | 1.64e-5 |
| TAF | 8.37e-6 | 8.93e-6 |

CI ubuntu-latest numbers replace these in `converter_pr.yaml` (M1).

### Job graph (target)

```
pre-commit (local): ruff-format, ruff-check, prettier-check, eslint
pre-push (local): make test-unit-fast

ci-cd.yml:
  converter-perf  name: "Converter perf (tac2iwxxm)"
    → pytest tests/perf/test_converter_pr_gate.py (hard)
  …existing jobs unchanged…
```

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Hooks | husky + pre-commit (slimmed) | #833 / D-S056-husky-shape |
| Perf | pytest + committed YAML | #834 / D-S056-perf |
| CI | `.github/workflows/ci-cd.yml` | TC-EV047-007 |
| Docs | markdown under `docs/guides/` | #956/#957 |
| Help | frontend static link | UJ-054 |
| Connectivity H4–H5 | 10-e2e for Help; 12/13 waived | routing |

## Data Dependencies

None (fixtures in-repo).

## Implementation Phases

### Phase 1: Stabilize + operator narrative

**Entry**: `D-S056-04-plan` approved.  
**Exit**: AC1–AC9 green; tip CI green; ruleset includes Converter perf after M2; Help + docs ship.

#### M1: Converter perf baselines + hard harness — P0

**Goal**: CI-recorded baselines + hard-fail PR gate (compare against baseline).  
**Acceptance**: TC-EV047-005..008; artificial slowdown red.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Contract tests: baseline file path/schema; gate fails when p95 over ceiling; refresh target documented | Test | **completed** | TC-EV047-005..008; D-S056-04-baseline | — | — |
| T1.2 | Implement harness + `make perf-converter-baseline` (record p50/p95 on demand) | Code | **completed** | #834; D-S056-perf | T1.1 | — |
| T1.3 | **Establish baseline**: laptop seed → Linux Docker `ci_recorded` (floor 200µs); DEVELOPMENT refresh note | Config | **completed** | D-S056-04-baseline; D-S056-04-plan=2 | T1.2 | — |
| T1.4 | Wire `ci-cd.yml` job `name: Converter perf (tac2iwxxm)`; deploy.needs | Config | **completed** | TC-EV047-007; D-S056-04-ci-job | T1.3 | — |
| T1.5 | Apply rulesets **including** Converter perf (admin); verify `gh api …/rulesets` lists context | Ops | pending | D-S056-gateA=2; D-S056-ruleset-defer=2 | T1.4 | — |

#### M2: Slim husky — P0

**Goal**: Shape A local hooks; CI keeps offloaded gates.  
**Acceptance**: TC-EV047-001..004.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Contract tests for husky scripts + `test-unit-fast` + DEVELOPMENT table | Test | **completed** | TC-EV047-001..004 | — | — |
| T2.2 | Implement slim `.husky/pre-commit` / `pre-push`; add `make lint-fast` / `test-unit-fast` | Config | **completed** | D-S056-04-husky/unit-fast | T2.1 | — |
| T2.3 | Update `docs/ops/DEVELOPMENT.md` + test-plan hook tables (EV-047 supersede EV-036 day-to-day) | Docs | **completed** | AC3 | T2.2 | — |

#### M2.5: Coverage ≥95% (package + per-file) — P0

**Goal**: Enforce package `fail_under` ≥95 and CI per-file ≥95 for literally every Python package including `packages/auth` and `apps/worker`; stabilize tac2iwxxm flake (~94.96%).  
**Acceptance**: CI fails under package or per-file coverage below 95%; tac2iwxxm no longer flakes under 95; auth + worker meet the same gates.  
**Decisions**: `D-S056-cov95=2`, `D-S056-cov95-scope=2`, `D-S056-m3-order=2` (before M3 / T3.1).

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.5.1 | Raise package `fail_under` ≥95 where missing (all Python packages in CI) | Config | **completed** | D-S056-cov95=2 | T2.3 | — |
| T2.5.2 | Add CI per-file ≥95 coverage check | Config | **completed** | D-S056-cov95=2 | T2.5.1 | — |
| T2.5.3 | Fix tac2iwxxm flaky ~94.96% so package gate stays ≥95 | Test | **completed** | D-S056-cov95=2 | T2.5.1 | — |
| T2.5.4 | Lift `packages/auth` + `apps/worker` to package + per-file ≥95% | Test | **completed** | D-S056-cov95-scope=2 | T2.5.1 | — |

#### M3: Operator one-pager + handbook + Help — P0

**Goal**: User-facing docs + discovery.  
**Acceptance**: TC-EV047-009..011; UJ-054.  
**Blocked until**: M2.5 complete (`D-S056-m3-order=2`).

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Write `docs/guides/operator-one-pager.md` (one printed page; no internal cites) | Docs | **completed** | #956 AC7 | T2.5.1–T2.5.4 | — |
| T3.2 | Write `docs/guides/operator-handbook.md` (sections + ingest pointer; link from one-pager) | Docs | **completed** | #957 AC8 | T3.1 | — |
| T3.3 | README Quick start links; in-app Help entry → one-pager | Code | **completed** | AC9; UJ-054 | T3.1 | — |
| T3.4 | Vitest/Playwright for Help entry (TC-EV047-011) | Test | **completed** | TC-EV047-011; 10-e2e | T3.3 | — |

#### M4: Verify closeout — P1

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T4.1 | Tip CI green; 08/09/10/11 reports | Verify | **completed** | routing Standard; D-S056-ac-bundle=1 | M1–M2.5–M3 | — |

###### Parallelizable

After plan approve: M1 and M2 can proceed in parallel once T1.1/T2.1 land; **M2.5 before M3** (`D-S056-m3-order=2`); M3 after coverage gate.

## PR Plan

| Milestone | PR title | Target |
|-----------|----------|--------|
| M1–M3 | `[EV-047] M0: slim husky, converter perf gate, coverage 95%, operator docs` | `stage` |

## Phase Gate Check

- [x] AC1–AC9 met (`D-S056-ac-bundle=1`)  
- [x] Baselines committed from CI-class measurement  
- [ ] Ruleset requires `Converter perf (tac2iwxxm)` — **deferred** T1.5 / `D-S056-t15-admin` (script lists job; admin apply pending)  
- [x] Package + per-file coverage ≥95% in CI (`D-S056-cov95=2`)  
- [x] Tip CI green ([31286442836](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31286442836) @ `3ca4f438`)  

