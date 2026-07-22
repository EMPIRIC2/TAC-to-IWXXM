---
session_id: S020-aerodrome-quality
type: feature
status: in_progress
branch: evolve/EV-015-aerodrome-quality
started_at: 2026-07-22
intent: "F15 sequel — TAF + SPECI quality bars (#735/#734); F20 + deepen F6/F12; EV-011 stack"
orchestrator: 16-evolve
evolve_cycle_id: EV-015
context_briefs:
  - docs/context/aerodrome-quality.md
standing_docs_touched: []
---

# Session S020 — aerodrome-quality

## Intent

Raise **TAF** and **SPECI** TAC lint, validation, and TAC→IWXXM conversion quality to the same bar F15 set for METAR/SPECI:

1. **[#735](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/735)** — TAF (`iwxxm:TAF`): FM/BECMG/TEMPO/PROB, NIL/CNL/AMD/COR, TX/TN, CAVOK/NSC/NSW; Annex-3 + IWXXM-US forecast extensions (F6.c).
2. **[#734](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/734)** — SPECI (`iwxxm:SPECI`): **full** product quality AC (parallel to #735), not residual-only — shared METAR/SPECI rules plus adjacency / mis-classification guards.

Same stack as EV-011: `tac-validate` / `tac2iwxxm` / `iwxxm-validate` / goldens / coverage matrix / ADR-028 registry (reuse, amend codes only).

## Prior session

| Item | Disposition |
|------|-------------|
| S019 / EV-014 | **Completed** — F16–F19 Done; PR #772 |
| S015 / EV-011 | **Completed** — F15 Done; PR #742; METAR/SPECI R1–R8 closed |

## Intake decisions (Phase 0 — Batch 1 locked 2026-07-22)

| ID | Decision |
|----|----------|
| E15-1 | Open `S020-taf-quality` → **amended** rename to `S020-aerodrome-quality` (`D-S020-EV015-s1m2-2`) |
| E15-2 | **Full** SPECI (#734) + TAF (#735) quality bars this cycle |
| E15-3 | New **F20** (TAF + SPECI quality bar) + deepen **F6.b / F6.c** + **F12**; reuse ADR-028 |
| E15-4 | Provisional Lean — **superseded** by E15-route-amend |
| E15-route-amend | **A — Lean+build** (`D-S020-EV015-route-1`) |
| E15-5 | Full #735/#734 AC — guidance + fixtures + goldens + matrix (TAF **and** SPECI) |
| E15-6 | Siblings OOS; no PyPI; no F16–F19; F7 Planned (smoke only) |
| E15-7 | Redeploy if API/FE changes; H1–H3 if API; H4–H5 `taf`/`speci` workbench smoke |
| E15-8 | Lock Phase 0 → write F20 + start **01-requirements** |
| E15-10 | Approve 01 deltas → 02-verify-plan |
| S1.M1 | Full HARD themes T1–T4/S1–S3/C1; 04 kill-switch (`D-S020-EV015-s1m1-1`) |
| S1.M2 | Rename session/branch to aerodrome-quality (`D-S020-EV015-s1m2-2`) |
| S9.M1 | Keep skip 05; lightweight consistency at 04 exit (`D-S020-EV015-s9m1-1`) |
| AskQuestion | Waived (written interview; UI unavailable) |

## Proposed Fn allocation

| Fn | Title | Role |
|----|-------|------|
| **F20** | TAF + SPECI quality bar (F15 sequel) | New — product quality metrics, journeys, tests; registry codes for TAF (+ SPECI deepen) |
| **F6** (deepen) | Convert/golden fidelity | F6.c TAF; F6.b SPECI (Annex-3 + IWXXM-US where applicable) |
| **F12** (deepen) | `tac-validate` rule packs + fixtures | Coverage-matrix TAF + SPECI rows; accept/negative |

## Scope (Phase 0 **approved** 2026-07-22)

### In

- #735 exceptional-rule table → accept + negative fixtures (or explicit deferrals)
- #734 exceptional-rule table → accept + negative fixtures; Auto-detect / lint never mis-classify SPECI↔METAR
- Encode audit vs WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections (no `runwayState`)
- Round-trip convert → `iwxxm-validate` XSD+Schematron on goldens
- Coverage-matrix TAF + SPECI row updates; gaps filed or closed
- API/UI smoke: `product=taf` / `product=speci` convert / lint-tac / decode + workbench (F7 stays Planned)

### Out

- Sibling product-quality tickets (#731, #733, #736–#741, etc.) unless shared registry/common-rule touch
- New dissemination / F16–F19 work; PyPI release bumps; COLLECT

## Routing plan

See [routing-plan.md](./routing-plan.md) — **approved** Lean+build (`D-S020-EV015-route-1`).

## Current stage

**01-requirements** (delta) — feature-list F20 written; document manifest pending approval.

## Links

- Issues: [#735](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/735), [#734](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/734)
- Predecessor: F15 / EV-011 — `docs/sessions/S015-metar-lint-quality/`
- Corpus: F6 / F12 / proposed F20 — `docs/feature-list.md`
- Domain: `docs/domain/rules/COVERAGE_MATRIX.md`, ADR-028
