# VAA / TCA theme → fixture map — S027 / EV-021 (T0.1)

**Date**: 2026-07-29  
**Task**: T0.1 (E21-T2=1 — close inventory; light dig)  
**Seed**: [wmo-vaa-tca-examples-inventory.md](wmo-vaa-tca-examples-inventory.md)  
**Authority**: 2025-2 defaults; `canonicalize_xml` (E21-2 / ADR-032). Translation Amd79 XMLs = TAC themes only (E21-D4).

## Keep-green (regression — do not regress)

| Pack | Themes / goldens | Owner |
|------|------------------|-------|
| F23 SIGMET + VA SIGMET | G1–G3 / V1–V3 / C1 | S025 |
| F24 AIRMET | A1–A4 | S026 |
| F25 METAR/SPECI/TAF | W1–W4 | S026 |

Always write **F26 theme Vn** vs **F23 theme Vn** (`D-S027-EV021-s02m1-1`).

---

## F26 — VAA themes → fixtures

### F26 theme V3 — golden (HARD)

| Role | Path |
|------|------|
| TAC | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/va-advisory-A7-2.tac` |
| XML | `…/va-advisory-A7-2.xml` |
| Pack | `packages/tac2iwxxm/tests/fixtures/annex3_golden/vaa_a7_2.{tac,golden.xml}` |
| Assert | convert(defaults) → `canonicalize_xml` == vendor; root `iwxxm:VolcanicAshAdvisory` |
| TC | TC-F26-002 / TC-F26-003 — `test_tc_f26_002_vaa_annex3_goldens.py` |
| Notes | Karymsky / TOKYO; FCST +18 HR `NO VA EXP` → `status="NO_VOLCANIC_ASH_EXPECTED"`; OBS ring vertex order follows TAC (WMO example reorders one triangle) |

### F26 theme V1 — exceptional lint/encode (HARD)

Guidance (`TAC-to-XML-Guidance.txt` §VAA) + #736 table → accept + negative fixtures:

| TAC cue | IWXXM / lint target | Fixture source |
|---------|---------------------|----------------|
| Volcano `UNKNOWN` / `UNNAMED` | name string as-is | Guidance + synth |
| UNKNOWN position / elev / details | nil + `unknown` | Guidance + synth |
| OBS time `NOT PROVIDED` | nil `phenomenonTime` + `missing` | Guidance |
| `VA NOT IDENTIFIABLE` / `NOT AVBL` / `NOT PROVIDED` | observed `status` | Guidance; mine `FVAG01SABM-1600` TAC |
| Forecast `NO VA EXP` / `NOT AVBL` / `NOT PROVIDED` | forecast `status` | Golden A7-2; `FVAU03ADRM-0424`; `FVFE01RJTD-1720` |
| Remarks `NIL` | nil remarks + `inapplicable` | `FVFE01RJTD-1720` TAC |
| `NO FURTHER ADVISORIES` | nil `nextAdvisoryTime` + `inapplicable` | `FVAG01SABM-1600` TAC |
| Colour NOT GIVEN / NOT AVBL | colour nil / status | `FVAG01SABM-1600`; `FVXX23KNES-1922` |

**Translation package TAC paths** (mine themes; do **not** byte-match Amd79 XML under 2025-2):

- `vendor/schemas/iwxxm-translation/Amd79-80-2023/volcanic-ash-advisory/FVAG01SABM-1600*`
- `…/FVAU03ADRM-0424*`
- `…/FVFE01RJTD-1720*`
- `…/FVXX23KNES-1922*`

### F26 theme V2 — adjacency (HARD)

| Guard | Fixture intent | TC |
|-------|----------------|-----|
| `product=vaa` never emits `iwxxm:VolcanicAshSIGMET` | VAA TAC → advisory root only | TC-F26-006 |
| VA SIGMET path never emits `iwxxm:VolcanicAshAdvisory` | Keep F23 VA SIGMET green | complements TC-F23-006 |

**Fixtures (T1.3):** `packages/tac2iwxxm/tests/test_tc_f26_006_adjacency.py` —
parametrizes F26 V1 VAA accept pack + `vaa_basic` and F23 VA SIGMET accept
(`sigmet_v1_va_volcano`, `sigmet_v1_no_va_exp`); cross-product lint/convert
rejection + bulletin-neighbor no silent-swap.

### F26 theme C1 — common rules

| Rule | Fixture |
|------|---------|
| `reportStatus` / `permissibleUsage` | accept pack |
| `translationFailedTAC` | `va-advisory-translation-failed.{tac,xml}` — **not** catalog happy-path |
| Geometry CRS / nilReasons / one-IWXXM-per-TAC | accept + negatives |

### Catalog gate (F7.g / S02.M2)

| Demo | Until F26 V3 greens |
|------|---------------------|
| `vaa_basic` (package + FE bodies) | **Hide** from Examples |
| Unlock | When TC-F26-002 green → offer `va-advisory-A7-2` (or renamed passer) |

---

## F27 — TCA themes → fixtures

### F27 theme T3 — golden (HARD)

| Role | Path |
|------|------|
| TAC | `vendor/schemas/iwxxm/2025-2/IWXXM/examples/tc-advisory-A2-2.tac` |
| XML | `…/tc-advisory-A2-2.xml` |
| Assert | convert(defaults) → `canonicalize_xml` == vendor; root `iwxxm:TropicalCycloneAdvisory` |
| TC | TC-F27-002 / TC-F27-003 |
| Notes | GLORIA / YUFO; `RMK: NIL` → remarks `nilReason=inapplicable` |

### F27 theme T1 — exceptional lint/encode (HARD)

| TAC cue | IWXXM / lint target | Fixture source |
|---------|---------------------|----------------|
| Cyclone `UNNAMED` | `tropicalCycloneName=UNNAMED` | Guidance + synth |
| Observed CB `NIL` | nil CB + `missing` | Guidance; `FKNT23KNHC-1458` (no CB) |
| Remarks `NIL` | nil remarks + `inapplicable` | Golden A2-2; `FKNT23KNHC-1501`; `FKPQ30RJTD-1800` |
| `NO MSG EXP` | nil `nextAdvisoryTime` + `inapplicable` | Guidance; `FKNT23KNHC-1501` |
| Forecast wind &lt;34 kt | nil max wind + `nothingOfOperationalSignificance` | Guidance + synth |
| No longer a TC | nil forecast position + `inapplicable` | Guidance; weakening `FKNT23KNHC-1458` |
| EXERCISE / TEST abbreviated | status / permissibleUsage | `FKNT23KNHC-1500` / `1501` |
| CB circle TOP ABV / TOP BLW/FL | geometry encode | `FKPQ30RJTD-1800`; `FKNT23KNHC-1501` |

**Translation package TAC paths**:

- `…/tropical-cyclone-advisory/FKNT23KNHC-1458*`
- `…/FKNT23KNHC-1500*`
- `…/FKNT23KNHC-1501*`
- `…/FKPQ30RJTD-1800*`

### F27 theme T2 — adjacency (HARD)

| Guard | Fixture intent | TC |
|-------|----------------|-----|
| `product=tca` never emits `iwxxm:TropicalCycloneSIGMET` | TCA → advisory root only | TC-F27-006 |
| #738 TC SIGMET quality | **OOS** this cycle | cite-only |

### F27 theme C1 — common rules

| Rule | Fixture |
|------|---------|
| Same C1 family as F26 | accept pack |
| `translationFailedTAC` | `tc-advisory-translation-failed.{tac,xml}` — not catalog happy-path |

### Catalog gate (F7.g / S02.M2)

| Demo | Until F27 T3 greens |
|------|---------------------|
| `tca_basic` | **Hide** from Examples |
| Unlock | When TC-F27-002 green → offer `tc-advisory-A2-2` **independently** of VAA |

---

## OOS (cite-only)

| Item | Issue |
|------|-------|
| TC SIGMET | #738 |
| SWX | #740 |
| VONA `vona-A7-1` | #741 |
| 2023-1 `va-advisory-A2-1` as 2025-2 golden | different example id |
| Amd79 XML byte-match under 2025-2 | E21-D4 |

## Schemas (encode targets)

- `vendor/schemas/iwxxm/2025-2/IWXXM/volcanicAshAdvisory.xsd`
- `vendor/schemas/iwxxm/2025-2/IWXXM/tropicalCycloneAdvisory.xsd`
- + Schematron packs for those products

## M0 exit

- [x] Theme → fixture map written (this doc)
- [x] COVERAGE_MATRIX links (T0.2)
- [x] `wmo-quality.yml` extended for VAA+TCA (T0.3)
