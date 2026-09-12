# WMO quality research catalog — S026 / EV-020

> **T0.1** (E20-F2=1). Full mining dig for **AIRMET + METAR/SPECI/TAF** WMO official
> example parity. Cite external / paywalled sources; do **not** copy Annex 3 /
> Manual-on-Codes prose into wheels. Map F24 themes A1–A4 / F25 themes W1–W4 →
> registry codes + fixtures in M1–M5.
> **SIGMET** already quality-barred (F23) — **keep green** in combined CI; no new SIGMET
> fixture work unless regression.

**Tickets:** [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) AIRMET ·
F25 deepen METAR/SPECI/TAF vendor goldens  
**HARD themes:** F24 A1–A4 / F25 W1–W4 (E20-F7 kill-switch — AskQuestion; no silent defer)  
**Naming:** “F24 theme An” / “F25 theme Wn” vs pipeline gates  
**Predecessors:**
[sigmet-research-catalog.md](../../S025-sigmet-quality/reports/sigmet-research-catalog.md) (F23);
[taf-speci-research-catalog.md](../../S020-aerodrome-quality/reports/taf-speci-research-catalog.md) (F20);
[metar-research-catalog.md](../../S015-metar-lint-quality/reports/metar-research-catalog.md) (F15)  
**Policy:** [ADR-032](../../../adr/ADR-032-wmo-default-golden-glossary.md) — `canonicalize_xml`
equality under **default** convert settings only.

---

## Sources

| Source | Access | Role for F24/F25 |
|--------|--------|------------------|
| Vendor `TAC-to-XML-Guidance.txt` (2025-2) | In-repo `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` · [wmo-im/iwxxm v2025-2](https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt) | **Primary encode cookbook** — METAR/SPECI, TAF, AirspaceVolume, AIRMET/SIGMET |
| FM 205 / WMO-No. 306 Vol I.3 Part D | Cite [WMO-306-vI-3-2023-mining-notes.md](../../../domain/mining/WMO-306-vI-3-2023-mining-notes.md); runtime pin → vendor 2025-2 XSD+SCH | Authoritative IWXXM representation |
| ICAO Annex 3 (Ch.7 + App 6; App 3/5) | **Paywall** — cite [icao-annex-3-mining-notes.md](../../../domain/mining/icao-annex-3-mining-notes.md) only | SARPs: AIRMET / METAR·SPECI / TAF |
| EUR Doc 014 (5th Ed. 2023) | **Public** — [icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md](../../../domain/mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) | AIRMET TAC shape; AHL `WA`→`LW`; Part 4; App C informative |
| codes.wmo.int | Public — [RULE_SOURCE_URLS.md](../../../domain/rules/RULE_SOURCE_URLS.md) | AirWxPhenomena; nilReason; MetFeature |
| Official IWXXM examples (2025-2) | Vendor examples dir | Golden seeds (table below) |
| ISSUE_CATALOG / ADR-028 | In-repo | AIRMET SCREAMING_SNAKE codes; tags `airmet` |
| #731 exceptional-rule table | Issue body | AIRMET / SIGMET family cancel + geometry |
| F15/F20 research catalogs | Session reports | METAR/SPECI/TAF lint already deep; F25 = **vendor XML parity** |

**2025-2 corrections:** do **not** encode removed METAR `runwayState` / `CLRD` / `R88` /
`R99` / `SNOCLO` deposit mappings from older guidance rows.

**API wire:** Unchanged `product=` values (`airmet`, `metar`, `speci`, `taf`); decode
shape unchanged (richer strings only — ADR-032).

---

## Official WMO golden seeds (defaults)

| Theme | TAC | Vendor XML | Root | Cycle role |
|-------|-----|------------|------|------------|
| **A3** | `airmet-A6-1a-TS.tac` | `airmet-A6-1a-TS.xml` | `iwxxm:AIRMET` | F24 HARD golden |
| **W1** | `metar-A3-1.tac` | `metar-A3-1.xml` | `iwxxm:METAR` | F25 HARD |
| **W2** | `speci-A3-2.tac` | `speci-A3-2.xml` | `iwxxm:SPECI` | F25 HARD |
| **W3** | `taf-A5-1.tac` | `taf-A5-1.xml` | `iwxxm:TAF` | F25 HARD |
| **W3** | `taf-A5-2.tac` (`TAF AMD … CNL`) | `taf-A5-2.xml` | `iwxxm:TAF` cancel | F25 HARD (E20-E1; S02.M1) |
| Keep | `sigmet-A6-1a-TS` / CNL | existing F23 goldens | `iwxxm:SIGMET` | Regression in `wmo-quality.yml` |
| Not happy-path | `*-translation-failed.*` | — | translation-failed | A4 / adjacency only |

