# SIGMET examples: invisible OUTPUT_VALIDATION_WARNING

Session: EV-1159-sigmet-example-validate. Ticket: #1159. Scale: standard. Gate: open.

[Corpus: product §F7] [Corpus: product §F23] [Corpus: product §F25] [Corpus: api] [Corpus: journeys] [Corpus: tests]

UI reference: operator workbench Examples catalog. Non-deployed local preview deferred until Build opens (documenting from repo + issue text).

## Goal

Audit every shipped UI example for convert + IWXXM validate. Fix the SIGMET path so soft `OUTPUT_VALIDATION_WARNING` either does not fire or surfaces actionable issue details. Make the IWXXM validate control succeed or fail with visible diagnostics. Add regression coverage.

## Shipped example inventory (catalog)

Source: `apps/frontend/src/fixtures/examples/examplesCatalog.ts` on `stage` (19 rows).

| Product | Ids | Mode |
|---|---|---|
| METAR | `metar_a3_1`, `ahl_metar_wmo_a3_1`, `ahl_metar_multi`, `iwxxm_metar_nil_collect` | tac / ahl / collect |
| SPECI | `speci_a3_2` | tac |
| TAF | `taf_a5_1`, `taf_a5_2` | tac |
| SIGMET | `sigmet_a6_1a_ts`, `sigmet_a6_1b_cnl`, `sigmet_va_eggx`, `sigmet_a6_2_tc`, `sigmet_multi_location_va` | tac |
| AIRMET | `airmet_a6_1a_ts` | tac |
| VAA | `vaa_a7_2` | tac |
| TCA | `tca_a2_2` | tac |
| SWXA | `swxa_a7_3`, `swxa_a7_4`, `swxa_a7_5` | tac (wmoReference) |
| VONA | `vona_a7_1` | tac |

Pass/fail matrix for convert + validate is a Build deliverable. Documenting records the inventory and the suspected failure modes below.

## Symptom

Operator loads a SIGMET example, converts, and sees soft warning copy such as “Output converted, but IWXXM validation reported issues” / `OUTPUT_VALIDATION_WARNING` with a count (“… found - 3 issues”) while the Conversion/Validation log does not list the three underlying issues. Separately, Validate IWXXM on those examples fails or is confusing.

## Suspected root causes (to confirm in Build)

### A — Backend collapses details off the wire issues list (confirmed + fixed)

In `apps/backend/src/routers/conversion.py`, when post-convert orchestrator validation is not valid, convert previously added **one** `ConversionIssue` with `code=OUTPUT_VALIDATION_WARNING` and a count message. Individual findings lived only in statistics `validation_errors`. **Fix:** `emit_output_validation_soft_warning` flattens orchestrator (and package error) findings onto response `issues[]`.

### B — Package vs orchestrator validity mismatch (partial)

Offline package validate of `sigmet_a6_1a_ts` is `ok` with skip warnings. Soft warn came from orchestrator `is_valid=False`, not package XSD.

### C — Validate button mode vs convert output (mitigated)

Validate IWXXM expects XML. Switching to Validate IWXXM now prefills the editor from the latest converted XML when present.

### D — FE filter / hide (not primary)

`ErrorLogPanel` already renders code / message / hint. Vitest covers soft-warn + detail rows (TC-F7-044).

## Confirmed root cause (Build)

Post-convert soft validation included `AIRPORT_ICAO` and `TAC_SYNTAX` (METAR/SPECI) on every product. SIGMET example TAC (e.g. YUDD) produced `UNKNOWN_ICAO`, `MISSING_KEYWORD`, `MISSING_TIMESTAMP` — three invisible findings behind one soft warn. **Fix:** exclude those input layers from post-convert orch layers (they already run only for METAR/SPECI before convert).

## Example matrix (convert + validate_output, 2026-09-29)

All SIGMET catalog TAC examples: convert successful, **no** `OUTPUT_VALIDATION_WARNING`. Soft warn remains only where real IWXXM findings exist (e.g. some SWXA/VONA/TAF), and those responses now include flattened detail codes.

## Locked product decisions (intake)

- Prefer fixing **display + example quality** over weakening validation.
- No new SIGMET products. No dissemination. No example-picker redesign beyond showing issues.
- No vendor pin change unless required to clear false positives (separate call-out).
- Operator copy stays free of internal doc refs.
- Deepens F7.g / F23 / F25. No new feature id. F6 stays Implemented.

## Out of scope

- New SIGMET products or product-family expansion.
- Dissemination / F16–F19.
- Example picker UX redesign beyond issue visibility.
- Vendor schema pin changes unless required (call out).
- Promoting `stage` to `main`.
- Closing or merging PR #1269.

## Success / AC

1. Documented pass/fail matrix for every shipped UI example (convert + IWXXM validate).
2. SIGMET path: zero `OUTPUT_VALIDATION_WARNING`, **or** warnings listed with code / message / path (or equivalent).
3. Root cause documented (bad example vs validate engine vs FE / payload).
4. IWXXM validation on SIGMET examples succeeds or shows actionable errors.
5. Regression coverage (unit and/or e2e) for soft-warning visibility.

## Build intent (not started)

- Confirm (A)–(D) with HTTP convert of each SIGMET example and FE validate path.
- Likely fix: flatten orchestrator issues onto convert `issues[]` (reuse `add_aggregated_validation_issues` pattern) and/or attach child details under the soft warning; fix examples only if TAC/XML is wrong; improve validate handoff if mode confusion is real.
- Tests: backend unit for soft-warning payload shape; FE Vitest for ErrorLogPanel / FileConverter visibility; deepen TC-F7-008 / UJ-032 as needed.
- PR `--base stage`. No promote.
