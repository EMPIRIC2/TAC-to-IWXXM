# 01-requirements — S070 / EV-060 (delta)

**Status:** complete (intake locked `D-S070-e9`; user “recommended for all”)  
**Gate:** Spec→Build **closed** — no product code  
**Corpus:** [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F10]
[Corpus: product §F29] [Corpus: product §F31] [Corpus: api] [Corpus: journeys] [Corpus: tests]
[Corpus: decisions §EV-060]

## Startup

EV0–EV9 completed in 16-evolve; remaining batches (EV6–EV9) accepted as **recommended**.
01 UI preview offer: **remind at 11-verify-impl** (`D-S070-e2`).

## Standing doc deltas

| Doc | Delta |
|-----|--------|
| `docs/feature-list.md` | F7.t slice; EV-060 AC for #1001–#1006; F29/F31 notes |
| `docs/spec.md` | F7.t / AHL / profile / log_level / bulletin fields |
| `docs/user-journeys.md` | UJ-059..063; UJ-003/046 UAT |
| `docs/test-plan.md` | TC-EV060-* + H4–H5 rows |
| `docs/api-contract.md` | `product=iwxxm`; log_level logger verbosity |
| `docs/decisions/evolve-decisions.md` | §EV-060 |
| `docs/decisions/requirements-decisions.md` | EV-060 table |

No new CORPUS member. No `acceptance-criteria.md` standing file — AC live in feature-list + test-plan.

## Next

**02-verify-plan** (delta Gate A). Dual-mode Spec `verify-qa` / `uat` after Gate A or in parallel with 04.
