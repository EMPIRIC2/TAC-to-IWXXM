---
session_id: S069-ci-schemathesis-mutation
type: feature
status: completed
branch: evolve/EV-059-ci-schemathesis-mutation
orchestrator: 16-evolve
evolve_cycle_id: EV-059
github_issues: [841, 727, 874]
prior_session: S068-quality-metrics-diff-layout
opened: 2026-08-17
closed: 2026-08-17
close_decision: D-S069-close=1
---

# Session brief — S069-ci-schemathesis-mutation

> **Cycle**: EV-059 · **Type**: feature · **Opened**: 2026-08-17 · **Closed**: 2026-08-17 (`D-S069-close=1`)  
> **Branch**: `evolve/EV-059-ci-schemathesis-mutation` @ `stage@c458669e` → tip `8755ae87`  
> **Orchestrator**: **16-evolve** · **Preset**: Lean · **Promote**: held  
> **Issues**: [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) · [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727) · [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874) — all **CLOSED**  
> **PRs**: [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) · [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) → `stage`  
> **Corpus**: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec] [Corpus: api] [Corpus: decisions §EV-059]

## Goal

Close epic **#841** by delivering **Schemathesis** (#727) and **mutation testing** (#874: Stryker + pytest-gremlins), keep CI runtime/cost minimal, and fix clear bugs/survivors found by those suites (or waive with rationale).

## Intent

Finish the remaining #841 children as one evolve cycle with **two PRs** (do not bundle stacks). New feature **F34** frames contract + mutation quality gates.

| Decision | Choice |
|----------|--------|
| D-S069-e0 | **1a / 2a+cost / 3a / 4b→CIa / 5a+research / 6a** — close #841; minimal CI cost; two PRs; required Schemathesis path-filtered; mutation nightly/manual; research Python tool |
| D-S069-ci | **CIa** — Schemathesis path-filtered **required** (tight Hypothesis budget + timeout); mutation **nightly / workflow_dispatch only** |
| D-S069-e1 | **1a / 2a / 3a / 4a** — feature session; #841+#727+#874; normal urgency; **pytest-gremlins** + **Stryker** |
| D-S069-e2 | **1a / 2a / 3b / 4a** — developers+CI; coverage≠contract/assertion strength; **new Fn F34**; fence existing required CI + husky budget |
| D-S069-e3 | **1a / 2a / 3a / 4a** — minimal docs delta; CORPUS under product/tests/tech-spec/api; no dual Spec skills; Lean Spec `01→02` |
| D-S069-e4 | **1b / 2a / 3a / 4a** — **broad** Python+TS mutation coverage (all packages/services via nightly matrix); no deploy; Lean Build QA; CI logs + bug reports only |
| D-S069-e5 | **1a / 2b / 3a / 4a** — OOS fence as epic; **breaking OpenAPI cleanup allowed** when Schemathesis proves export wrong; no PII; CI+local only |
| D-S069-e6 | **1a / 2a / 3a / 4a** — no product UI; UI preview N/A; no CORS; H0i/contract-style only (skip H4–H5) |
| D-S069-route | **1a / 2a / 3a / 4a** — Spec `01→02`; Build `07→08` blocked; orchestrator 16-evolve; skip 03–06, 09–13 |
| D-S069-e8 | **1** — open session; Spec-development only; Spec→Build gate closed |

## Out of scope

- Required mutation score on every PR
- Rust crate mutation (first pass)
- Live staging/prod Schemathesis as merge gate
- Product UI / journey changes
- Weakening coverage ≥95% or other required `main` checks
- Promote `stage` → `main`
- Replacing hand-written UJ/pytest with Schemathesis alone

## Features

- **F34** — Contract (Schemathesis) + mutation (Stryker / pytest-gremlins) quality gates  
  ([Corpus: product §F34] — to be written in 01)

## CI posture (locked)

| Suite | When | Gate |
|-------|------|------|
| Schemathesis | PRs touching `apps/backend/**` / OpenAPI-related paths | **Required**, tight max-examples + job timeout |
| Mutation (Python + TS) | Nightly / `workflow_dispatch`; scoped matrix across packages | **Not** required on every PR; hard timeouts |

## Acceptance (seed — refine in 01)

| ID | Criterion |
|----|-----------|
| AC1 | Schemathesis suite loads OpenAPI from backend ASGI; auth strategy exercises protected routes |
| AC2 | `make test-schemathesis` + path-filtered required CI job with documented knobs / budget |
| AC3 | pytest-gremlins + Stryker configs + `make` targets; nightly/manual matrix covers Python packages + TS surfaces |
| AC4 | Deps listed in `docs/dependency-inventory.md`; notes in `docs/test-plan.md` |
| AC5 | Findings: product/schema bugs fixed with bug-investigation where applicable; survivors/waivers documented |
| AC6 | Two PRs (#727 then #874); epic #841 closable when both Done |

## Implementation notes

- Prefer pytest + Schemathesis against FastAPI `app`; reuse backend test fixtures
- OpenAPI fixes preferred over broad skips; multipart/convert routes high value
- Mutation: chunked nightly matrix + timeouts to control cost; kill survivors or waive
- PR target: `stage`; promote held

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- #841 / #727 / #874 → **In progress** (session open)

## Routing plan

See [routing-plan.md](./routing-plan.md).
