# Evolve report — EV-059

> Cycle: EV-059 · Session: S069-ci-schemathesis-mutation  
> Closed: 2026-08-17 · `D-S069-close=1`  
> Preset: Lean · Spec→Build: open (Build done) · Promote: **held**

## Goal

Close epic #841 via Schemathesis OpenAPI property suite (#727) + broad Python/TS mutation testing (#874); fix findings; keep CI minutes low.

## Outcome

| Item | Result |
|------|--------|
| F34 | **Done** — contract + mutation quality gates on `stage` |
| M1 Schemathesis | PR [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) **MERGED** → `stage` @ `c08bc30f`; [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727) **CLOSED** |
| M2 Mutation | PR [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) **MERGED** → `stage` @ `8755ae87`; [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874) **CLOSED** |
| Epic | [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) **CLOSED** |
| Tip CI | [32054972352](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32054972352) **SUCCESS** (after sticky soft-fail `354354b6`) |
| Promote | **Held** (out of scope this cycle) |

## Routing (Lean)

`00 → 16 → 01 → 02` → Spec→Build open → `07 → 08` (skip 03–06, 09–13)

## Features / corpus

- **F34** — [Corpus: product §F34]
- Tests / CI — [Corpus: tests] [Corpus: tech-spec] [Corpus: api]
- Decisions — [Corpus: decisions §EV-059]

## Notable decisions

| ID | Summary |
|----|---------|
| D-S069-ci | Schemathesis path-filtered required; mutation nightly/manual only |
| D-S069-tool | pytest-gremlins + Stryker |
| D-S069-sticky-softfail | Soft-fail Coverage/Quality sticky PR comments on GitHub API 429/5xx |
| D-S069-m2-survivors | Waive 3 equivalent Stryker survivors on `parseCommaSeparatedOrigins` |
| D-S069-close | Close cycle on stage; promote held |

## Out of scope (honored)

Mutation required on every PR · Rust mutation · live staging/prod Schemathesis merge gate · product UI · weaken ≥95% coverage · promote `stage`→`main` · replace hand-written UJ/pytest

## Next

Promote `stage`→`main` only after separate user re-approve. Optional: `15-service-health` on staging tip if desired.
