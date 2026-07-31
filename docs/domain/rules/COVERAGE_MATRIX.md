# Coverage matrix — F6 product × profile × rule sources

**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · impl [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800) (supersedes #797 backlog)  
**Mined:** 2026-07-30 (APAC FAQs / codes / translation · #797 · WMO-306 I.3 2019/upd-2021 dig **1–272 complete** · #798 · prior EUR Doc 014 · **S031/EV-024** #804/#807/#773)  
**S030 / EV-023 theme map:** [apac-encode-theme-fixture-map.md](../../sessions/S030-apac-encode-validate/reports/apac-encode-theme-fixture-map.md) (TC-EV023-001..009)  
**S031 / EV-024 theme map:** [domain-mine-theme-map.md](../../sessions/S031-iwxxm-domain-mine/reports/domain-mine-theme-map.md) (TC-EV024-001..008) · stem matrix [wmo-im-iwxxm-IWXXM-tree-mining-notes.md](../mining/wmo-im-iwxxm-IWXXM-tree-mining-notes.md)  
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

**Release:** G4 **and** G5 on the document’s year line. AWC / iwxxm-translation = smoke only
(translation suite: TAC→**2025-2** encode + SCH; **no** byte-match to suite **2023-1** XML — #797).  
**IWXXM→TAC round-trip:** not a domain gate (APAC FAQ §8.3: reverse translate not permitted when source TAC exists).

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
| **SPECI** | ✅ same as METAR (+ App 3 §2.3.2 shall / §2.3.3 Rec thresholds) | ✅ same package `metarSpeci.xsd` | ✅ same | **F15** R1–R8 + adjacency closed; **F20 / #734** S1–S3 themes closed (lint deepen + misclass guards + annex3/`iwxxm_us` goldens) — [research catalog](../../sessions/S020-aerodrome-quality/reports/taf-speci-research-catalog.md) · S020/EV-015 |
| **TAF** | ✅ Annex 3 App 5 (§1.3 change/PROB; Table A5-2) / Doc 8896 (paywall); vocab via 49-2 / 306 | ✅ Guidance + examples (CNL/NIL/AMD) | ✅ `taf.xsd` + SCH | **F20 / #735** T1–T4 themes closed (lint + annex3 goldens; residual convert deepen filed below) — [research catalog](../../sessions/S020-aerodrome-quality/reports/taf-speci-research-catalog.md) · S020/EV-015 |
| **SIGMET** | ✅ Annex 3 Ch.7 + App 6 phenomena/validity (paywall); SigWxPhenomena registry; **+** [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) public TAC guide | ✅ Guidance + examples + FM 205 (+ METCE for TC/VA members); EUR Doc 014 AHL `WS`/`WV`/`WC`→`LS`/`LV`/`LY` | ✅ `sigmet.xsd` + SCH (+ METCE 1.2) | **F23 / #733+#739** S025/EV-019 — **G1–G3 / V1–V3 / C1 closed or deferred** (lint + convert + annex3 goldens; residuals below); TC SIGMET #738 OOS |
| **AIRMET** | ✅ Annex 3 Ch.7 + App 6; AirWxPhenomena + VIS-cause lists; **+** [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) | ✅ Guidance + examples + FM 205; EUR Doc 014 AHL `WA`→`LW` | ✅ `airmet.xsd` + SCH | **F24 / #731** S026/EV-020 — WMO `airmet-A6-1a-TS` default golden + registry (in progress) |
| **VAA** | ✅ Annex 3 App 2 §3.1.2 **shall** IWXXM + Table **A2-1** ([dig](../mining/icao-annex-3-mining-notes.md)); Doc 9766 paywall for colour **meanings**; colour machine IDs via registry ✅ | ✅ Guidance + examples + AviationColourCode + [METCE 1.2](https://schemas.wmo.int/metce/1.2/) `Volcano` | ✅ `volcanicAshAdvisory.xsd` (+ METCE embed) | **F26 / #736** S027/EV-021 — **V1–V3/C1 closed** (T2.3–T2.4); inventory [wmo-vaa-tca-examples-inventory.md](../../sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md) |
| **TCA** | ✅ Annex 3 App 2 §5.1.1 (≥34 kt) · §5.1.3 **shall** IWXXM + Table **A2-2** | ✅ Guidance + examples + FM 205 + METCE `TropicalCyclone` | ✅ `tropicalCycloneAdvisory.xsd` (+ METCE embed) | **F27 / #737** S027/EV-021 — T1–T3/C1 (in progress); same inventory |
| **METAR (US)** | ✅ FMH-1 Ch.12 + SPECI §2.5.2 ([dig](../mining/fmh1-2019-mining-notes.md)) + NWS FMH-1 registry | ✅ Body + RMK → iwxxm-us `extension` | ✅ WMO base + iwxxm-us 3.0 | GIFTs stripped REMARKS |
| **Bulletin / AHL** | ✅ WMO AHL page | ✅ AHL T1T2 TAC↔IWXXM + [OPMET Guidelines 5th](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) (`A_…xml.gz`, COLLECT) | COLLECT / iwxxm-collect (vendor `externalSchema`; = `wmo-im/collect` 1.2) | Outside GIFTs; WIS2 path ≠ COLLECT (one resource/notification — [Tier B](../mining/wmo-im-tier-b-mining-notes.md)) |

---

## Profile × source class

| Source class | annex3 | iwxxm_us | Primary consumer |
|--------------|--------|----------|------------------|
| ICAO Annex 3 / Doc 8896 | ✅ (paywall) | National differences → FMH-1 / NWS instructions | `tac-validate` |
| WMO 306 Vol I.1 (TAC FM) | ✅ (e-Library) | — | `tac-validate` |
| WMO 306 Vol I.3 / FM 205 | ✅ ([2023 dig](../mining/WMO-306-vI-3-2023-mining-notes.md); historical [2019/upd-2021](../mining/WMO-306-vI-3-2019-upd-2021-mining-notes.md) **1–272 complete** · #798) | extension hook only | `tac2iwxxm` |
| codes.wmo.int | ✅ | + BUFR flags for some US attrs | both encode + validate |
| wmo-im/iwxxm XSD+SCH | ✅ (`…/iwxxm/<pin>/rule/`; **not** top-level [schemas.wmo.int/rule/](https://schemas.wmo.int/rule/) — that index is IWXXM 1.x / foundation mirror only — [dig](../mining/schemas-wmo-int-rule-mining-notes.md)) | base only | `iwxxm-validate` |
| iwxxm-us 3.0 | — | ✅ | `tac2iwxxm` + combined validate |
| FMH-1 / codes.nws.noaa.gov | — | ✅ | US REMARKS / national TAC |
| iwxxm-translation | informative fixtures | examples under us site | golden tests (Amd79-80-2023: 14 METAR + 20 SPECI under `metar/` + TAF/VAA/TCA; suite IWXXM **2023-1** — [parity dig](../mining/iwxxm-translation-parity-mining-notes.md) · #797) |
| iwxxm-modelling (UML/EA) | informative provenance for SCH/XSD generation | — | design only — see [notes](../mining/iwxxm-modelling-v2025-2-mining-notes.md) |
| ICAO APAC IWXXM FAQs (3rd Ed. Mar 2025) | informative | — | encode/ops gotchas (NSC, `translationFailedTAC`, translationCentre, COLLECT) — [dig](../mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) · #797 |

---

## codes.wmo.int × product (vocab only)

| Product | Key registers | Normative? | Notes |
|---------|---------------|------------|-------|
| METAR/SPECI | Present/forecast weather, recent weather, cloud amount, CB/TCU, nils | ✅ | Weather concept IDs mostly `306/4678/{TAC}` — membership SoT = vendor CSV (**402** stable); live HTML browse ≈101 is incomplete |
| TAF | Same weather/cloud + nils (NOSIG/NSW) | ✅ | Change-group schedule still Annex 3 prose |
| SIGMET | SigWxPhenomena; MetFeature secondary | ✅ | Outside GIFTs |
| AIRMET | AirWxPhenomena; WeatherCausingVisibilityReduction | ✅ | Prefer 2023-1.4 for D-10 vs AirWx split |
| VAA | `iwxxm/AviationColourCode` + MetFeature VOLCANO/**VOLCANIC_ASH** | ✅ | Prefer `iwxxm/` colour (GREEN/YELLOW/ORANGE/RED/**UNASSIGNED**); **`VOLCANIC_ASH` only on `iwxxm/MeteorologicalFeature`** (not `49-2/`) — [codes dig](../mining/codes-wmo-int-aviation-mining-notes.md) |
| TCA | MetFeature `TROPICAL_CYCLONE` + nils | Partial | `TROPICAL_CYCLONE` shared on both MetFeature registers; TAC geometry/template elsewhere |
| All (nil) | `common/nil` **and** `iwxxm/nil` | ✅ | Dual SCH RDF; classic F6 examples prefer `common/nil` — [codes dig](../mining/codes-wmo-int-aviation-mining-notes.md) |

---

## Official example pairs (wmo-im/iwxxm v2025-2)

| Product | TAC AHL → IWXXM AHL | Root | Example pair (prefix) |
|---------|---------------------|------|------------------------|
| METAR | SA → LA | `iwxxm:METAR` | `metar-A3-1` |
| SPECI | SP → LP | `iwxxm:SPECI` | `speci-A3-2` |
| TAF | FC/FT → LC/LT | `iwxxm:TAF` | `taf-A5-1`, cancel `taf-A5-2` |
| SIGMET | WS → LS | `iwxxm:SIGMET` | `sigmet-A6-1a-TS`, CNL `…-1b-CNL` |
| SIGMET TC | WC → LY | `iwxxm:TropicalCycloneSIGMET` | `sigmet-A6-2-TC` |
| SIGMET VA | WV → LV | `iwxxm:VolcanicAshSIGMET` | `sigmet-VA-EGGX` · `sigmet-multi-location-VA` (UI **wmoReference**; convert soft) |
| AIRMET | WA → LW | `iwxxm:AIRMET` | `airmet-A6-1a-TS` |
| VAA | FV → LU | `iwxxm:VolcanicAshAdvisory` | `va-advisory-A7-2` |
| TCA | FK → LK | `iwxxm:TropicalCycloneAdvisory` | `tc-advisory-A2-2` |

Failed convert path: `*-translation-failed.*` → `@translationFailedTAC` quarantine shape.

**Sample-menu tiers (UJ-039 / ADR-032 amend · S031):** `wmoPass` = default-golden equality; `wmoReference` = loadable official TAC (may not equal encoder). Roadmap stems (SWX/VONA/WAFS/QVACI) and TC SIGMET `#738` stay out of happy-path menu (S02.M2).

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
| ICAO APAC IWXXM FAQs 3rd (public, informative) | NSC exclusivity warn | NSC omit layers; `translationFailedTAC`; translationCentre gate; FIR→polygon | NSC co-occurrence SCH smoke | COLLECT multi-version NS hooks (F16–F19; `dissemination.collect_namespaces`) · cite · #800 · [theme map](../../sessions/S030-apac-encode-validate/reports/apac-encode-theme-fixture-map.md) |
| wmo-im/iwxxm `IWXXM/` tree (#804 dig) | Official `.tac` accept | Stem×surface wire; Guidance re-scrape | Pin XSD/SCH + examples | Examples catalog (UJ-039) · [tree dig](../mining/wmo-im-iwxxm-IWXXM-tree-mining-notes.md) |
| IWXXM-US METAR/SPECI.pdf (#773) | US REMARKS types | `iwxxm_us` extension encode gaps → children | Combined catalog | US samples only (not WMO menu) · [PDF dig](../mining/iwxxm-us-metar-speci-pdf-mining-notes.md) |
| WIS2 aviation (cookbook/guide/WTH) | — | — (no TAC encode) | — | F8 routing / Annex 3 use-rights; not COLLECT packing · **#806 OOS** EV-024 |
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
| **T1** TAF NIL / CNL / AMD / COR | Registry + negatives | `reportStatus` / cancel / nil baseForecast | SCH | ✅ closed (lint M1; convert goldens M2) |
| **T2** TAF change groups FM/BECMG/TEMPO/PROB + TL/AT | Validity / PROB rules | Ordered `changeForecast` | SCH | ✅ lint closed (M1); **deferred** convert deepen — no FM/BECMG/TEMPO/PROB golden pack this cycle (follow-on) |
| **T3** TAF TX/TN on base only; CAVOK/NSC/NSW/VV/// | Checklist | Guidance exceptional map | XSD/SCH | ✅ closed (lint M1; CAVOK convert golden M2) |
| **T4** TAF golden convert + SCH | — | Expanded annex3 (+ iwxxm_us) | M-xsd / M-sch / M-golden | ✅ closed annex3 pack (M2) + `taf_us_altimeter` baseline; **deferred** additional `iwxxm_us` TAF cases (follow-on) |
| **S1** SPECI exceptional rules (shared METAR/SPECI) | Deepen pack + negatives | `iwxxm:SPECI` root | Existing + expand | ✅ closed (lint M3 T3.1–T3.2; convert via S3 goldens) |
| **S2** SPECI↔METAR mis-classification | Product hint / Auto-detect | Per-report identity | TC-F20-006 | ✅ closed (MISSING_PRODUCT_KEYWORD + convert mismatch; TC-F20-006) |
| **S3** SPECI golden convert + SCH | — | Expand annex3 / iwxxm_us | M-xsd / M-sch | ✅ closed (annex3 + `iwxxm_us` goldens T3.5–T3.6; TC-F20-003) |
| **C1** Common rules (reportStatus, nilReasons, CRS, one-report) | ✅ where TAC tokens (AMD/COR/NIL/NSC + `MULTI_REPORT_BULLETIN`); **convert-only** (lint N/A): 2-D CRS (`srsName`/`srsDimension`/`axisLabels`), `translationFailedTAC`, COLLECT packing, code-list URIs — no TAC surface; catalog §C1 | Guidance common table | Round-trip | ✅ lint closed (T4.2); **deferred** convert-only CRS / `translationFailedTAC` / COLLECT / code-list URIs (no TAC lint surface) |

HARD themes closed or explicitly deferred above (E15-5). Residual convert deepen (T2 changeForecast goldens; extra T4 `iwxxm_us` TAF; C1 CRS convert) is follow-on — not silent omission.

---

## SIGMET / VA SIGMET — F23 quality themes (S025 / EV-019)

Hard themes from #733 / #739 exceptional-rule tables + WMO `TAC-to-XML-Guidance.txt` +
2025-2 corrections + [EUR Doc 014](../mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md)
(public TAC shape). Paywalled Annex 3 / FM 205 prose: **cite-only** via mining notes.
Research catalog: [`docs/sessions/S025-sigmet-quality/reports/sigmet-research-catalog.md`](../../sessions/S025-sigmet-quality/reports/sigmet-research-catalog.md)
(T0.1 · E19-16). Codes extend [ISSUE_CATALOG.md](./ISSUE_CATALOG.md) / ADR-028 registry.
API: `product=sigmet`; root `iwxxm:SIGMET` vs `iwxxm:VolcanicAshSIGMET` from TAC content
(E19-13=A). TC SIGMET (#738), AIRMET, VAA, TCA OOS this cycle.

> **Naming (D-S025-EV019-s6m1-1)**: Theme ids **G1–G3 / V1–V3 / C1** below are **F23
> themes**, not the pipeline gates **G1–G7** in the table above (G1 TAC lint … G7 Bulletin).
> In execution plans / PRs, write “F23 theme G1” or “gate G1” — never bare `G1` alone.

| Theme | Lint (F12/F23) | Convert (F6.d) | Validate / goldens | Status |
|-------|----------------|----------------|--------------------|--------|
| **G1** General SIGMET exceptional (CNL, point→circle, single alt, STNR, polygon/line CRS) | Registry + accept/negatives (M1) | Exceptional encode (T2.2) | SCH soft-skip platform-wide | ✅ Closed (S025 T2.3 / D-S025-T2.3-A) — residual: `TOP ABV`/`BLW` qualifier encode light; arbitrary polygon heuristics |
| **G2** Sequence / validity / FIR·CTA / phenomenon / movement·intensity | Checklist rules (M1) | Intensity/MOV/STNR in convert | SCH soft-skip | ✅ Closed (S025 T2.3 / D-S025-T2.3-A) — residual: full OBS/FCST analysis-time + forecast-position collections thin |
| **G3** General SIGMET golden convert + SCH | — | annex3 `sigmet_a6_1a_ts` / CNL / STNR | M-xsd / M-sch / M-golden (TC-F23-002) | ✅ Closed (S025 T2.3 / D-S025-T2.3-A) |
| **V1** VA-specific (volcano identity, ash geometry/forecast, `NO VA EXP`, CNL FIR-moved) | Registry + negatives (T3.1–T3.2) | `VolcanicAshSIGMET` fields | SCH soft-skip | ✅ Closed (S025 T3.1–T3.2) |
| **V2** VA SIGMET ↔ general SIGMET ↔ VAA adjacency | Product/root guards (T3.3–T3.4) | Content-selected root under `product=sigmet`; never VAA | TC-F23-006 | ✅ Closed (S025 T3.3–T3.4) |
| **V3** VA SIGMET golden convert + SCH | — | Expand annex3 (`sigmet-VA-EGGX`, …) (T4.1–T4.2) | M-xsd / M-sch / M-golden | ✅ Closed (S025 T4.1–T4.2; TC-F23-003) |
| **C1** Common rules (reportStatus, nilReasons, CRS, one-report, translationFailedTAC) | ✅ where TAC tokens (CNL/STNR/`NO VA EXP`/COR ban + `MULTI_REPORT_BULLETIN`); **convert-only** (lint N/A): 2-D CRS (`srsName`/`srsDimension`/`axisLabels`), `translationFailedTAC`, COLLECT packing, code-list URIs — no TAC surface; catalog §C1 | Guidance common table | Round-trip | ✅ lint closed (T4.4); **deferred** convert-only CRS / `translationFailedTAC` / COLLECT / code-list URIs (no TAC lint surface; F20 C1 pattern) |

HARD themes close or explicitly defer during build (E19-5). Residual convert-only items
without TAC lint surface follow F20 C1 pattern — not silent omission.

---

## Acceptance checklist (#719)

- [x] ≥1 normative or semi-official URL (or explicit paywall/TBD) per F6 product for validation
- [x] Conversion URLs beyond METAR-only GIFTs heritage
- [x] Labels: normative vs informative vs historical-GIFTs
- [x] Cross-links to #698 / #699 in [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md)
- [x] No secrets or scraped copyrighted full-text in-repo
- [x] F15 acc3 — METAR/SPECI rows + R1–R8 closed (S015 / EV-011; see table above)
- [x] F20 acc — TAF + SPECI themes T1–T4 / S1–S3 / C1 closed or deferred (S020 / EV-015; see table above)
- [x] F23 acc — SIGMET + VA SIGMET themes G1–G3 / V1–V3 / C1 closed or deferred (S025 / EV-019)
- [x] F24 acc — AIRMET WMO default golden + registry (S026 / EV-020; #731)
- [x] F25 acc — METAR/SPECI/TAF WMO default goldens + Examples catalog gate (S026 / EV-020)
- [ ] F26 acc — VAA WMO default golden + registry themes V1–V3/C1 (S027 / EV-021; #736)
- [x] F27 acc — TCA WMO default golden + registry themes T1–T3/C1 (S027 / EV-021; #737)

---

## AIRMET — F24 quality themes (S026 / EV-020)

Hard themes from #731 + WMO `TAC-to-XML-Guidance.txt` + vendor `airmet-A6-1a-TS` (defaults only).  
**Research catalog:** [wmo-quality-research-catalog.md](../../sessions/S026-airmet-quality-wmo-examples/reports/wmo-quality-research-catalog.md) (T0.1).

| Theme | Lint | Convert / golden | Validate | Status |
|-------|------|------------------|----------|--------|
| **A1** Header / sequence / validity / FIR | Registry | IR header | — | ✅ Closed (S026 T1.1–T1.2) — sequence/FIR registry + rules |
| **A2** Phenomenon + intensity (ISOL TS, STNR, WKN, …) | Registry | Encode | SCH | ✅ Closed (S026 T1.3–T1.4) — OBS/STNR/WKN/TOP ABV + STNR+MOV / missing OBS·FCST |
| **A3** Geometry + vertical (AirspaceVolume / posList / FL) | — | **M-golden (F23 encoder pattern)** | M-xsd/M-sch | ✅ Closed (S026 T2.1–T2.2) — `airmet-A6-1a-TS` AirspaceVolume/posList/TOP ABV; residuals below |
| **A4** Negatives + translation-failed adjacency | Negatives | Not happy-path | — | ✅ Closed (S026 T2.4) — TC-F24-004 registry codes + translation-failed root guard |
| **C1** Common rules (shared with SIGMET family) | ✅ where TAC | Deferred convert-only per F23 C1 pattern | — | Cite F23 |

**A3 residuals (documented, not deferred themes):** vendor XML labels MWO as `YUDD` while TAC uses `YUSO` — encoder follows TAC; STNR encodes `#731` shared motion nils (vendor omits motion). Golden is encoder-shaped under `canonicalize_xml` (ADR-032 / F23 pattern), not byte-identical vendor UUIDs.

## METAR / SPECI / TAF — F25 WMO official example parity (S026 / EV-020)

**Research catalog:** [wmo-quality-research-catalog.md](../../sessions/S026-airmet-quality-wmo-examples/reports/wmo-quality-research-catalog.md) (T0.1).  
Paywalled Annex 3 / FMH: cite mining notes only — do not copy prose into wheels.

| Theme | Convert / golden (defaults) | UI catalog | Status |
|-------|------------------------------|------------|--------|
| **W1** `metar-A3-1` | `canonicalize_xml` == vendor | Include when green | **Closed** (S026 T3.1–T3.2) |
| **W2** `speci-A3-2` | same | Include when green | **Closed** (S026 T3.1–T3.2) |
| **W3** `taf-A5-1` + `taf-A5-2` | same | Include when green | **Closed** (S026 T4.1–T4.3; E20-E1) |
| **W4** Examples gate | — | Only WMO-passers for in-scope products | **Closed** (S026 T5.3–T5.4; E20-F4) |

---

## VAA — F26 quality themes (S027 / EV-021)

Hard themes from #736 + WMO `TAC-to-XML-Guidance.txt` §Volcanic Ash Advisory + vendor
`va-advisory-A7-2` (defaults only). Mine TAC themes from
`iwxxm-translation` Amd79-80-2023; **no** Amd79 XML byte-match under 2025-2 (E21-D4).  
**Inventory:** [wmo-vaa-tca-examples-inventory.md](../../sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md).  
**Theme→fixture map (T0.1):** [vaa-tca-theme-fixture-map.md](../../sessions/S027-vaa-quality/reports/vaa-tca-theme-fixture-map.md).

> **Naming (`D-S027-EV021-s02m1-1`)**: Theme ids **V1–V3 / C1** below are **F26 themes**.
> F23 also used **V1–V3** for VA *SIGMET* — always write “F26 theme V1” vs “F23 theme V1”
> in plans/PRs (do not rename to A1–A3).

| Theme | Lint (F12/F26) | Convert (F6.f) | Validate / goldens | Status |
|-------|----------------|----------------|--------------------|--------|
| **V1** VAA exceptional (UNKNOWN/UNNAMED, OBS/FCST status, nilReasons, remarks NIL, `NO FURTHER ADVISORIES`) | Registry + accept/negatives (T1.1–T1.2) | Exceptional encode | SCH soft-skip platform-wide | ✅ Closed (S027 T1.1–T1.2; T2.3) |
| **V2** VAA ↔ VA SIGMET adjacency | Product/root guards (T1.3–T1.4) | Never emit `VolcanicAshSIGMET` under `product=vaa` | TC-F26-006 | ✅ Closed (S027 T1.3–T1.4; T2.3) |
| **V3** VAA golden convert + SCH | — | `va-advisory-A7-2` defaults `canonicalize_xml` (T2.1–T2.2) | M-xsd / M-sch / M-golden (TC-F26-002/003) | ✅ Closed (S027 T2.1–T2.2; T2.3) |
| **C1** Common rules | ✅ where TAC (V1 negatives) | Shared with F23 C1 pattern | translation-failed not happy-path (TC-F26-004) | ✅ Closed (S027 T2.4) |

## TCA — F27 quality themes (S027 / EV-021)

Hard themes from #737 + guidance §Tropical Cyclone Advisory + vendor `tc-advisory-A2-2`
(defaults only). Same translation-package mine policy (E21-D4).  
**Theme→fixture map (T0.1):** [vaa-tca-theme-fixture-map.md](../../sessions/S027-vaa-quality/reports/vaa-tca-theme-fixture-map.md).

> **Naming (`D-S027-EV021-s02m1-1`)**: Theme ids **T1–T3 / C1** below are **F27 themes** —
> always write “F27 theme T1” in plans/PRs.

| Theme | Lint (F12/F27) | Convert (F6.f) | Validate / goldens | Status |
|-------|----------------|----------------|--------------------|--------|
| **T1** TCA exceptional (`UNNAMED`, CB NIL, remarks NIL, `NO MSG EXP`, wind &lt;34 kt, no-longer-TC) | Registry + accept/negatives (T3.1–T3.2) | Exceptional encode | SCH soft-skip | ✅ Closed (S027 T3.1–T3.2) |
| **T2** TCA ↔ TC SIGMET adjacency | Product/root guards (T3.3–T3.4) | Never emit `TropicalCycloneSIGMET` under `product=tca` | TC-F27-006 | ✅ Closed (S027 T3.3–T3.4) |
| **T3** TCA golden convert + SCH | — | `tc-advisory-A2-2` defaults `canonicalize_xml` (T4.1–T4.2) | M-xsd / M-sch / M-golden (TC-F27-002/003) | ✅ Closed (S027 T4.1–T4.2; T4.3) |
| **C1** Common rules | ✅ where TAC | Shared pattern | translation-failed not happy-path (TC-F27-004) | ✅ Closed (S027 T4.4) |

---

## Domain mine durable promotions — S031 / EV-024 (#804 / #807 / #773)

Discovery-first cycle: mine → promote durable rows → wire sample menu / validate → **child issues** for encode (no big-bang). Theme map: [domain-mine-theme-map.md](../../sessions/S031-iwxxm-domain-mine/reports/domain-mine-theme-map.md). Guidance/SCH gap inventory: [guidance-sch-assert-gap-list.md](../../sessions/S031-iwxxm-domain-mine/reports/guidance-sch-assert-gap-list.md).

| Durable finding | Promoted to | Status |
|-----------------|-------------|--------|
| Pin `IWXXM/` folder×relevancy + stem×surface (V/C/U/D) | [tree dig](../mining/wmo-im-iwxxm-IWXXM-tree-mining-notes.md) · example table above · UJ-039 catalog | ✅ M1 |
| Org / sibling refresh; explicit #806 WIS2 skip | [org dig](../mining/wmo-im-org-mining-notes.md) | ✅ M2 |
| US METAR/SPECI.pdf + modelling + VLab URL rows | [RULE_SOURCE_URLS §5](./RULE_SOURCE_URLS.md) · [PDF dig](../mining/iwxxm-us-metar-speci-pdf-mining-notes.md) | ✅ M3 |
| `wmoReference` catalog tier + VA EGGX / multi-location menu | ADR-032 amend · `examplesCatalog.ts` · FIXTURE_GAPS | ✅ M5 |
| In-scope stems on validate CI (XML well-formed/XSD/GML) | `test_wmo_canonical_examples` + loader inventory (M6) | ✅ / wire |
| Multi-location VA **convert** equality | [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809) — menu stays **reference** | ⚠ → #809 |
| TC SIGMET A6-2 menu / encode bar | Existing #738 | ⚠ deferred |
| SWX / VONA / WAFS / QVACI sample menu | Existing #740 / #741 + S02.M2 | ❌ roadmap |
| US Variable RVR / Lightning / SnowIncrease+sensors | [#810](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/810) · [#811](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/811) · [#812](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/812) | #810/#811/#812 ✅ encode (S032 T1–T3) |
| Guidance topic ↔ SCH assert ↔ lint map residuals | Gap list → #809 + #800 survivors | ⚠ → children |

### METAR (US) — #773 type checklist (durable summary)

Full type×TAC×encode×validate table lives in the [PDF dig](../mining/iwxxm-us-metar-speci-pdf-mining-notes.md). Matrix status for planning:

| Cluster | Encode | Validate | Fixture | Child focus |
|---------|--------|----------|---------|-------------|
| Addendum / AO2 / SLP / PK WND | ⚠ partial | ⚠ | ⚠ | F15 deepen continue |
| Variable RVR | ✅ S032/#810 | ⚠ | ✅ TC-EV025-001 | Validate smoke M6 |
| Wind shift / FROPA | ✅ S032/M4.1 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| Lightning / VisuallyObservablePhenomena | ✅ S032/#811+#M4.2+#M4.3 | ⚠ | ✅ TC-EV025-002/004 | Validate smoke M6 |
| Sky / convective / hail | ✅ S032/M4.2 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| SnowIncrease / sensor outage | ✅ S032/#812 | ⚠ | ✅ TC-EV025-003 | Validate smoke M6 |
| Sector / obscuration / second-site / tower | ✅ S032/M4.3 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| Variable CIG / SKY / VIS | ✅ S032/M4.4 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| MaxMin / precip ProcessedProperty / AO hrefs | ✅ S032/M4.5 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| Addendum residuals / RecentWeather | ✅ S032/M4.6 | ⚠ | ✅ TC-EV025-004 | Validate smoke M6 |
| Codelist hrefs (NWS) | ✅ S032/M4.5 (AO + statistical) | ⚠ | ✅ TC-EV025-004 | Prefer codes.nws.noaa.gov |

Do **not** mix US examples into the WMO sample menu (UJ-039 / E24-C).
