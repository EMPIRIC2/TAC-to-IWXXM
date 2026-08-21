# Evolve Plan Card

> Cycle: EV-059 | Session: S069-ci-schemathesis-mutation | Updated: 2026-08-17  
> Status: **completed** (`D-S069-close=1`; promote held)

## Goal

Close epic #841: Schemathesis OpenAPI property suite (#727) + broad Python/TS mutation testing (#874); fix findings; keep CI minutes low.

## Features

- F34 — Contract + mutation quality gates — [Corpus: product §F34]
- Supporting: [Corpus: tests] [Corpus: tech-spec] [Corpus: api]

## In / out of scope

- In: Schemathesis ASGI suite + auth; path-filtered required CI (tight budget); pytest-gremlins + Stryker across Python packages and TS; nightly/manual mutation matrix; inventory + test-plan; OpenAPI cleanup when export wrong; bugfixes/waivers for findings; two PRs → `stage`
- Out: mutation required on every PR; Rust mutation; live staging/prod Schemathesis as merge gate; product UI features; weaken coverage≥95%; stage→main promote; replace hand-written UJ/pytest

## Phase split

- Active phase: **closed** (Build complete)
- Spec→Build gate: **open** (`D-S069-gateA=1a`, `D-S069-spec-build=2a`)
- Preset: **Lean** (`D-S069-route`)

## Spec-development band (00–06)

- Stages (ordered): `00 → 16 → 01 → 02` — **complete**
- Dual-mode Spec skills: none
- Skip: `03`, `04`, `05`, `06`
- Gate A: **PASS** — [02-verify-plan](reports/02-verify-plan.md)

## Build band (07–13)

- Stages (ordered): `07 → 08` — **complete**
- Dual-mode Build skills: none
- Deploy intent: **none** (promote held)
- Skip: `09`, `10`, `11`, `12`, `13`
- PRs: [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) (M1) · [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) (M2) → `stage` @ `8755ae87`

## Next child stage

**None** — cycle closed. Promote only on separate re-approve.

## Locked intake

| ID | Decision |
|----|----------|
| D-S069-ci | Path-filtered Schemathesis required; mutation nightly/manual |
| D-S069-tool | pytest-gremlins + Stryker |
| D-S069-fn | F34 |
| D-S069-route | Lean Spec 01→02; Build 07→08 |
| D-S069-gateA | **1a** — PASS |
| D-S069-spec-build | **2a** — Open Build |
| D-S069-sticky-softfail | Soft-fail sticky PR comments on GitHub API 429/5xx |
| D-S069-close | **1** — Close on stage; promote held |

## Risks / open decisions

- None open — cycle complete; promote deferred
