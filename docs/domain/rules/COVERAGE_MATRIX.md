# Coverage matrix — F6 product × profile × rule sources

**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Mined:** 2026-07-20 (EUR Doc 014 SIGMET/AIRMET Guide dig · prior 2026-07-14 A3/A5/A6 checklists)  
**Legend:** ✅ normative URL present · ⚠ partial / paywall cite · ❌ blocked / TBD

“Validation” in matrices = TAC token/template/vocab rules (not always full grammar offline).  
“Conversion” = TAC → IWXXM mapping / nilReason / href.  
“IWXXM val” = XSD + Schematron + offline RDF for produced XML.

Profiles: **`annex3`** (ICAO/WMO core) · **`iwxxm_us`** (US national extensions).

**Strategies (how to apply these cells):** [../README.md](../README.md) §End-to-end strategy ·
[../TAC_VALIDATION.md](../TAC_VALIDATION.md) §Validation strategy ·
[../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) §Conversion strategy ·
[../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) §Validation strategy ·
[README.md](./README.md) role routing.

---

## Pipeline gate × role (all F6)

| Gate | Role | Public / machine path (paywall = cite-only) | Pass means |
|------|------|---------------------------------------------|------------|
| **G1 TAC lint** | validation | codes.wmo.int + official `.tac` (+ Annex 3 when licensed) | Template / vocab OK for profile |
| **G2 Convert** | conversion | `TAC-to-XML-Guidance.txt` + official pair + pin XSD | Tokens / nils encoded correctly |
| **G3 Well-formed** | iwxxm-validation | XML + declared namespaces (`xmlns:xlink` when used) | Parses |
| **G4 XSD** | iwxxm-validation | Vendored `2025-2/IWXXM/*.xsd` (+ METCE/AIXM) | Structure / types OK |
| **G5 Schematron** | iwxxm-validation | Vendored `rule/iwxxm.sch` + `rule/*.rdf` (`xslt2`) | Business rules OK |
| **G6 Golden** | all | `schemas.wmo.int/iwxxm/2025-2/examples/` | Pair still passes G2–G5 |
| **G7 Bulletin** (when packed) | bulletin | OPMET Guidelines 5th + COLLECT / AHL | Aggregated message ops-ready |

**Release:** G4 **and** G5 on the document’s year line. AWC / iwxxm-translation = smoke only.  
**IWXXM→TAC round-trip:** not a domain gate.

### Product × strategy cite (quick)

| Product | TAC strategy cite | Convert cite | Validate cite |
|---------|-------------------|--------------|---------------|
| METAR / SPECI | **A3-2 checklist** · App 3 §2.3 (SPECI) · vocab | Guidance METAR; CAVOK/NSC/… | `metarSpeci.xsd` · `metar-A3-1` / `speci-A3-2` |
| TAF | **A5-1 checklist** · App 5 §1.3 · A5-2 | CNL/NIL; `VV///` absent | `taf.xsd` · `taf-A5-*` |
| SIGMET / AIRMET | **A6 one-phenomenon** · Ch.7 · SigWx/AirWx · [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) (public TAC shape) | Guidance volumes + hrefs · EUR Doc 014 T1T2 map | `sigmet.xsd` / `airmet.xsd` |
| VAA | App 2 §3.1.2 · **A2-1 checklist** | Colour registry · METCE Volcano | `volcanicAshAdvisory.xsd` · `va-advisory-A7-2` |
| TCA | App 2 §5.1.1/§5.1.3 · **A2-2 checklist** | METCE TropicalCyclone | `tropicalCycloneAdvisory.xsd` · `tc-advisory-A2-2` |
| METAR US | FMH-1 §12 + **§2.5.2.a** + **RMK→iwxxm-us map** | Structured Addendum elements | WMO pin + iwxxm-us 3.0 |

Detail: [TAC_VALIDATION](../TAC_VALIDATION.md) · [IWXXM_CONVERSION](../IWXXM_CONVERSION.md) · [IWXXM_VALIDATION](../IWXXM_VALIDATION.md).

---

## Master: product × has URL?

