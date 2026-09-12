# Execution plan — S054 / EV-045 (Rust crate CI)

> **Generated**: 2026-08-08  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-045-rust-ci`  
> **Issue**: [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)  
> **Build Plan Card**: `docs/sessions/S054-rust-ci-crates/build-plan-card.md`

**Corpus**: [Corpus: product §F13] [Corpus: product §F14] [Corpus: tech-spec]
[Corpus: tests] [Corpus: adr/ADR-017] [Corpus: decisions]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Rust CI gates |
| **Active milestone** | M1: Makefile + CI workflow |
| **Active task** | — (M1 complete) |
| **Tasks completed** | 7 / 7 |
| **Stage** | 08-verify-build (D-S054-t17-ci=1) |
| **Last updated** | 2026-08-08 |
| **Build Plan Card** | `docs/sessions/S054-rust-ci-crates/build-plan-card.md` |

## Tech decisions (D-S054-04 — locked 2026-08-08)

| ID | Choice |
|----|--------|
| D-S054-04-jobs | **2** — cargo checks via **matrix** over crates; required context kept as exact `Rust crates (fmt/clippy/test)` via a thin **gate job** that `needs` the matrix (GH appends matrix values to static job names) |
| D-S054-04-maturin | **2** — extend `tac2iwxxm-native` into a **two-package matrix**; job `name: ${{ matrix.check_name }}` with locked strings `tac2iwxxm PyO3 (maturin)` / `iwxxm-validate PyO3 (maturin)` |
| D-S054-04-trigger | **1** — run with default `ci-cd.yml` PR/push (same as today’s native job; not path-filter-only) |
| D-S054-04-local | **2** — `deploy.needs` includes cargo gate + both maturin matrix legs; `make rust-check` = fmt+clippy+`cargo test` **both** crates **and** both `test-*-native` maturin smokes |
| D-S054-ac6-waive | **2** — AC6 ops (live rulesets) deferred; docs + `apply_gh_branch_rulesets.sh` already updated |

### Job graph (target)

```
rust-crates (matrix: tac2iwxxm | iwxxm-validate)
  └─ fmt --check → clippy -D warnings → cargo test
       └─ rust-crates-gate  name: "Rust crates (fmt/clippy/test)"

native-pyo3 (matrix; renames today’s tac2iwxxm-native)
  ├─ name: tac2iwxxm PyO3 (maturin)
  └─ name: iwxxm-validate PyO3 (maturin)

deploy.needs: [test, test-alembic, rust-crates-gate, native-pyo3]
  (or equivalent ids; both maturin matrix legs must pass)
