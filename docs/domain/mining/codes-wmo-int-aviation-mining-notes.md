# codes.wmo.int — aviation registers (2026-07-30 refresh)

Transitory dig — **not** standing SoT. Cite URIs; do not dump registries into git.

**Source:** WMO Codes Registry  
**URL:** https://codes.wmo.int/  
**Local:** `.local/reference/codes-wmo-int-aviation/` (optional extracts only)  
**Label:** **normative-vocabulary**  
**Mined:** 2026-07-30  
**Ticket:** [#797](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/797)  
**Prior catalog:** [RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) §codes.wmo.int · [COVERAGE_MATRIX](../rules/COVERAGE_MATRIX.md) §codes.wmo.int × product

## Focus

Confirm live aviation register inventory vs vendor RDF / encode hrefs for F6 products.

## Register inventory (live HTML, 2026-07-30)

### `https://codes.wmo.int/iwxxm`

| Register | Role |
|----------|------|
| `AviationColourCode` | VONA / 2025-2 colour vocabulary |
| `MeteorologicalFeature` | Feature typing (VA/TC/etc.) |
| `nil` | IWXXM-native nil set (parallel to `common/nil`) |

### `https://codes.wmo.int/49-2`

| Register | Products |
|----------|----------|
| `AerodromePresentOrForecastWeather` | METAR/SPECI/TAF |
| `AerodromeRecentWeather` | METAR/SPECI |
| `CloudAmountReportedAtAerodrome` | METAR/SPECI/TAF |
| `SigConvectiveCloudType` | CB/TCU |
| `SigWxPhenomena` | SIGMET |
| `AirWxPhenomena` | AIRMET |
| `WeatherCausingVisibilityReduction` | AIRMET |
| `AviationColourCode` | Legacy colour set (≠ `iwxxm/` member set) |
| `MeteorologicalFeature` | Experimental / dual with `iwxxm/` |
| `SpaceWxLocation` / `SpaceWxPhenomena` | SWX |
| `observable-property` / `observation-type` | Observables |

### `https://codes.wmo.int/common/nil`

Members observed: `missing`, `inapplicable`, `unknown`, `withheld`, `template`, `notObservable`, `notDetectedByAutoSystem`, `nothingOfOperationalSignificance`, `noSignificantChange`, `AboveDetectionRange`, `BelowDetectionRange`.

`iwxxm/nil` exposes the **same notation set** (11 concepts) — dual SCH paths remain (`IWXXM.nilReasonCheckLegacy` vs `IWXXM.nilReasonCheck`).

### Colour set divergence (still material)

| `49-2/AviationColourCode` | `iwxxm/AviationColourCode` |
|---------------------------|----------------------------|
| GREEN, YELLOW, ORANGE, RED, **NIL**, **NOT_GIVEN**, **UNKNOWN** (7) | GREEN, YELLOW, ORANGE, RED, **UNASSIGNED** (5) |

Encode per XSD `vocabulary=` for the target package (2025-2 VONA → `iwxxm/`).

### MetFeature divergence (confirmed live + vendor RDF 2026-07-30)

| Register | Unique members | Delta |
|----------|----------------|-------|
| `49-2/MeteorologicalFeature` | **27** | — |
| `iwxxm/MeteorologicalFeature` | **28** | **`VOLCANIC_ASH` only on `iwxxm/`** |

Shared core includes `VOLCANO`, `TROPICAL_CYCLONE`, `QUASI-STATIONARY_FRONT_*`, fronts, turbulence, etc. Vendor SCH RDF (`codes.wmo.int-*-MeteorologicalFeature.rdf`) **matches** live HTML when notations allow hyphens. For VAA ash-feature hrefs under pin **2025-2**, prefer `iwxxm/MeteorologicalFeature/VOLCANIC_ASH` when XSD/examples use that vocabulary — do not invent the concept under `49-2/`.

### Weather tokens `306/4678`

| Source | Unique notations | Use |
|--------|------------------|-----|
| Live HTML browse (`Accept: text/html`) | **~101** (incomplete page / subset) | Discovery only |
| Vendor `iwxxm-codelists` CSV `CSV/306/4678/4678_entity.csv` | **402** (`status=stable`) | **CI / membership SoT** with Manual-wins caveat |

Do **not** treat the HTML browse count as the full register. Sample HTML compounds still include `+SHRASN`, `+TSGR`. Local: `.local/reference/codes-wmo-int-aviation/extracts/member-sets-2026-07-30.json` + `4678-count-note.json` (gitignored).

### Access friction

Bare `curl` without `Accept: text/html` (or RDF media types) often returns **404** on register pages; browser / Linked Data clients succeed. Documented on catalog `iwxxm` register row.

### SCH RDF coverage (vendor pin `iwxxm` v2025-2)

| RDF under `IWXXM/rule/` | Matches live members? |
|-------------------------|------------------------|
| `codes.wmo.int-49-2-AviationColourCode.rdf` | ✅ 7/7 |
| `codes.wmo.int-iwxxm-AviationColourCode.rdf` | ✅ 5/5 |
| `codes.wmo.int-common-nil.rdf` / `…-iwxxm-nil.rdf` | ✅ 11/11 each |
| `codes.wmo.int-49-2-MeteorologicalFeature.rdf` | ✅ 27/27 |
| `codes.wmo.int-iwxxm-MeteorologicalFeature.rdf` | ✅ 28/28 (incl. VOLCANIC_ASH) |

No SCH `document()` filename gap for these dual registers on the current pin.

## Gaps / conflicts

| Claim | Action |
|-------|--------|
| Live registry is SoT for hrefs | Keep offline RDF/CSV for CI; optional live smoke only |
| Dual nil / colour registers | Assert encode hrefs match XSD vocabulary + SCH RDF for pin (#797) |
| Dual MetFeature (+ `VOLCANIC_ASH`) | Same rule as colour — encode per XSD `vocabulary=` (#797) |
| HTML `306/4678` ≈101 | **Incomplete** vs vendor **402** — prefer CSV/RDF; optional live full dump not required for CI |

## Product × artifact matrix

| Product | Register / URI family | Role | Official landing | Gap vs GIFTs | Consumer |
|---------|----------------------|------|------------------|--------------|----------|
| METAR/SPECI/TAF | `306/4678/{TAC}` (vendor CSV **402**); `49-2` weather/cloud/recent; `common/nil` | vocab + nil | codes.wmo.int | Machine enumerations | `tac-validate`, `tac2iwxxm`, SCH RDF |
| SIGMET | `49-2/SigWxPhenomena` | phenomenon href | same | Outside GIFTs | convert + SCH |
| AIRMET | `49-2/AirWxPhenomena` + VIS-cause | phenomenon href | same | Outside GIFTs | convert + SCH |
| VAA / VONA | `iwxxm/AviationColourCode` (+ MetFeature; **`VOLCANIC_ASH`**) | colour + feature | `codes.wmo.int/iwxxm/…` | Dual colour; MetFeature +1 vs `49-2` | convert + SCH |
| TCA | MetFeature `TROPICAL_CYCLONE` + nils | feature | both registers share TC | Outside GIFTs | convert |
| SWX | `SpaceWxLocation` / `SpaceWxPhenomena` | beyond F6 core | `49-2/` | IWXXM-native | #740 |
| All | `common/nil` **and** `iwxxm/nil` | nilReason | both landings | Dual SCH patterns | `iwxxm-validate` |

## Catalog paste rows

```text
### codes.wmo.int aviation refresh (2026-07-30)
- Publisher: WMO Codes Registry
- URL: https://codes.wmo.int/ (+ /iwxxm, /49-2, /common/nil, /306/4678)
- Access: public Linked Data
- Applies to: products=[all F6 + SWX/VONA]; profiles=[annex3,iwxxm_us]; role=[validation,conversion,iwxxm-validation]
- Gap vs GIFTs: dual colour/nil; MetFeature VOLCANIC_ASH (28 vs 27); HTML 4678 incomplete vs CSV 402
- Consumer: tac-validate | tac2iwxxm | iwxxm-validate | UI-decode
- Label: normative-vocabulary
- Caveats: offline CSV/RDF for CI; Accept header needed for HTML; Manual wins over CSV; do not dump registries into git
- Mined: 2026-07-30 · #797 · detail mining/codes-wmo-int-aviation-mining-notes.md
```

## Domain-knowledge cross-check

| Older claim | This pass (2026-07-30) | Action |
|-------------|------------------------|--------|
| Tier A TBD: diff `49-2` vs `iwxxm` colour members | Confirmed: 49-2 has NIL/NOT_GIVEN/UNKNOWN; iwxxm has **UNASSIGNED** | Promoted to canonicals; close Tier A “suggested next” item 1 as done for colour |
| Tier A / dig TBD: MetFeature member-set diff | `iwxxm/` adds **`VOLCANIC_ASH`** (**28** vs **27**) | Promoted; caveat `49-2` experimental MetFeature |
| Prefer only `common/nil` | Live `iwxxm/nil` has same 11 notations | Keep dual SCH; encode per example/XSD vocabulary |
| Live codes.wmo.int for CI | Still optional; HTML needs Accept | Prefer vendor `rule/*.rdf` (no change) |
| “100+” / “~101” 4678 concepts as full register | Live HTML ≈ **101**; vendor CSV = **402** stable | **Caveat HTML incompleteness**; CI = CSV/RDF |
| SCH RDF may lag live colour/nil/MetFeature | Pin RDF **byte-matches** live member sets (2026-07-30) | Close “confirm SCH RDF filenames” next-pass |

## Implications for this repo

- **F6 / tac2iwxxm:** VAA/VONA colour → `iwxxm/AviationColourCode/{…}`; ash MetFeature → `iwxxm/MeteorologicalFeature/VOLCANIC_ASH` when vocabulary requires it; classic F6 nils stay example-aligned (`common/nil` unless XSD says otherwise).
- **tac-validate:** Weather token membership via offline **402**-row 4678 CSV / RDF (not HTML browse).
- **iwxxm-validate:** Keep both nil RDF + both colour RDF + MetFeature RDF in pin — filenames present and member-complete for current pin.
- **Caveats / TBD:** Periodic vendor-sync re-diff vs live colour/MetFeature only; do not gate on HTML 4678 count.

## Suggested next mining passes

1. ~~Member-set diff MetFeature~~ — **done** (`VOLCANIC_ASH` only on `iwxxm/`; counts 28 vs 27).
2. ~~Confirm SCH RDF filenames~~ — **done** (colour/nil/MetFeature all present + match).
3. ~~Diff vendor 4678 vs live HTML~~ — **done** (HTML incomplete; CSV=402 SoT).
4. Optional: after next `iwxxm-codelists` sync, re-diff colour/MetFeature RDF vs live.

## Promotion checklist

- [x] Inventory confirmed against existing catalog rows (no URL invent)
- [x] Canonical encode/validate notes for colour/nil dual registers (`IWXXM_CONVERSION` / `IWXXM_VALIDATION` / `COVERAGE_MATRIX`)
- [x] MetFeature `VOLCANIC_ASH` delta promoted (counts corrected 28/27)
- [x] 4678 HTML-incomplete vs CSV-402 caveat promoted
- [x] SCH RDF coverage confirmed
- [x] Mining index updated
- [x] Product matrix + cross-check + implications (this continue)
- [x] Optional live `306/4678` count smoke — **not needed** for CI (prefer CSV); closed as mining item