| F6 product | TAC validation URL? | Conversion URL? | IWXXM validation URL? | Gap vs GIFTs |
|------------|---------------------|-----------------|-----------------------|--------------|
| **METAR** | ✅ Annex 3 (paywall; [dig](../mining/icao-annex-3-mining-notes.md) Table A3-2, CAVOK, AUTO/missing) + codes.wmo.int weather/nils; FMH-1 for US | ✅ TAC-to-XML-Guidance + FM 205 + examples | ✅ schemas.wmo.int/2025-2 + SCH | **S015/EV-011 (#732)**: F15 registry + **R1–R8 themes closed** (lint/fixtures/goldens/adjacency) — [research catalog](../../sessions/S015-metar-lint-quality/reports/metar-research-catalog.md) · [ISSUE_CATALOG](./ISSUE_CATALOG.md) · [context](../../context/metar-lint-quality.md) |
| **SPECI** | ✅ same as METAR (+ App 3 §2.3.2 shall / §2.3.3 Rec thresholds) | ✅ same package `metarSpeci.xsd` | ✅ same | **F15** R1–R8 + adjacency closed; **F20 / #734** full SPECI quality bar — [research catalog](../../sessions/S020-aerodrome-quality/reports/taf-speci-research-catalog.md) (S1–S3) · S020/EV-015 |
| **TAF** | ✅ Annex 3 App 5 (§1.3 change/PROB; Table A5-2) / Doc 8896 (paywall); vocab via 49-2 / 306 | ✅ Guidance + examples (CNL/NIL/AMD) | ✅ `taf.xsd` + SCH | **F20 / #735** TAF quality bar — [research catalog](../../sessions/S020-aerodrome-quality/reports/taf-speci-research-catalog.md) (T1–T4) · S020/EV-015 |
| **SIGMET** | ✅ Annex 3 Ch.7 + App 6 phenomena/validity (paywall); SigWxPhenomena registry; **+** [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) public TAC guide | ✅ Guidance + examples + FM 205 (+ METCE for TC/VA members); EUR Doc 014 AHL `WS`/`WV`/`WC`→`LS`/`LV`/`LY` | ✅ `sigmet.xsd` + SCH (+ METCE 1.2) | **Entire product** outside GIFTs |
| **AIRMET** | ✅ Annex 3 Ch.7 + App 6; AirWxPhenomena + VIS-cause lists; **+** [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) | ✅ Guidance + examples + FM 205; EUR Doc 014 AHL `WA`→`LW` | ✅ `airmet.xsd` + SCH | Entire product outside GIFTs |
| **VAA** | ✅ Annex 3 App 2 §3.1.2 **shall** IWXXM + Table **A2-1** ([dig](../mining/icao-annex-3-mining-notes.md)); Doc 9766 paywall for colour **meanings**; colour machine IDs via registry ✅ | ✅ Guidance + examples + AviationColourCode + [METCE 1.2](https://schemas.wmo.int/metce/1.2/) `Volcano` | ✅ `volcanicAshAdvisory.xsd` (+ METCE embed) | Entire product outside GIFTs |
| **TCA** | ✅ Annex 3 App 2 §5.1.1 (≥34 kt) · §5.1.3 **shall** IWXXM + Table **A2-2** | ✅ Guidance + examples + FM 205 + METCE `TropicalCyclone` | ✅ `tropicalCycloneAdvisory.xsd` (+ METCE embed) | Entire product outside GIFTs |
| **METAR (US)** | ✅ FMH-1 Ch.12 + SPECI §2.5.2 ([dig](../mining/fmh1-2019-mining-notes.md)) + NWS FMH-1 registry | ✅ Body + RMK → iwxxm-us `extension` | ✅ WMO base + iwxxm-us 3.0 | GIFTs stripped REMARKS |
| **Bulletin / AHL** | ✅ WMO AHL page | ✅ AHL T1T2 TAC↔IWXXM + [OPMET Guidelines 5th](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) (`A_…xml.gz`, COLLECT) | COLLECT / iwxxm-collect (vendor `externalSchema`; = `wmo-im/collect` 1.2) | Outside GIFTs; WIS2 path ≠ COLLECT (one resource/notification — [Tier B](../mining/wmo-im-tier-b-mining-notes.md)) |

---

## Profile × source class

| Source class | annex3 | iwxxm_us | Primary consumer |
|--------------|--------|----------|------------------|
| ICAO Annex 3 / Doc 8896 | ✅ (paywall) | National differences → FMH-1 / NWS instructions | `tac-validate` |
| WMO 306 Vol I.1 (TAC FM) | ✅ (e-Library) | — | `tac-validate` |
| WMO 306 Vol I.3 / FM 205 | ✅ | extension hook only | `tac2iwxxm` |
| codes.wmo.int | ✅ | + BUFR flags for some US attrs | both encode + validate |
| wmo-im/iwxxm XSD+SCH | ✅ (`…/iwxxm/<pin>/rule/`; **not** top-level [schemas.wmo.int/rule/](https://schemas.wmo.int/rule/) — that index is IWXXM 1.x / foundation mirror only — [dig](../mining/schemas-wmo-int-rule-mining-notes.md)) | base only | `iwxxm-validate` |
| iwxxm-us 3.0 | — | ✅ | `tac2iwxxm` + combined validate |
| FMH-1 / codes.nws.noaa.gov | — | ✅ | US REMARKS / national TAC |
| iwxxm-translation | informative fixtures | examples under us site | golden tests (Amd79-80: METAR/TAF/VAA/TCA only — see [mining/wmo-im-tier-a-mining-notes.md](../mining/wmo-im-tier-a-mining-notes.md)) |
| iwxxm-modelling (UML/EA) | informative provenance for SCH/XSD generation | — | design only — see [notes](../mining/iwxxm-modelling-v2025-2-mining-notes.md) |

---

## codes.wmo.int × product (vocab only)

| Product | Key registers | Normative? | Notes |
|---------|---------------|------------|-------|
| METAR/SPECI | Present/forecast weather, recent weather, cloud amount, CB/TCU, nils | ✅ | Weather concept IDs mostly `306/4678/{TAC}` |
| TAF | Same weather/cloud + nils (NOSIG/NSW) | ✅ | Change-group schedule still Annex 3 prose |
| SIGMET | SigWxPhenomena; MetFeature secondary | ✅ | Outside GIFTs |
| AIRMET | AirWxPhenomena; WeatherCausingVisibilityReduction | ✅ | Prefer 2023-1.4 for D-10 vs AirWx split |
| VAA | `iwxxm/AviationColourCode` + MetFeature VOLCANO/VOLCANIC_ASH | ✅ | Prefer iwxxm/ colour set for 2025-2 |
| TCA | MetFeature `TROPICAL_CYCLONE` + nils | Partial | TAC geometry/template elsewhere |

---

## Official example pairs (wmo-im/iwxxm v2025-2)

| Product | TAC AHL → IWXXM AHL | Root | Example pair (prefix) |
|---------|---------------------|------|------------------------|
| METAR | SA → LA | `iwxxm:METAR` | `metar-A3-1` |
| SPECI | SP → LP | `iwxxm:SPECI` | `speci-A3-2` |
| TAF | FC/FT → LC/LT | `iwxxm:TAF` | `taf-A5-1`, cancel `taf-A5-2` |
| SIGMET | WS → LS | `iwxxm:SIGMET` | `sigmet-A6-1a-TS`, CNL `…-1b-CNL` |
| SIGMET TC | WC → LY | `iwxxm:TropicalCycloneSIGMET` | `sigmet-A6-2-TC` |
| SIGMET VA | WV → LV | `iwxxm:VolcanicAshSIGMET` | `sigmet-VA-EGGX` |
| AIRMET | WA → LW | `iwxxm:AIRMET` | `airmet-A6-1a-TS` |
| VAA | FV → LU | `iwxxm:VolcanicAshAdvisory` | `va-advisory-A7-2` |
| TCA | FK → LK | `iwxxm:TropicalCycloneAdvisory` | `tc-advisory-A2-2` |

Failed convert path: `*-translation-failed.*` → `@translationFailedTAC` quarantine shape.

---

## Consumer routing

| Artifact | tac-validate | tac2iwxxm | iwxxm-validate | UI (#702/#714) |
|----------|--------------|-----------|----------------|----------------|
| Annex 3 / Doc 8896 | primary | thresholds | — | cite |
| codes.wmo.int | vocab | hrefs / nils | RDF check | explain |
| TAC-to-XML-Guidance | nil tokens | **primary encode** | cross-check | explain |
| AWC Data API (informative) | live raw TAC (optional) | — (do not encode-regress) | optional live XML smoke — TAF may be ill-formed; METAR may be COLLECT; engine may skip xslt2 SCH | samples |
| Official examples | golden accept | golden IWXXM | SCH fixtures (when xslt2 path runs) | samples |
| FMH-1 / iwxxm-us | US profile | extensions | combined catalog | US samples |
| PPT-02 Framework (informative) | TAC sunset ~2030; AHL TAC bulletin heading | translation attrs + `translationFailedTAC`; METAR/SIGMET capacity vs TAC; package×line matrix | package versions + ≤2021-2 deprecation messaging | cite |
| OPMET IWXXM Exchange Guidelines 5th (public) | — | Translation Centre; partial translation; `permissibleUsage` | Schematron-by-version / partial % (ROC stats) | cite + bulletin AMHS |
| WIS2 aviation (cookbook/guide/WTH) | — | — (no TAC encode) | — | F8 routing / Annex 3 use-rights; not COLLECT packing |
| Doc 10003 published (paywall) | — | translation-centre metadata / exchange | version/transition prose if present | cite |
| Doc 10003 Advance 2014 draft (historical) | — | IWXXM v1 lineage; weather lists obsolete | 1.0RC2 sample only | lineage notes |
| iwxxm-modelling UML/EA (informative) | — | WithNilReason / extension lineage | SCH **Pattern ID** taxonomy (not runtime SCH path) | cite |
| METCE 1.2 (schemas.wmo.int) | — | TC/VA/VAA/TCA feature encode (`TropicalCyclone` / `Volcano`) | imported XSD (+ optional `metce.sch`) | cite |
| OPM 1.2 (schemas.wmo.int) | — | — (not F6 encode SoT; METCE Process scaffolding only) | transitive XSD via METCE (+ optional `opm.sch`) | cite |
| SAF 1.0–1.1 (schemas.wmo.int) | — | — (**historical**; do not encode `saf:` under 2025-2; use AIXM) | IWXXM 1.x lineage only (`saf.sch`) | lineage |
| TSML 1.0 (schemas.wmo.int mirror of OGC) | — | — (not aviation encode) | — (not on IWXXM validate path) | discovery only |
| GIFTs heritage | gap list only | gap list only | — | — |

---

## METAR / SPECI — F15 research themes (S015 / EV-011)

Hard themes from [metar-research-catalog.md](../../sessions/S015-metar-lint-quality/reports/metar-research-catalog.md)
(E11-23/28). Codes live in [ISSUE_CATALOG.md](./ISSUE_CATALOG.md) / `packages/tac-validate` registry.

| Theme | Lint (F12/F15) | Convert (F6) | Validate / goldens | Status |
|-------|----------------|--------------|--------------------|--------|
| **R1** Station / time / field order | `MISSING_CCCC` / `MISSING_OBS_TIME` / odd-order warnings | Emit CCCC + obs time | — | ✅ closed |
| **R2** Visibility SM / m / fractions / 9999 | `INVALID_VISIBILITY` / `MISSING_VISIBILITY` | Units in IWXXM | XSD units | ✅ closed |
| **R3** Weather phenomena grammar | `INVALID_WEATHER` | wx → IWXXM | SCH where applicable | ✅ closed |
| **R4** Clouds / CAVOK / VV / CB·TCU | `INVALID_CLOUD_TOKEN` / `CLOUD_CB_OR_TCU` | CAVOK → `cloudAndVisibilityOK` | SCH | ✅ closed |
| **R5** US RMK (AO1/AO2/SLP/P/T/PK WND) | `REMARK_US_EXTENSION` / `INVALID_REMARK` | `iwxxm_us` extensions | US schema | ✅ closed |
| **R6** Golden convert + SCH | — | Expanded annex3 + iwxxm_us manifests | M-parse / M-xsd / M-sch / M-golden | ✅ closed |
| **R7** METAR↔SPECI adjacency | Shared pack; no silent cross-product | Same `metarSpeci` path | SPECI goldens + TC-F15-005 | ✅ closed |
| **R8** AUTO / COR / NIL / NOSIG / TEMPO / RVR / VRB·gust | Registry + accept/negative each | AUTO/CAVOK fidelity where fixtures allow | As fixtures allow | ✅ closed |

Non–R-theme gaps (broader aviation nils, full COLLECT packing) remain outside F15 HARD scope.

---

## TAF / SPECI — F20 quality themes (S020 / EV-015)

Hard themes from [taf-speci-research-catalog.md](../../sessions/S020-aerodrome-quality/reports/taf-speci-research-catalog.md)
(E15-13; #735 / #734 exceptional-rule tables + WMO `TAC-to-XML-Guidance.txt` + 2025-2
corrections — no `runwayState`). Paywalled Annex 3 / FMH / FM 205 prose: **cite-only** via
mining notes (see catalog Sources). Codes extend [ISSUE_CATALOG.md](./ISSUE_CATALOG.md) /
ADR-028 registry.

| Theme | Lint (F12/F20) | Convert (F6) | Validate / goldens | Status |
|-------|----------------|--------------|--------------------|--------|
| **T1** TAF NIL / CNL / AMD / COR | Registry + negatives | `reportStatus` / cancel / nil baseForecast | SCH | ✅ lint (M1); convert goldens (M2) |
| **T2** TAF change groups FM/BECMG/TEMPO/PROB + TL/AT | Validity / PROB rules | Ordered `changeForecast` | SCH | ✅ lint (M1); convert deepen open |
| **T3** TAF TX/TN on base only; CAVOK/NSC/NSW/VV/// | Checklist | Guidance exceptional map | XSD/SCH | ✅ lint (M1); CAVOK convert golden |
| **T4** TAF golden convert + SCH | — | Expanded annex3 (+ iwxxm_us) | M-xsd / M-sch / M-golden | ✅ annex3 pack (M2); iwxxm_us deepen open |
| **S1** SPECI exceptional rules (shared METAR/SPECI) | Deepen pack + negatives | `iwxxm:SPECI` root | Existing + expand | ✅ lint deepen (M3 T3.1–T3.2); convert goldens open (S3) |
| **S2** SPECI↔METAR mis-classification | Product hint / Auto-detect | Per-report identity | TC-F20-006 | ✅ guards (MISSING_PRODUCT_KEYWORD + convert mismatch; TC-F20-006) |
| **S3** SPECI golden convert + SCH | — | Expand annex3 / iwxxm_us | M-xsd / M-sch | 🔲 F20 |
| **C1** Common rules (reportStatus, nilReasons, CRS, one-report) | ✅ where TAC tokens (AMD/COR/NIL/NSC + `MULTI_REPORT_BULLETIN`); **convert-only** (lint N/A): 2-D CRS (`srsName`/`srsDimension`/`axisLabels`), `translationFailedTAC`, COLLECT packing, code-list URIs — no TAC surface; catalog §C1 | Guidance common table | Round-trip | ✅ lint (T4.2); convert CRS deepen open |

Deferral of any HARD theme requires AskQuestion + matrix note (E15-5).

---

## Acceptance checklist (#719)

- [x] ≥1 normative or semi-official URL (or explicit paywall/TBD) per F6 product for validation
- [x] Conversion URLs beyond METAR-only GIFTs heritage
- [x] Labels: normative vs informative vs historical-GIFTs
- [x] Cross-links to #698 / #699 in [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md)
- [x] No secrets or scraped copyrighted full-text in-repo
- [x] F15 acc3 — METAR/SPECI rows + R1–R8 closed (S015 / EV-011; see table above)
- [ ] F20 acc — TAF + SPECI themes T1–T4 / S1–S3 / C1 closed or deferred (S020 / EV-015)
