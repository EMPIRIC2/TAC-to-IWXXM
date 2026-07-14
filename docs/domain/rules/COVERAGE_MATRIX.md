# Coverage matrix — F6 product × profile × rule sources

**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Mined:** 2026-07-14  
**Legend:** ✅ normative URL present · ⚠ partial / paywall cite · ❌ blocked / TBD

“Validation” in matrices = TAC token/template/vocab rules (not always full grammar offline).  
“Conversion” = TAC → IWXXM mapping / nilReason / href.  
“IWXXM val” = XSD + Schematron + offline RDF for produced XML.

Profiles: **`annex3`** (ICAO/WMO core) · **`iwxxm_us`** (US national extensions).

---

## Master: product × has URL?

| F6 product | TAC validation URL? | Conversion URL? | IWXXM validation URL? | Gap vs GIFTs |
|------------|---------------------|-----------------|-----------------------|--------------|
| **METAR** | ✅ Annex 3 (paywall) + codes.wmo.int weather/nils; FMH-1 for US | ✅ TAC-to-XML-Guidance + FM 205 + examples | ✅ schemas.wmo.int/2025-2 + SCH | US REMARKS; aviation nils under-used |
| **SPECI** | ✅ same as METAR (+ SPECI criteria in Annex 3) | ✅ same package `metarSpeci.xsd` | ✅ same | same |
| **TAF** | ✅ Annex 3 / Doc 8896 (paywall); vocab via 49-2 / 306 | ✅ Guidance + examples (CNL/NIL/AMD) | ✅ `taf.xsd` + SCH | Outside GIFTs depth |
| **SIGMET** | ✅ Annex 3 (paywall); SigWxPhenomena registry | ✅ Guidance + examples + FM 205 | ✅ `sigmet.xsd` + SCH | **Entire product** outside GIFTs |
| **AIRMET** | ✅ Annex 3; AirWxPhenomena + VIS-cause lists | ✅ Guidance + examples + FM 205 | ✅ `airmet.xsd` + SCH | Entire product outside GIFTs |
| **VAA** | ⚠ Annex 3 / Doc 9766 paywall; colour via registry ✅ | ✅ Guidance + examples + AviationColourCode | ✅ `volcanicAshAdvisory.xsd` | Entire product outside GIFTs |
| **TCA** | ⚠ Annex 3 / regional practice (paywall); MetFeature TC partial | ✅ Guidance + examples + FM 205 | ✅ `tropicalCycloneAdvisory.xsd` | Entire product; template depth TBD beyond examples |
| **Bulletin / AHL** | ✅ WMO AHL page | ✅ AHL T1T2 TAC↔IWXXM | COLLECT / iwxxm-collect | Outside GIFTs |

---

## Profile × source class

| Source class | annex3 | iwxxm_us | Primary consumer |
|--------------|--------|----------|------------------|
| ICAO Annex 3 / Doc 8896 | ✅ (paywall) | National differences → FMH-1 / NWS instructions | `tac-validate` |
| WMO 306 Vol I.1 (TAC FM) | ✅ (e-Library) | — | `tac-validate` |
| WMO 306 Vol I.3 / FM 205 | ✅ | extension hook only | `tac2iwxxm` |
| codes.wmo.int | ✅ | + BUFR flags for some US attrs | both encode + validate |
| wmo-im/iwxxm XSD+SCH | ✅ | base only | `iwxxm-validate` |
| iwxxm-us 3.0 | — | ✅ | `tac2iwxxm` + combined validate |
| FMH-1 / codes.nws.noaa.gov | — | ✅ | US REMARKS / national TAC |
| iwxxm-translation | informative fixtures | examples under us site | golden tests |

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
| Official examples | golden accept | golden IWXXM | SCH fixtures | samples |
| FMH-1 / iwxxm-us | US profile | extensions | combined catalog | US samples |
| PPT-02 Framework (informative) | — | translation attrs / capacity gaps | version deprecation messaging | cite |
| Doc 10003 published (paywall) | — | translation-centre metadata / exchange | version/transition prose if present | cite |
| Doc 10003 Advance 2014 draft (historical) | — | IWXXM v1 lineage; weather lists obsolete | 1.0RC2 sample only | lineage notes |
| GIFTs heritage | gap list only | gap list only | — | — |

---

## Acceptance checklist (#719)

- [x] ≥1 normative or semi-official URL (or explicit paywall/TBD) per F6 product for validation
- [x] Conversion URLs beyond METAR-only GIFTs heritage
- [x] Labels: normative vs informative vs historical-GIFTs
- [x] Cross-links to #698 / #699 in [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md)
- [x] No secrets or scraped copyrighted full-text in-repo
