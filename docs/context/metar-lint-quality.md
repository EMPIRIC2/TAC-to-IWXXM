---
slug: metar-lint-quality
topic: "METAR lint issue registry + #732 quality (lint/validate/convert)"
status: active
created: 2026-07-19
session_id: S015-metar-lint-quality
evolve_cycle_id: EV-011
linked_features: [F15, F6, F12]
---

# Context — metar-lint-quality

Scoped brief for S015 / EV-011. Standing specs remain canonical; this file seeds research and gap notes.

## Problem

`tac-validate` already emits structured `Issue` (`severity`, `code`, `message`, spans), but codes are scattered in rule functions — not a single maintainable registry. METAR convert/validate goldens are thin relative to the F6.a/F6.b “reference product” bar ([#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732)).

## Current baseline (repo)

| Layer | State |
|-------|--------|
| Issue model | `packages/tac-validate` — `error` / `warning` / `info` |
| METAR accept fixture | `packages/tac-validate/tests/fixtures/accept/metar_basic.tac` |
| Convert matrix | `packages/tac2iwxxm/tests/fixtures/product_matrix/metar_basic.tac` |
| Coverage | `docs/domain/rules/COVERAGE_MATRIX.md` — METAR reference row; gaps: US REMARKS, nils under-use |
| Known gaps (#732) | COR/NIL/remarks; IWXXM-US (AO2, SLP, PK WND); AHL+SPECI adjacency; #667 remarks |

## External research sources

| Source | Use for |
|--------|---------|
| [MetarCentral — How to Read METAR](https://metarcentral.com/learn/how-to-read-metar) | Token checklist (wind, vis SM/m, weather, clouds, T/Td, A/Q, RMK AO2/SLP/PK WND) → lint rule candidates + decode/summary copy |
| [AviationRef METAR decoder](https://www.aviationref.com/metar-decoder) | Interactive decode UX patterns; sample TAC set (intl + US); TEMPO/NOSIG adjacency |
| [moryakovdv/iwxxmConverter](https://github.com/moryakovdv/iwxxmConverter) | TAC→IWXXM IR steps; METAR/SPECI converter tests; Schematron validation samples; note: RMK still TODO upstream |
| [FlightPlanDatabase FMS spec](https://flightplandatabase.com/dev/specification) | **Out of scope as METAR authority** (X-Plane FMS format) — do not encode as TAC rules |

### Research themes to expand (R1–R6 draft)

| ID | Theme | Candidate work |
|----|-------|----------------|
| R1 | Field-order / missing-group lint | ERROR for missing station/time; WARNING for unusual order |
| R2 | Visibility dual dialect | SM vs meters; fractional SM; 9999 |
| R3 | Weather phenomena grammar | Intensity + descriptor + precip; VC*; invalid combos → WARNING/ERROR |
| R4 | Cloud / CAVOK / VV / CB/TCU | Ceiling semantics; CB/TCU INFO/WARNING for decode |
| R5 | Remarks pack | AO1/AO2, SLP, P####, T########, PK WND — lint + IWXXM-US emit |
| R6 | Convert golden + SCH round-trip | Expand product_matrix; CI fail on XSD/Schematron regression |

## Success signals

- Registry is the single source of issue codes/severities; rules import from it
- New METAR rules add registry rows + fixtures without renaming existing public codes casually
- Golden METAR → convert → `iwxxm-validate` passes pinned versions in CI
- Negative fixtures never silent-succeed on known violations
- Research notes cited in domain/coverage updates (no copyrighted Annex 3 prose in wheels)

## Resolution log (local)

| ID | Resolution |
|----|------------|
| R0 | FMS URL excluded as METAR source (E11-3 scope note) |
| R-depth | E11-6: implement catalog **and** encode R1–R6 **and** goldens; opportunistically improve any other METAR lint/convert/validate gap found in research |
| R-route | E11-5: full routing 00–13 incl. 03/06 + Render |
