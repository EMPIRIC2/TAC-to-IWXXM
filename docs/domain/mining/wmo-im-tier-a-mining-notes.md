# wmo-im Tier A local clones — mining notes

**Status:** working notes (not normative). Runtime SoT remains `vendor/schemas/*` + `vendor/manifest.json`.  
**Focus of this pass:** pull Tier A repos locally; mine products × artifacts for encode / validate / fixtures  
**Ticket:** pairs with [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local clones (gitignored):** `.local/reference/wmo-im-tier-a/`

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Org survey | [mining/wmo-im-org-mining-notes.md](./wmo-im-org-mining-notes.md) |
| Creation companion | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| Validation companion | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Modelling (separate) | [mining/iwxxm-modelling-v2025-2-mining-notes.md](./iwxxm-modelling-v2025-2-mining-notes.md) |

| Item | Value |
|------|-------|
| Title | Tier A local mine (`iwxxm`, `iwxxm-codelists`, `iwxxm-modelling`, `iwxxm-translation`) |
| Publisher | WMO TT-AvData / wmo-im |
| Official landings | https://github.com/wmo-im/{iwxxm,iwxxm-codelists,iwxxm-modelling,iwxxm-translation} |
| Pin / edition | Manifest SHAs (see table); package line **2025-2** |
| Date mined | 2026-07-14 |
| Access | public |
| Label | mixed: normative-schema / normative-vocabulary / informative |

---

## Local checkout inventory

| Dir under `.local/reference/wmo-im-tier-a/` | Manifest label | Checked out SHA | Matches vendor? |
|--------------------------------------------|----------------|-----------------|-----------------|
| `iwxxm/` | tag `v2025-2` | `35180cbe…` | **Yes** (vendor pin) |
| `iwxxm-tag-v2025-2/` | — (drift ref) | `2c4db03…` (current GitHub **tag tip**) | Tag tip **older** than vendor pin |
| `iwxxm-codelists/` | `49-2` | `b0511b76…` | **Yes** |
| `iwxxm-modelling/` | `v2025-2` | `ec099bfd…` | **Yes** |
| `iwxxm-translation/` | `master` | `a251e8bc…` | **Yes** |

Key files under pin match vendor byte-for-byte (spot-check: `TAC-to-XML-Guidance.txt`, `rule/iwxxm.sch`).

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Machine SoT family for XSD, Schematron, offline RDF, official TAC↔XML examples, TAC→nilReason guidance | ICAO Annex 3 / Doc 8896 TAC grammar text |
| Working FM 205 AsciiDoc (`documentation/manual/FM205.adoc` = **FM 205-2025-2**) aligned to this package line | Automatic replacement for WMO e-Library PDF of Manual on Codes (still cite library for formal publish) |
| Informative amendment-tagged fixtures in `iwxxm-translation` | Official WMO/ICAO status (README disclaimer) |

---

## Critical pin / tag conflicts (defer-to-latest)

| Claim A | Claim B | Action |
|---------|---------|--------|
| GitHub tag `v2025-2` → `2c4db03` (2025-11-25; flat `IWXXM/` layout) | Vendor + manifest SHA `35180cbe` (2026-02-17; **versioned** `2025-2/IWXXM/` + `2023-1/`) | **Runtime wins:** vendor/manifest SHA. Cite `schemas.wmo.int/iwxxm/2025-2/` for HTTP. Treat bare “tag tip” clones as incomplete. |
| Manifest label `iwxxm-codelists` / `49-2` | **No** Git tag named `49-2` on remote; branches `master` and `2025-2` both **ahead** of pin SHA | Cite **commit SHA** + registry CSV; do not assume `git checkout 49-2` works |
| ReleaseNotes: prefer `codes.wmo.int/iwxxm/{AviationColourCode,nil,MeteorologicalFeature}` for VONA/WAFS/QVACI/MetFeature | Official METAR/TAF examples + `TAC-to-XML-Guidance.txt` still encode **`common/nil`** | **Both valid by product:** follow Guidance + official examples for classic F6; follow XSD `vocabulary` + SCH RDF doc for 2025-2-native lists (`iwxxm/*`). SCH has **both** `IWXXM.nilReasonCheckLegacy` (`common/nil`) and `IWXXM.nilReasonCheck` (`iwxxm/nil`). |
| Guidance still describes `runwayState` / CLRD / SNOCLO / R88 / R99 | ReleaseNotes RC1: **removed** runwayState package from METAR/SPECI 2025-2 | Caveat guidance rows as **historical for this pin**; do not invent runwayState encode for 2025-2 |
| Older WMO-306 Vol I.3 mining cited FM **205-2023-1** package tables | Repo `FM205.adoc` is titled **FM 205-2025-2** with amendment↔version table through Amd **82** → IWXXM **2025-2** | Prefer this AsciiDoc + vendor pin over 2023 printed tables for package selection; keep library PDF for formal citation |

---

## Product × artifact matrix (`iwxxm` pin `2025-2/IWXXM`)

| Product | TAC input artifact | IWXXM output (root / XSD) | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|--------------------|---------------------------|-----------------------------|--------------|----------|
| METAR | `examples/metar-A3-1.tac` (+ NIL collect, translation-failed) | `iwxxm:METAR` / `metarSpeci.xsd` | Guidance METAR/SPECI section; pair XML | REMARKS / US; runwayState gone | tac2iwxxm, iwxxm-validate |
| SPECI | `speci-A3-2.tac` | `iwxxm:SPECI` / same XSD | same | same | same |
| TAF | `taf-A5-1`, cancel `taf-A5-2`, NIL collect, failed | `iwxxm:TAF` / `taf.xsd` | Guidance TAF (NIL/CNL/NSC/NSW) | Outside GIFTs depth | same |
| SIGMET | TS/CNL/TC/VA/multi-VA + failed collect | `SIGMET` / TC / VA / `sigmet.xsd` | Guidance AIRMET and SIGMET + AirspaceVolume | Entire product | same |
| AIRMET | `airmet-A6-1a-TS` + failed | `iwxxm:AIRMET` / `airmet.xsd` | same guidance | Entire product | same |
| VAA | `va-advisory-A7-2` + failed | `VolcanicAshAdvisory` / `volcanicAshAdvisory.xsd` | Guidance Volcanic Ash Advisory | Entire product | same |
| TCA | `tc-advisory-A2-2` + failed | `TropicalCycloneAdvisory` / `tropicalCycloneAdvisory.xsd` | Guidance Tropical Cyclone Advisory | Entire product | same |
| Bulletin | `*-NIL-collect.*`, failed-collect | `iwxxm-collect.xsd` + external `collect/` | examples | Outside GIFTs | bulletin |
| VONA / SWX / WAFS / QVACI | present in examples | `vona.xsd`, `spaceWxAdvisory.xsd`, `WAFSSigWxFC.xsd`, `qvaci.xsd` | ReleaseNotes + examples | Outside F6 / GIFTs | optional encode |

**Layout after pin reorg:** package lives at `2025-2/IWXXM/` (also mirrored under repo-root `IWXXM/` and `2023-1/` for lineage). HTTP publish stays flat: `https://schemas.wmo.int/iwxxm/2025-2/…`.

---

## Key findings

### 1. `iwxxm` — normative schema + conversion notes + examples

- **15** product/common XSDs including `iwxxm-collect.xsd`; single Schematron `rule/iwxxm.sch`.
- Offline RDF under `rule/` includes **both** `49-2-*` and `iwxxm-*` colour / MetFeature / nil sets, plus BUFR flags and `common-nil`.
- `TAC-to-XML-Guidance.txt` (~221 lines): products METAR/SPECI, TAF, AirspaceVolume tops, AIRMET/SIGMET, VAA, TCA; classic tokens → `http://codes.wmo.int/common/nil/…`.
- `documentation/manual/FM205.adoc` is **FM 205-2025-2** (Annex 3 + PANS-MET scope; package versions; `schemas.wmo.int` resource list).
- Release date in notes: finalised **2025-2** dated **19 November 2025**; RC1 removed runwayState; RC2 VAA `sourceElevationAMSL`, space-wx locationIndicator multiplicity, etc.

### 2. `iwxxm-codelists` — normative vocabulary (feeds registry)

Registers under `CSV/49-2/` (from container):  
`AerodromePresentOrForecastWeather`, `AerodromeRecentWeather`, `AirWxPhenomena`, `AviationColourCode`, `CloudAmountReportedAtAerodrome`, `MeteorologicalFeature` (**experimental**), `SigConvectiveCloudType`, `SigWxPhenomena`, `SpaceWxLocation`, `SpaceWxPhenomena`, `WeatherCausingVisibilityReduction`, plus `observable-property` / `observation-type`.  
Also `CSV/306/4678` and `CSV/common/nil`.  
README: if CSV ≠ Manual on Codes, **Manual wins**.

### 3. `iwxxm-translation` — informative fixtures only

- `LATEST_EXAMPLE` → `Amd79-80-2023`.
- Product dirs: **metar** (69 files), **taf** (15), **volcanic-ash-advisory** (9), **tropical-cyclone-advisory** (9).
- **No** dedicated SPECI / SIGMET / AIRMET amendment trees (SPECI appears inside metar test notes only).
- Do not override official `iwxxm` examples.
- **Caveat (2026-07-30 / #797):** suite `IWXXM_VERSION` = **2023-1**. Treat TAC as informative convert inputs under pin **2025-2**; **do not** require XML byte-match to suite fixtures — see [iwxxm-translation-parity-mining-notes.md](./iwxxm-translation-parity-mining-notes.md). Colour dual-register TBD below is **closed** for AviationColourCode members — [codes-wmo-int-aviation-mining-notes.md](./codes-wmo-int-aviation-mining-notes.md).

### 4. `iwxxm-modelling`

Already mined: [mining/iwxxm-modelling-v2025-2-mining-notes.md](./iwxxm-modelling-v2025-2-mining-notes.md). Local clone confirms large `EA/` + `tool/` tree at pin SHA — informative generators only.

---

## Catalog paste rows

```text
### wmo-im Tier A local mine (manifest SHAs)
- Publisher: WMO TT-AvData
- URL: https://github.com/wmo-im/iwxxm (commit 35180cbe…) + siblings
- Access: public; local mirror .local/reference/wmo-im-tier-a/ (gitignored)
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,+VONA/SWX/WAFS/QVACI]; profiles=[annex3]; role=[conversion|iwxxm-validation|bulletin]
- Gap vs GIFTs: full multi-product XSDs/examples; advisories; runwayState removed
- Consumer: tac2iwxxm | iwxxm-validate | bulletin | UI-decode
- Label: normative-schema (+ normative-vocabulary codelists; informative translation)
- Caveats: GitHub tag v2025-2 tip lags vendor SHA; codelists label 49-2 is not a git tag; dual nil/colour registers by product
- Mined: 2026-07-14
```

---

## Domain-knowledge cross-check

| Older claim | This pass | Action |
|-------------|-----------|--------|
| “Checkout tag `v2025-2`” ≡ vendor tree | Tag tip ≠ manifest SHA; layout reorg | Document pin SHA; prefer vendor / schemas.wmo.int |
| WMO-306 mining FM 205-2023-1 as current package map | `FM205.adoc` is 205-**2025-2** with Amd 82 | Caveat 2023 notes; point here + vendor |
| Org survey Tier A “already catalogued” only | Deep mine found dual registers + stale guidance runwayState + translation product gaps | Promote into companions |
| Prefer only `49-2/AviationColourCode` | 2025-2 VONA uses `iwxxm/AviationColourCode` | Keep both URLs; encode per XSD vocabulary |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Keep nilReasons from Guidance (`common/nil`) for METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA; do **not** emit removed `runwayState` for 2025-2; use `iwxxm/*` lists where XSD `vocabulary=` says so (VONA colour, MetFeature, etc.).
- **tac-validate:** Still no Annex 3 text here; FM205.adoc paraphrases product scope only.
- **iwxxm-validate:** Continue offline SCH+RDF under `vendor/schemas/iwxxm/2025-2/IWXXM/rule/`; ensure both nil RDF files stay in catalog for CI.
- **Caveats / TBD:** ~~Optional dedicated pass comparing `49-2` vs `iwxxm` AviationColourCode member sets (NIL/NOT_GIVEN/UNKNOWN vs UNASSIGNED).~~ **Done 2026-07-30** — [codes-wmo-int-aviation-mining-notes.md](./codes-wmo-int-aviation-mining-notes.md). Vendor sync when remote retags `v2025-2` to post-reorg SHA still open.

---

## Suggested next mining passes

1. ~~Diff `49-2` vs `iwxxm` colour + MetFeature concept sets and note schema↔registry casing.~~ **Done** (#797 dig): colour NIL/NOT_GIVEN/UNKNOWN vs **UNASSIGNED**; MetFeature `iwxxm/` **28** vs `49-2/` **27** (**+`VOLCANIC_ASH`**) — [codes-wmo-int-aviation-mining-notes.md](./codes-wmo-int-aviation-mining-notes.md).
2. Refresh [mining/WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) with “superseded package tables → see FM205.adoc 2025-2”.
3. Inventory which SCH patterns fire on official examples (legacy vs iwxxm nil) for CI fixture policy.
4. APAC FAQ encode gotchas — [icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](./icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) (promoted; engine #797).
```