```

Toolchain: `dtolnay/rust-toolchain@stable` + `rustfmt`,`clippy`; cache `Swatinem/rust-cache@v2` (or equivalent).

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Language | Rust (stable) + Python 3.12 / uv | ADR-017; existing CI |
| Formatter | `cargo fmt --check` | AC1 / TC-EV045-001 |
| Linter | `cargo clippy -- -D warnings` | AC2 / D-S054-01-ac |
| Tests | `cargo test` + maturin pytest smokes | AC3–4 |
| CI | `.github/workflows/ci-cd.yml` | D-S054-01-ac |
| Local | `make rust-check` | AC5 / D-S054-04-local |
| Deploy impact | Gate DOKS deploy on new jobs | D-S054-04-local |
| Connectivity H4–H5 | **N/A** — no browser/API surface | routing skip 10/12/13 |

## Data Dependencies

None.

## Implementation Phases

### Phase 1: Rust CI gates

**Objective**: Required cargo + maturin CI for both crates; Makefile parity.  
**Entry gate**: This plan approved (D-S054-04-plan).  
**Exit gate**: Tip CI green on evolve branch; TC-EV045-001..005/007 green; AC6 docs/script met (ops waived).

#### M1: Makefile + CI workflow — P0

**Goal**: Local `make rust-check` + `ci-cd.yml` jobs with locked check names.  
**Acceptance**: TC-EV045-001..005, TC-EV045-007; deploy blocked on red Rust/native jobs.

##### Tasks (TDD order)

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Add contract tests for EV-045: `make rust-check` in Makefile; locked job `name:` strings + gate/matrix shape in `ci-cd.yml`; `deploy.needs` includes rust gate + native matrix | Test | completed | test-plan TC-EV045-001..007; feature-list F13/F14 deepen | — | — |
| T1.2 | Implement `make rust-check` (and helpers if needed): both crates fmt/clippy/`cargo test` + `test-tac2iwxxm-native` + `test-iwxxm-validate-native` | Config | completed | tech-spec §Rust native crates; AC5 | T1.1 | — |
| T1.3 | Add `rust-crates` matrix job (fmt/clippy/test) + `rust-crates-gate` with `name: Rust crates (fmt/clippy/test)`; rust-cache + stable toolchain | Config | completed | AC1–3, AC7; D-S054-04-jobs | T1.1 | — |
| T1.4 | Refactor `tac2iwxxm-native` → package matrix with `check_name` for both PyO3 smokes (`IWXXM_VALIDATE_REQUIRE_RUST` / existing tac2iwxxm tests) | Config | completed | AC4; D-S054-04-maturin | T1.1 | — |
| T1.5 | Wire `deploy.needs` to rust gate + native matrix; keep default CI triggers (no path-filter-only) | Config | completed | D-S054-04-trigger/local; ADR-034 deploy | T1.3, T1.4 | — |
| T1.6 | Back-add tech-spec / feature AC notes with final job ids + matrix/gate rationale; confirm ruleset script lists locked names | Docs | completed | tech-spec; test-plan; apply_gh_branch_rulesets.sh | T1.5 | — |
| T1.7 | Tip CI green on `evolve/EV-045-rust-ci` (watch `ci-cd.yml`); fix clippy/fmt debt if jobs fail | Code | completed | TC-EV045-*; build-execution | T1.2–T1.6 | — |

**PR**: [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) → **`stage`** (ADR-034; supersedes #952).  
**T1.7 closed** (`D-S054-t17-ci=1`): accept run [31273500621](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31273500621) @ `f270618c` as tip CI for EV-045 Rust/maturin/test jobs (tip `09ce2bef` docs-only after that; Staging gate fail was base=`main` only).

###### Parallelizable

After T1.1 green (red→green on contracts): T1.2 ∥ T1.3 ∥ T1.4, then T1.5 → T1.6 → T1.7.

#### Phase 1 Gate Check

- [x] All M1 tasks `completed`
- [x] Contract tests green
- [x] Tip CI includes Rust gate + both maturin checks green (`D-S054-t17-ci=1` / run 31273500621)
- [x] `make rust-check` documented and works where Rust/maturin available
- [x] AC6 docs/script present; ops waive recorded (D-S054-ac6-waive=2)

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-045-rust-ci` |
| Commits | One task per commit: `[T1.n] …` |
| PR | Evolve PR to `main` after 11 (or earlier if user asks); title `[EV-045] Rust crate CI (#725)` |
| Rulesets | Script ready; **admin apply deferred** |

### PR checklist (draft)

- [ ] TC-EV045 contract tests pass
- [ ] CI job names match test-plan table exactly (gate + two maturin)
- [ ] `deploy.needs` updated
- [ ] No browser/deploy smoke required this cycle

## Task Tracking

| ID | Status | Feature | evolve_cycle_id |
|----|--------|---------|-----------------|
| T1.1 | completed | F13, F14 | EV-045 |
| T1.2 | completed | F13, F14 | EV-045 |
| T1.3 | completed | F13, F14 | EV-045 |
| T1.4 | completed | F13, F14 | EV-045 |
| T1.5 | completed | F13, F14 | EV-045 |
| T1.6 | completed | F13, F14 | EV-045 |
| T1.7 | completed | F13, F14 | EV-045 |

## Phase Gate Log

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| A→B | PASS | 2026-08-08 | D-S054-gateA=2; AC6 ops waived |
| B→C | PASS | 2026-08-08 | D-S054-gateB=1 |
| C→D | PASS | 2026-08-08 | 08 PASS; 09 pass_with_advisories; 11 APPROVED D-S054-11=1 |

## Out of scope (confirm)

- New `rust-ci.yml` workflow
- Path-filter-only Rust jobs
- Live GH ruleset apply (waived)
- Browser E2E / staging-prod deploy smoke
- Multi-arch wheel CI beyond `pypi-publish.yml`
