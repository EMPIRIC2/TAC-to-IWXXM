# Context — validation policy layers

**Session:** EV-validation-policy-layers  
**Issue:** [#1216](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1216)  
**Date:** 2026-09-20  
**Corpus:** [Corpus: product §F15] [Corpus: product §F2] [Corpus: adr/ADR-028] [Corpus: adr/ADR-038] [Corpus: adr/ADR-045] [Corpus: decisions]

## Problem

TAC lint codes live in a solid registry (ADR-028), but detectors are imperative Python and mined YAML catalogs are projections—not executable policy. IWXXM validation is Schematron/XSD with a mined assert inventory under `tac2iwxxm`. Decode packs (ADR-045) already show how declarative packs scale; lint/validate need the same *layering* without duplicating Schematron or merging packages.

## Locked solution shape

Four layers: **Registry → Detector → Policy → Runtime** (D-VPL lock).

- One conversion-profile UX; policies are modules it references.
- MatchPort optional injection from decode; strict on annex3 METAR.
- IWXXM: vendor `.sch` SoT + enablement policy + national bundles.
- R1–R8 METAR/SPECI acceptance via sequenced theme flips.

## Touched components

| Component | Change |
|---|---|
| `packages/tac-validate` | Detector packs, TAC quality policy, MatchPort, runtime |
| `packages/iwxxm-validate` | Assert inventory home, IWXXM output policy |
| `packages/tac2iwxxm` | Profile resolver refs to policy ids; generated catalogs |
| `apps/backend` | Thin: resolve profile only (no new HTTP fields) |
| `apps/frontend` | No lint-profile picker this cycle |

## Must not break

- `/lint-tac` / `/validate` Issue wire shape
- ADR-028 code stability
- Pack-engine boundary (decode does not emit lint)
- Vendor schemas read-only

## Memory

Session-open: no strong matches. Historical retrieve: low-signal cross-project item only — **waive** (keep-local). Prior in-repo: ADR-045 pack cycles, ADR-028 registry, ADR-038 `validation.tac` / `outputValidation`.

## Docs to delta (draft-docs)

feature-list F15/F2 · spec components · ADR-046 new · amend ADR-028/038 · test-plan TCs · api-contract review (no wire add) · journeys note · config-spec overlay env if needed · decisions/evolve-decisions