---

## Themes → work items

| ID | Theme | Lint (F12/F24) | Convert (F6) | Validate / goldens / UI |
|----|-------|----------------|--------------|-------------------------|
| **A1** | AIRMET header / sequence / validity / FIR | Registry + accept/negatives | IR header fields | — |
| **A2** | Phenomenon + intensity (ISOL TS, STNR, WKN, …) | Registry | AirWxPhenomena URI; intensityChange; STNR motion | SCH |
| **A3** | Geometry + vertical (AirspaceVolume / posList / TOP ABV FL) | — | **M-golden vs vendor** | M-xsd / M-sch |
| **A4** | Negatives + translation-failed adjacency | Negatives | Not happy-path Examples | — |
| **W1** | `metar-A3-1` vendor equality | Reuse F15 | `canonicalize_xml` == vendor | M-xsd/M-sch; catalog when green |
| **W2** | `speci-A3-2` vendor equality | Reuse F20 | same | same |
| **W3** | `taf-A5-1` + `taf-A5-2` vendor equality | Reuse F20 | TAF + cancel/AMD | same |
| **W4** | Examples catalog gate | — | — | Only WMO-passers; incremental unlock (E20-F4) |
| **C1** | Common rules (shared) | Where TAC applies | Cite F23 C1 pattern; defer convert-only | Round-trip |

---

## Theme detail — AIRMET (F24 A1–A4)

### A1 — Header / sequence / validity / FIR

| Concern | Encode / SARPs cite | Lint intent |
|---------|---------------------|-------------|
| First line | `CCCC AIRMET [seq] VALID YYGGgg/YYGGgg CCCC-` (EUR Doc 014 Part 4) | Sequence + VALID present |
| FIR / CTA | `issuingAirTrafficServicesRegion` Airspace designator + name | FIR tokens |
| ATS unit / MWO | Unit designators on issue path | Issuing identity |
| Validity | AIRMET caps (Annex 3 / EUR) | Duration / midnight guards |
| AHL | TAC `WA` → IWXXM `LW` | Bulletin heading when packed |

**Baseline today:** `packages/tac-validate/tests/fixtures/{accept,negative}/airmet/` —
`airmet_basic.tac`, `missing_valid.tac`, `multi_phenomenon.tac`.  
**Gap:** richer A1 negatives (bad sequence, FIR shape) with registry codes tagged `airmet`.

### A2 — Phenomenon + intensity / movement

