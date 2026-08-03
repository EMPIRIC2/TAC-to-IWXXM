---
session_id: S036-eight-family-ahl-rules-823
type: feature
status: completed
branch: main
started_at: 2026-08-01
completed_at: 2026-08-02
intent: "Umbrella #823 — mine + close lint/conversion/IWXXM-validation gaps for eight TAC→IWXXM families (AHL/bulletin first, then product-by-product); shared AHL/filename rules; seek examples for all TAC input shapes. Exclude SIGWX/VONA/QVACI."
orchestrator: 16-evolve
evolve_cycle_id: EV-029
github_issues:
  - 823
related_issues:
  - 738
  - 820
  - 740
  - 806
context_briefs:
  - docs/context/eight-family-ahl-rules-823.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/decisions/evolve-decisions.md
  - docs/domain/mining/**
  - docs/domain/rules/RULE_SOURCE_URLS.md
  - docs/domain/rules/COVERAGE_MATRIX.md
  - docs/domain/TAC_VALIDATION.md
  - docs/domain/IWXXM_CONVERSION.md
  - docs/domain/IWXXM_VALIDATION.md
feature_ids: [F28, F6, F12, F2, F13, F15, F20, F23, F24, F26, F27]
feature_note: "D-S036-fn — F28 SWXA quality bar (new) + deepen F6/F6.bulletin/F12/F2/F13/F15/F20/F23/F24/F26/F27; absorb #738/#820/#740"
ask_question: unavailable — written interview waive (D-S036-open / D-S036-fn)
---

# Session S036 — eight-family-ahl-rules-823

## Intent

Close **rules + engine + fixture** gaps for the eight-family TAC→IWXXM converter scope under
[#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823), going **1-by-1** across:

| Order | Family | IWXXM root(s) |
|------:|--------|---------------|
| 0 | Bulletin / AHL / COM rules | `collect:MeteorologicalBulletin` + shared AHL |
| 1 | METAR | `iwxxm:METAR` |
| 2 | SPECI | `iwxxm:SPECI` |
| 3 | TAF | `iwxxm:TAF` |
| 4 | SIGMET | `SIGMET` / `VolcanicAshSIGMET` / `TropicalCycloneSIGMET` (+ CNL) |
| 5 | AIRMET | `iwxxm:AIRMET` |
| 6 | VAA | `iwxxm:VolcanicAshAdvisory` |
| 7 | TCA | `iwxxm:TropicalCycloneAdvisory` |
| 8 | SWXA | `iwxxm:SpaceWeatherAdvisory` |

**Roles covered each step:** TAC lint (`tac-validate`) · TAC→IWXXM conversion (`tac2iwxxm`) ·
IWXXM XSD/Schematron (`iwxxm-validate`) · example/fixture inventory.

**Report states:** Normal · Amendment · Correction · Cancellation · Missing/`NIL` (where permitted).

**TAC input shapes (not file extensions):** standalone report · AHL + one/more reports · multi-report same type.

## Prior session

| Item | Disposition |
|------|-------------|
| S035 / EV-028 | **Completed** — #781 packaging; PR #824/#825 |
| S031 / EV-024 | Domain mine baseline — refresh/extend, don't restart |
| #738 / #820 / #740 | Related open quality tickets — absorb or child-link |

## Scope (locked — D-S036-open = 1,1,1,1,1,1)

### In

1. **Phase A** — mine/promote durable rules (#823 Phase A): mining notes, `RULE_SOURCE_URLS`,
   `COVERAGE_MATRIX`, canonicals (`TAC_VALIDATION` / `IWXXM_CONVERSION` / `IWXXM_VALIDATION`),
   example inventory across TAC shapes + official IWXXM examples
2. **Phase B** — implement gaps **product-by-product** in the order above (engines + tests +
   child issues for residuals)
3. **Shared AHL model** + IWXXM filename / `bulletinIdentifier` rules for conversion +
   dissemination consumers (sink UI deferred)
4. Target stack: IWXXM **2025-2** + Annex 3 21st + PANS-MET Doc 10157 (as in #823)

### Out

- SIGWX / VONA / QVACI as TAC converter inputs
- Dissemination drawer / sink UI polish this cycle
- #806 WIS2 topic mining (AHL aviation encode stays here; WIS2 exchange lane separate)
- Hand-edits to `vendor/schemas/*`
- Treating GIFTs as normative (ADR-014 — gap baseline only)

## Routing

See [routing-plan.md](./routing-plan.md). **Standard** — approved via intake `D-S036-open` Q5=1.

## UI preview

**N/A** — no browser UI in this session (`D-S036-open` Q6=1).

## Current stage

**01-requirements** completed (`D-S036-E29-M` = 2,1 — API `swxa`) → **02-verify-plan**.

## Links

- [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) (umbrella)
- Related: [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) · [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) · [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740)
)
