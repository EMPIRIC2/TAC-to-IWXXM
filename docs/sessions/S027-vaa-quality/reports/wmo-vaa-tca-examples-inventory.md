# WMO VAA / TCA IWXXM examples inventory — S027 / EV-021

**Date**: 2026-07-29  
**Decision**: E21-3 — dig vendor + translation-package examples for golden + exceptional fixtures.  
**Authority**: 2025-2 pinned line; golden equality via `canonicalize_xml` under default convert (E21-2).

## Primary goldens (2025-2 — happy path)

| Product | Root | TAC | XML | Notes |
|---------|------|-----|-----|-------|
| **VAA** | `iwxxm:VolcanicAshAdvisory` | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/va-advisory-A7-2.tac` | `…/va-advisory-A7-2.xml` | Karymsky / TOKYO; **FCST +18 HR = `NO VA EXP`** → XML `status="NO_VOLCANIC_ASH_EXPECTED"` |
| **TCA** | `iwxxm:TropicalCycloneAdvisory` | `…/tc-advisory-A2-2.tac` | `…/tc-advisory-A2-2.xml` | GLORIA / YUFO; **RMK: NIL** → remarks `nilReason=inapplicable` |

Same filenames also under `vendor/schemas/iwxxm/IWXXM/examples/` (unversioned snapshot alias).

## Translation-failed (not happy-path golden — E21 scope)

| Product | TAC | XML |
|---------|-----|-----|
| VAA | `va-advisory-translation-failed.tac` | `va-advisory-translation-failed.xml` |
| TCA | `tc-advisory-translation-failed.tac` | `tc-advisory-translation-failed.xml` |

Use for C1 / `translationFailedTAC` coverage — **do not** treat as catalog happy-path.

## Prior line (2023-1) — reference only

| Product | Pair | Note |
|---------|------|------|
| VAA | `va-advisory-A2-1.{tac,xml}` | Different example id than 2025-2 `A7-2` — **not** the 2025-2 golden |
| TCA | `tc-advisory-A2-2.{tac,xml}` | Same stem as 2025-2; verify namespace/version before reuse |

Do **not** assert 2023-1 XML equality under 2025-2 convert defaults.

## iwxxm-translation Amd79-80-2023 (exceptional-rule mine)

Path: `vendor/schemas/iwxxm-translation/Amd79-80-2023/`

### VAA (`volcanic-ash-advisory/`)

| Case | Themes (from `VolcanicAshAdvisoryTestCases.txt`) |
|------|--------------------------------------------------|
| `FVAG01SABM-1600` | VA NOT IDENTIFABLE; NOT GIVEN colour; NOT AVBL forecasts; **NO FURTHER ADVISORIES** |
| `FVAU03ADRM-0424` | Colour code; many VA clouds; **NO VA EXP**; 'no later than' |
| `FVFE01RJTD-1720` | **NO VA EXP**; NIL colour + remarks; next-advisory punctuality |
| `FVXX23KNES-1922` | Multiple ash clouds; no colour; 'will be issued by' |

### TCA (`tropical-cyclone-advisory/`)

| Case | Themes (from `TropicalCycloneCases.txt`) |
|------|------------------------------------------|
| `FKNT23KNHC-1458` | Weakening/dissipating TC; no CB group |
| `FKNT23KNHC-1500` | Abbreviated TEST message |
| `FKNT23KNHC-1501` | EXERCISE; multiple CB polygons; TOP BLW/TOP FL; NIL remark; no future messages |
| `FKPQ30RJTD-1800` | CB circle TOP ABV; NIL remark |

Older schema era — use for **TAC exceptional fixtures** and shape hints; re-encode targets must be 2025-2 XSD/Schematron, not byte-match these XMLs unless audited.

## Guidance exceptional rules (encode cookbook)

Source: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt`

### VAA (lines ~143–179)

| TAC | IWXXM |
|-----|-------|
| Volcano `UNKNOWN` / `UNNAMED` | `EruptingVolcano/name` = that string |
| UNKNOWN position / state / elev / details | nil + `nilReason=unknown` |
| OBS time `NOT PROVIDED` | nil `phenomenonTime` + `missing` |
| `VA NOT IDENTIFIABLE` / `NOT AVBL` / `NOT PROVIDED` | observed `status` accordingly |
| Forecast `NO VA EXP` / `NOT AVBL` / `NOT PROVIDED` | forecast `status` accordingly |
| Remarks `NIL` | nil remarks + `inapplicable` |
| `NO FURTHER ADVISORIES` | nil `nextAdvisoryTime` + `inapplicable` |

### TCA (lines ~182–200)

| TAC | IWXXM |
|-----|-------|
| Cyclone `UNNAMED` | `tropicalCycloneName` = `UNNAMED` |
| Observed CB `NIL` | nil CB + `missing` |
| Remarks `NIL` | nil remarks + `inapplicable` |
| `NO MSG EXP` | nil `nextAdvisoryTime` + `inapplicable` |
| Forecast wind &lt; 34 kt | nil max wind + `nothingOfOperationalSignificance` |
| No longer a TC | nil forecast position + `inapplicable` |

## In-repo non-WMO demos (catalog gate)

| Location | Status under E21-3 |
|----------|-------------------|
| `packages/tac2iwxxm/tests/fixtures/product_matrix/vaa_basic.tac` | Hide from FE Examples until golden-bar passer exists (or replace with `A7-2`) |
| `…/tca_basic.tac` | Same for TCA / `A2-2` |
| `apps/frontend/src/fixtures/examples/bodies/{vaa,tca}_basic.tac` | Same |
| FE catalog gaps (E16-8) | Close by unlocking WMO passers when convert greens |

## Do not conflate

| Product | Root | Issue |
|---------|------|-------|
| VA SIGMET | `iwxxm:VolcanicAshSIGMET` | #739 (Done F23) |
| TC SIGMET | `iwxxm:TropicalCycloneSIGMET` | #738 (OOS) |
| VONA | `vona-A7-1` | #741 (OOS) |
| SWX | Space Weather Advisory | #740 (OOS) |

## Schemas

- `vendor/schemas/iwxxm/2025-2/IWXXM/volcanicAshAdvisory.xsd`
- `vendor/schemas/iwxxm/2025-2/IWXXM/tropicalCycloneAdvisory.xsd`

## Theme→fixture map (T0.1 closed)

Closed mapping for build: [vaa-tca-theme-fixture-map.md](vaa-tca-theme-fixture-map.md).
