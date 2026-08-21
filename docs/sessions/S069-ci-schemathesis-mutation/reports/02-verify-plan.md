# 02-verify-plan — S069 / EV-059 (Gate A)

> **Status**: **completed** — Gate A **PASS** (`D-S069-gateA=1a`); Spec→Build **open** (`D-S069-spec-build=2a`)  
> **Date**: 2026-08-17  
> **Mode**: delta · **Fn**: F34  
> **Corpus**: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec] [Corpus: api]  
> [Corpus: decisions §EV-059]

## Startup

| ID | Choice |
|----|--------|
| D-S069-02-start | **1a–6a** — Gate A → Spec→Build AskQuestion; carry locked intake; no blockers |

## Documents audited (delta)

| Doc | Sections | Result |
|-----|----------|--------|
| feature-list.md | Summary F34 + §F34 | Consistent with intake |
| test-plan.md | Coverage note + EV-059 + TC-F34-001..007 | Matches AC/budgets/matrix |
| dependency-inventory.md | Workspace tooling + changelog | schemathesis / gremlins / Stryker |
| CORPUS.md | product F1–F34 | Updated |
| evolve-decisions.md | §EV-059 | AC + decisions align |
| user-journeys.md | — | **N/A** (no new UJ; `D-S069-01-uj`) |
| api-contract.md | — | No standing delta yet; OpenAPI fixes allowed in Build when Schemathesis proves export wrong |

## High-confidence statements (auto-approved — from locked interviews)

| # | Statement | Source |
|---|-----------|--------|
| H1 | F34 is Planned Platform feature for Schemathesis + mutation gates | E2 3b / 01 1a |
| H2 | Schemathesis is path-filtered **required**; max-examples ≤ 25; job ≤ 10 min | D-S069-ci / 01 3a / AC7 |
| H3 | Mutation is nightly/manual only (not every PR) via pytest-gremlins + Stryker | D-S069-ci / D-S069-tool |
| H4 | Python + TS mutation matrix spans listed packages/apps; excludes e2e + Rust | D-S069-e4 / 01 4a |
| H5 | No new UJ; TC-F34-001..007 are the verification ids | D-S069-01-uj/tc |
| H6 | Two PRs (#727 then #874); epic #841 closable when children Done | epic + AC6 |
| H7 | No H4–H5 / deploy this cycle | D-S069-e6 / routing |
| H8 | Breaking OpenAPI cleanup allowed when Schemathesis proves export wrong | D-S069-e5=2b |
| H9 | Deps listed as **dev** before pin in 07-build | inventory + D-S069-01-deps |

## Medium / low (reviewed — no blockers)

| # | Confidence | Note | Verdict |
|---|------------|------|---------|
| M1 | Medium | `api-contract.md` not updated in Spec — OK if Build fixes OpenAPI export in place and cites `[Corpus: api]` when shapes change | **Accept** — defer to Build |
| M2 | Medium | Full mutation matrix may still be expensive nightly — mitigated by chunking + timeouts (not PR-required) | **Accept** — cost posture locked |
| L1 | Low | Exact Stryker plugin set / gremlins CLI flags TBD in 07 | **Accept** — Spec names tools + licenses only |

## Consistency checklist

- [x] feature-list AC ↔ test-plan TC-F34-* ↔ evolve-decisions AC
- [x] CI posture identical across product/tests/decisions
- [x] Inventory licenses match bake-off (MIT / MIT / Apache-2.0)
- [x] No false H4–H5 requirement for CI-only Fn
- [x] Build band 07→08 still blocked until Spec→Build gate
- [x] No contradiction with epic “don’t bundle #727+#874”

## Gate A recommendation

**PASS** — Spec-development complete for Lean routing; ready for Spec→Build AskQuestion.

## Gate decisions (recorded)

| ID | Choice |
|----|--------|
| D-S069-gateA | **1a** — PASS — F34 / TC-F34 / CI posture consistent; Spec-development complete |
| D-S069-spec-build | **2a** — Open Build — proceed to **07→08**; Schemathesis (#727) first, mutation (#874) second |

## Next

**07-build** startup interview → M1 Schemathesis (#727) implementation.
