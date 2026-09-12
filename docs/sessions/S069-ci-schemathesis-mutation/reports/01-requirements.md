# 01-requirements — S069 / EV-059

> **Status**: completed (standing deltas written)  
> **Date**: 2026-08-17  
> **Mode**: delta · **Fn**: F34  
> **Corpus**: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec] [Corpus: api]  
> [Corpus: decisions §EV-059]

## Goal

Lock F34 acceptance and standing-doc deltas for Schemathesis (#727) + mutation testing (#874)
under epic #841, with CI cost ceilings, so **02-verify-plan** can run Gate A.

## Decisions (01)

| ID | Choice |
|----|--------|
| Startup | **1a–6a** — write F34 + test-plan + inventory; carry locked intake; hand off 02 |
| D-S069-01-title | **1a** — F34 Contract + mutation quality gates |
| D-S069-01-ac | **2b** — AC1–AC7 (include budget ceilings) |
| D-S069-01-budget | **3a** — max-examples ≤ 25; Schemathesis job ≤ 10 min |
| D-S069-01-matrix | **4a** — full Python + TS matrix (nightly); exclude e2e + Rust |
| D-S069-01-uj | **1a** — no new UJ |
| D-S069-01-tc | **2a** — TC-F34-001..007 |
| D-S069-01-deps | **3a** — schemathesis, pytest-gremlins, @stryker-mutator/core |

## Artifacts updated

| Doc | Delta |
|-----|-------|
| [feature-list.md](../../../feature-list.md) | Summary row + §F34 Planned |
| [test-plan.md](../../../test-plan.md) | EV-059 section + TC-F34-001..007; coverage note |
| [dependency-inventory.md](../../../dependency-inventory.md) | schemathesis / pytest-gremlins / Stryker (dev); changelog |
| [CORPUS.md](../../../CORPUS.md) | product scope F1–F34 |
| [evolve-decisions.md](../../../decisions/evolve-decisions.md) | §EV-059 AC table |

## Out of scope (unchanged)

Mutation on every PR; Rust mutation; live staging/prod Schemathesis merge gate; product UI;
weaken ≥95%; promote; replace hand-written UJ/pytest.

## Next

**02-verify-plan** (Gate A) → Spec→Build AskQuestion (gate remains closed until then).