| TAC (golden seed) | Encode (Guidance + #731) | Lint intent |
|-------------------|--------------------------|-------------|
| `ISOL TS` | `phenomenon` → `…/AirWxPhenomena/ISOL_TS` | AirWx code list |
| `OBS` | `timeIndicator="OBSERVATION"`; phenomenonTime may be nil/`missing` | OBS/FCST |
| `STNR` | Empty `directionOfMotion` + nilReason `…/inapplicable`; `speedOfMotion` **0** | Stationary |
| `WKN` | `intensityChange="WEAKEN"` | Intensity tokens |
| `TOP ABV FLnnn` | AirspaceVolume: `upperLimit=nnn`; `maximumLimit` nil + `unknown` | Level grammar |

**EUR Doc 014:** Part 4 AIRMET preparation; App A abbreviations for decode glossary (F9).

### A3 — Geometry golden (`airmet-A6-1a-TS`) — **primary #731 gap**

Vendor XML requires:

1. Root `iwxxm:AIRMET` with `reportStatus="NORMAL"` / `permissibleUsage="OPERATIONAL"`.
2. Issue / ATS / MWO / FIR / `sequenceNumber` / `validPeriod` matching TAC times.
3. `phenomenon` AirWx URI `ISOL_TS`.
4. `AIRMETEvolvingConditionCollection` `timeIndicator="OBSERVATION"`.
5. Member geometry = **`aixm:AirspaceVolume`** with:
   - `upperLimit uom="FL">100</…>` + `upperLimitReference` STD
   - `maximumLimit` nil + `nilReason="unknown"` (TOP ABV)
   - `horizontalProjection` / `aixm:Surface` with CRS (`srsName` EPSG:4326, `srsDimension="2"`, `axisLabels="Lat Long"`)
   - `gml:posList` polygon approximating **`N OF S50`** (vendor box −50/50 … −40/70 … closed ring)
6. Stable `gml:id` strategy acceptable for `canonicalize_xml` equality (F23 pattern).

**Known gap today:** convert path often yields **nil / empty geometry** vs vendor `AirspaceVolume`/`posList`.  
**Shared rules with SIGMET (#731 table):** CNL, point→circle r=0, single altitude both limits, STNR, polygon CRS, TOP ABV/BLW (AirspaceVolume section of Guidance).

**CI assert:** `canonicalize_xml(convert(tac, defaults)) == canonicalize_xml(vendor_xml)` + XSD + SCH.

### A4 — Negatives + translation-failed

| Case | Intent |
|------|--------|
| Multi-phenomenon / missing VALID | Existing negatives; extend registry completeness (TC-F24-001/004) |
| `airmet-translation-failed` | Not happy-path Examples; adjacency with SIGMET/VA (never silent root/product swap) |
| Bad CNL shape | When CNL AIRMET supported — omit phenomenon/analysis |

---

## Theme detail — METAR / SPECI / TAF (F25 W1–W4)

F15/F20 already raised **lint quality**. This cycle’s bar is **vendor example XML parity**
under defaults (ADR-032), not re-litigating R1–R8 / T1–T4 unless golden work exposes a gap.

### W1 — `metar-A3-1`

- Convert → `canonicalize_xml` == vendor `metar-A3-1.xml`.
- Prior F15 goldens may be product_matrix / synthetic — **do not** treat those as WMO
  official unless they match vendor.
- Guidance METAR/SPECI section + All-reports common; **no** runwayState encode (2025-2).

### W2 — `speci-A3-2`

- Same equality bar; root `iwxxm:SPECI`.
- Adjacency with METAR Auto-detect remains F15/F20; F25 must not break it.

### W3 — `taf-A5-1` + `taf-A5-2`

| Example | TAC note | Encode focus |
|---------|----------|--------------|
| A5-1 | Standard TAF | Base/change forecasts vs vendor |
| A5-2 | `TAF AMD … CNL` | Guidance: `isCancelReport=true`; cancelled validity; **absent** validPeriod / baseForecast / changeForecast |

Treat A5-2 like SIGMET CNL peer (S02.M1).

### W4 — Examples catalog gate

- List **only** demos that pass WMO default golden for in-scope products (E20-3).
- **Incremental unlock** (E20-F4 / S02.L2): keep SIGMET passers; add AIRMET after A3 green;
  METAR/SPECI after W1–W2; TAF after W3.
- Translation-failed fixtures never happy-path Examples.
- Vitest: TC-F25-003 / deepen TC-F7-008.

---

## Decode glossary (F9 deepen — M5)

| Concern | Plan |
|---------|------|
| Primary meanings | Official/near-official (codes.wmo.int, Annex cites, EUR App A, F3/OpenAIP names) |
| Overrides file | `packages/tac2iwxxm/src/tac2iwxxm/data/decode_glossary.yaml` |
| Env | `TAC2IWXXM_DECODE_GLOSSARY_PATH` (S02.L1) |
| Loader dep | Prefer existing transitive PyYAML; else declare `pyyaml` on tac2iwxxm (E20-F5=2) |
| Miss behavior | OpenAIP/F3 miss → keep ICAO designator; decode must not fail |
| API | Richer `summary`/`segments` strings only; no required new fields (ADR-032) |

Token seeds from AIRMET golden: `ISOL`, `TS`, `OBS`, `STNR`, `WKN`, `TOP`, `ABV`, `FL`,
FIR name `SHANLON`, designator `YUDD`.

---

## Combined CI (`wmo-quality.yml` — T0.3 / E20-F3=3)

| Pack | Filter intent |
|------|---------------|
| SIGMET / VA | Existing `run_sigmet_quality.sh` content (keep green) |
| AIRMET | `-k airmet or AIRMET` (tac-validate + tac2iwxxm) |
| METAR/SPECI/TAF WMO | Golden / annex3 tests for A3-1, A3-2, A5-1, A5-2 |
| Makefile | `make test-wmo-quality`; deprecate or alias `test-sigmet-quality` |

Does **not** replace full `ci-cd.yml` package jobs.

---

## Gaps → milestone map

| Gap | Milestone |
|-----|-----------|
| Research + matrix links + combined CI | M0 (T0.1–T0.3) |
| AIRMET registry A1–A2 | M1 |
| AIRMET geometry golden A3 + A4 | M2 |
| METAR/SPECI vendor equality | M3 |
| TAF A5-1/A5-2 equality | M4 |
| Glossary + catalog unlock | M5 |
| Smoke / 08 / 10 / 11 / 13 | M6 |

---

## OOS this cycle

- TC SIGMET #738, VAA #736, TCA #737, SWX/VONA quality bars
- PyPI version bumps unless required by pyyaml declare
- Non-default profiles / alternate IWXXM versions for golden equality
- New CORS / `VITE_*` knobs
