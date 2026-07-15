# PPT-02 IWXXM Framework (WMO / TT-AvData) — mining notes

**Status:** working notes (not normative). Prefer XSD / FM 205 / Annex 3 for binding claims.  
**Focus of this pass:** full deck (slides 1–19) + **human figure capture** of TAC↔IWXXM details on slides **5, 9, 11, 12, 14, 16, 17** (2026-07-14 refresh).  
**Local PDF + extracts (gitignored):** `.local/reference/ppt-02-iwxxm-framework-wmo/`

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| IWXXM creation | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Version policy | [../iwxxm/VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md) |
| FM 205 notes | [mining/WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) |
| Translation attrs | [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) |

| Item | Value |
|------|-------|
| Title | IWXXM Framework |
| Publisher / speaker | WMO TT-AvData (B.L. Choy); workshop hosted under ICAO ESAF materials |
| Official download | <https://www.icao.int/filebrowser/download/26741?fid=26741> |
| Event | ESAF Virtual Regional Workshop on IWXXM and Annex 3 Amendments |
| Deck date | 22 October 2025 |
| Pages | 19 |
| Local text | `.local/reference/ppt-02-iwxxm-framework-wmo/fulltext.txt` |
| Vendor pin (runtime) | `vendor/manifest.json` → `iwxxm` **v2025-2** |
| Access | public ICAO filebrowser (**Cloudflare challenge** on automated curl); local copy used for extract |
| Label | **informative** (workshop briefing; cites normative landings) |
| Date mined | 2026-07-14 (figure refresh same day) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| 2025 workshop overview of IWXXM status, landings, exchange, and migration messaging | Binding Annex 3 / Doc 10003 / FM 205 text |
| Convenient pointer cluster to WMO + ICAO landings (slides 6–7, 10) | Machine SoT for XSD, Schematron, or nilReason encodings |
| Operator-facing translation & AHL reminders useful for `tac2iwxxm` / bulletin | Product-by-product encode cookbook (use TAC-to-XML-Guidance + examples) |
| Deck snapshot of **package × IWXXM-line × Annex 3** matrix (p.5 / p.16) | Authoritative live compatibility table (prefer community.wmo.int + vendor XSDs) |
| Forward look: 2025-2 ops versions, TAC sunset ~2030, SWIM services | Authority to change this repo’s vendor pin without ADR / release process |

---

## Document map

| Slides | Topic | Approx. PDF pages | Relevance |
|--------|-------|-------------------|-----------|
| 1 | Title / TT-AvData / workshop | 1 | Provenance |
| 2–3 | Standard status; what IWXXM is; exchange vs TAC presentation | 2–3 | F1/F2 framing; UI-decode |
| 4–5 | Package versioning; Annex 3 compatibility table | 4–5 | F4; captured matrix below |
| 6–7 | WMO + ICAO resource locations | 6–7 | Catalog landings |
| 8–9 | Prepare at source; ROC translation attrs (METAR example) | 8–9 | `tac2iwxxm` metadata + TAC failure string |
| 10–12 | AMHS/FTBP + AHL filenames; global AOP IWXXM availability | 10–12 | `bulletin` |
| 13–14 | Consuming/render; IWXXM ≻ TAC content; IWXXM-only products | 13–14 | Conversion gaps; WAFS/QVA |
| 15–17 | Deprecate ≤2021-2; SWIM AMOIS/AMFIS/HWIS; new design figure | 15–17 | Version policy / future |
| 18–19 | Boss messages; TAC sunset ~2030 | 18–19 | Product roadmap only |

---

## Product × artifact matrix (from deck)

| Product | Deck claim | Official SoT to prefer | Gap vs GIFTs | Consumer |
|---------|------------|------------------------|--------------|----------|
| METAR | Can carry **>4 RVRs**; temp to **0.1 °C** (p.14); package **3.2.0** on 2025-2 (p.5/16) | `metarSpeci.xsd` + examples + TAC-to-XML-Guidance | Extra RVR / tenth-degree beyond TAC template | `tac2iwxxm`, UI-decode |
| SPECI | Same package as METAR | same | same | same |
| TAF | Package **3.0.2** on 2025-2 | `taf.xsd` | Outside GIFTs depth for full F6 | encode/validate |
| SIGMET | Polygons may have **>7 points** (p.14); package **4.0.2** on 2025-2 | `sigmet.xsd` + examples | Entire product outside GIFTs | `tac2iwxxm` |
| AIRMET | Package **3.1.2** on 2025-2 | `airmet.xsd` | Outside GIFTs | encode/validate |
| TCA | Package **3.1.1** on 2025-2 | `tropicalCycloneAdvisory.xsd` | Outside GIFTs | encode/validate |
| VAA | Package **3.2.0** on 2025-2 | `volcanicAshAdvisory.xsd` | Outside GIFTs | encode/validate |
| SWX | Package **3.1.0** on 2025-2 | `spaceWxAdvisory.xsd` | Outside GIFTs | encode/validate |
| WAFS SigWx | **IWXXM-only** (no TAC) (p.14); **1.2.0** on 2025-2 | `WAFSSigWxFC.xsd` | N/A (no TAC path) | future / optional |
| QVA (QVACI) | **IWXXM-only** (p.14); **1.0.0** on 2025-2 only | `qvaci.xsd` | N/A | future / optional |
| VONA | **1.0.0** on 2025-2 only (p.5/16) | `vona.xsd` | N/A | future / optional |
| Bulletin | Compressed AMHS FTBP + AHL `T1T2A1A2ii CCCC YYGGgg [BBB]` (p.10–11) | AHL community page | Outside GIFTs | bulletin / F8 |

---

## Key findings

### Status & amendment cycle (p.2–4)

- IWXXM became an ICAO Annex 3 **Standard** with Amendment **79** (Nov 2020) (PDF p.2).
- Schema updates follow Annex 3 and **PANS-MET** amendment cycles (p.2).
- Deck states Amendment **82** + new PANS-MET (Doc **10157**) → IWXXM **2025-2** targeted for publication **Nov 2025** (p.2). Align messaging with local pin `v2025-2` (verify live `schemas.wmo.int` when citing “operational after Nov 2025”).
- From **2021-2**, packages have **independent version numbers**; a **compatibility table** maps IWXXM / package versions to Annex 3 amendments (p.4–5). Landing cited:  
  <https://community.wmo.int/en/activity-areas/wis/iwxxm>

### What IWXXM is vs TAC (p.3)

- XML/GML implementation of Annex 3 SARPs; machine-checkable against schemas.
- Deck framing: IWXXM for **exchange**; TAC still favoured for **presentation** (used for both exchange and presentation) — relevant to UI-decode / F7 (#702/#714), not encode SoT.
- Closing tease: “IWXXM shall win at the end?”

### Compatibility table — full capture (p.5)

Human figure capture (not OCR). **Informative** deck snapshot; confirm against community table + vendored XSD `version=` attrs.

| Package | 1.1 | 2.1 | 3.0 | 2021-2 | 2023-1 | 2025-2 |
|---------|-----|-----|-----|--------|--------|--------|
| METAR and SPECI | 1.1.0 | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | **3.2.0** |
| TAF | 1.1.0 | 2.1.1 | 3.0.0 | 3.0.1 | 3.0.1 | **3.0.2** |
| SIGMET | 1.1.0 | 2.1.1 | 3.0.0 | 4.0.0 | 4.0.1 | **4.0.2** |
| AIRMET | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.1 | **3.1.2** |
| Tropical Cyclone Advisory | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | **3.1.1** |
| Volcanic Ash Advisory | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | **3.2.0** |
| Space Weather Advisory | — | — | 3.0.0 | 3.0.1 | 3.0.1 | **3.1.0** |
| WAFS SIGWX Forecast | — | — | — | 1.0.0 | 1.1.0 | **1.2.0** |
| Quantitative Volcanic Ash Concentration Information | — | — | — | — | — | **1.0.0** |
| Volcano Observatory Notice for Aviation | — | — | — | — | — | **1.0.0** |
| **ICAO Annex 3 Amendment** | **76** | **77** | **78** | **79–80** | **79–81** | **82** |
| **PANS-MET Edition** | — | — | — | — | — | **first** |

**Vendor cross-check (2026-07-14):** `2023-1` and `2025-2` columns match package `version` attrs under `vendor/schemas/iwxxm/{2023-1,2025-2}/IWXXM/` (`qvaci`/`vona` absent in 2023-1 tree). Prefer **vendor pin** over this deck if they ever drift.

### Operational versions after Nov 2025 (p.16)

Subset of the same matrix — **2023-1** and **2025-2** columns only (matches table above). Deck implies both lines are the operational pair after Nov 2025, aligning with this repo’s “latest + 1 prior” window (**2025-2** + **2023-1**).

### WMO resource landings (p.6)

| Landing | URL on slide | Role / label |
|---------|--------------|--------------|
| Manual on Codes Vol I.3 | https://library.wmo.int/idurl/4/35769 | normative (FM 205) |
| Schema artifacts | http://schemas.wmo.int/iwxxm → prefer https://schemas.wmo.int/iwxxm/2025-2/ | normative-schema |
| Code tables | http://codes.wmo.int → https://codes.wmo.int/ | normative-vocabulary |
| Community IWXXM home | https://community.wmo.int/en/activity-areas/wis/iwxxm | informative index + compatibility table |
| TT-AvData list | https://groups.wmo.int/tt-avdata | informative |
| GitHub working space | https://github.com/wmo-im/iwxxm | normative-schema (tag-pin for runtime) |

### ICAO resource landings (p.7)

| Landing | Access | Notes |
|---------|--------|-------|
| IWXXM Guidelines for OPMET Exchange | **public** PDF: [OPMET Guidelines 5th Ed.](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) (mined: [mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)) | Prep + exchange; deck (p.15) says update when 2025-2 is official and **deprecate IWXXM 2021-2 and earlier** — **that deprecation sentence is not in the Oct 2023 5th Edition text** (watch for a later Guidelines edition) |
| ICAO Doc **10003** — Manual on the ICAO Meteorological Information Exchange Model | **paywall** ($) | Structure of IWXXM; [RULE_SOURCE_URLS](../rules/RULE_SOURCE_URLS.md); Advance 2014 draft notes [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) |

### Preparation & translation metadata — TAC→IWXXM (p.8–9)

- Prefer production of IWXXM **at the source**.
- If another State/ROC translates TAC→IWXXM, set translation attributes; if the **producer** translates itself, **do not** set those attributes (p.8).
- Slide 9 METAR example (**captured**) highlights attrs on `iwxxm:METAR` (align names with vendored `common.xsd`):

| Attribute | Example value on slide |
|-----------|------------------------|
| `reportStatus` | `NORMAL` |
| `permissibleUsage` | `OPERATIONAL` |
| `translatedBulletinID` | `TTAAiiCCCYYGGgg` |
| `translatedBulletinReceptionTime` | `2014-05-15T15:29:00Z` |
| `translationCentreDesignator` | `YUZZ` |
| `translationCentreName` | `Fictional translation centre` |
| `translationTime` | `2014-05-15T15:30:00Z` |
| `translationFailedTAC` | **`METAR YUDO 221630Z INVALID`** (TAC string retained on fail) |

Other slide body: aerodrome `YUDO` / DONLON/INTERNATIONAL; issue/observation `2012-08-22T16:30:00Z`. Slide `schemaLocation` shows **2025-2RC2** path — runtime prefer non-RC pin URLs / vendored trees.

### Exchange / AHL — TAC bulletin heading (p.10–12)

- Exchange over **AMHS with FTBP**; compressed attachment; filename follows AHL rules for aviation data over AFS.
- Explicit link: <https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data> (slide 11 cites **v1.0.1**, **11 August 2025**).
- Abbreviated heading format (from WMO-No.386 Part II §2.3.2 as shown):  
  **`T1T2A1A2ii CCCC YYGGgg [BBB]`**
- Slide 12: regional **AOP-aerodrome IWXXM availability** percentages (ops context only — not encode SoT). OCR shows EUR high (~93% METAR-family availability in the deck figure); NAM/SAM low — treat numbers as snapshot, not standing KPIs.

### Consuming & TAC gap widening (p.13–14)

- Consumers need software to **render** IWXXM; TAC often still used for presentation (p.13).
- Content richer than TAC counterparts (p.14):
  - METAR: **>4 RVRs**; temperature to **0.1 °C**
  - SIGMET: polygons **>7 points**
  - New **IWXXM-only** products: WAFS SigWx; QVA Concentration Information
- Mentions a **global repository of IWXXM schema extensions** for national schemas → possible future core inclusion.

### Moving forward / versions / SWIM design (p.15–18)

- After 2025-2 official: Guidelines update to mark **≤2021-2 deprecated** (p.15).
- SWIM information-service names (informative): **AMOIS**, **AMFIS**, **HWIS**; METP WG-MIE visualization + MET-SWIM guidelines (p.15).
- Slide 17 UML (**captured**, forward-looking / SWIM): `MeteorologicalFeatureCollection` 1..\* `MeteorologicalFeature`; enums `ReportStatus` (NORMAL/AMENDMENT/CORRECTION), `PermissibleUsage` (OPERATIONAL/NON-OPERATIONAL), `PermissibleUsageReason` (TEST/EXERCISE), `WMOCategoryCode` (weatherObservations/Forecasts, volcanicObservations/Forecasts). **Not** binding for current F6 TAC→XML cutover — prefer vendored 2025-2 product XSDs.
- Conclusion (p.18): AFS IWXXM uptake lagging; plans for **TAC sunset clauses by ~2030**; new Annex 3 / PANS-MET info will be **IWXXM-only**; prioritize implementation of prep + exchange.

---

## Catalog paste rows

```text
### PPT-02 IWXXM Framework (ESAF workshop, TT-AvData)
- Publisher: WMO TT-AvData (B.L. Choy); ICAO ESAF workshop materials
- URL: https://www.icao.int/filebrowser/download/26741?fid=26741
- Stable concept pattern: n/a (briefing); cites community.wmo.int/…/iwxxm, schemas.wmo.int, codes.wmo.int
- Access: public filebrowser (Cloudflare challenge for bots); local extract under .local/reference/ppt-02-iwxxm-framework-wmo/
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,SWX,WAFS,QVACI,VONA]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin] (overview only)
- Gap vs GIFTs: METAR>4 RVR / 0.1°C; SIGMET>7 vertices; IWXXM-only WAFS/QVA/VONA; translation attrs + translationFailedTAC; AHL/AMHS; package×Annex3 matrix
- Consumer: tac2iwxxm | iwxxm-validate | bulletin | UI-decode
- Label: informative
- Caveats: not SoT for encode/validate; figures p.5/9/11/16/17 now captured in notes — still prefer vendor pin v2025-2 + community table
- Mined: 2026-07-14 · pin v2025-2 · notes mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md
```

---

## Domain-knowledge cross-check

| Older claim | This deck / capture | Action |
|-------------|---------------------|--------|
| Compatibility table TBD / unextracted | Full matrix p.5 + ops subset p.16 | Promote into VERSION_SUPPORT_POLICY as **informative** capture; runtime SoT stays vendor + community |
| OPMET Guidelines 5th lacks ≤2021-2 deprecation | Deck p.15 says Guidelines *will* deprecate after 2025-2 | Keep as future messaging; do not claim 5th Ed. already says it |
| Translation attrs named inconsistently | Slide 9 lists full `common.xsd` attr set incl. `translationFailedTAC` | Prefer vendored `common.xsd`; PPT-02 as operator reminder |
| “Latest + 1 prior” = 2025-2 + 2023-1 | p.16 shows those two as post–Nov 2025 operational columns | Consistent — cite pin + policy; deck is corroboration only |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Keep omit-translation-attrs-when-self-produced rule; quarantine path should populate `translationFailedTAC` with original TAC when translation fails. Do not clamp METAR RVR count / temp precision / SIGMET vertices to TAC presentation limits when schema allows richer content.
- **iwxxm-validate / F4:** Package versions for pin lines are now documented from the deck **and** verified against vendor XSDs — keep validating only the requested line’s Schematron/XSD.
- **bulletin / F8:** AHL template `T1T2A1A2ii CCCC YYGGgg [BBB]` + AMHS FTBP gzip filename story.
- **UI-decode / F7:** Exchange-vs-presentation framing remains **informative**.
- **Promotion:** Done for matrix → VERSION_SUPPORT_POLICY; translationFailedTAC + capacity gaps → IWXXM_CONVERSION; catalog caveats refreshed.

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `extracts/resources-landings.txt` | Slides 6–7, 10 (WMO/ICAO/AHL URLs) |
| `extracts/translation-and-gap.txt` | Slides 8, 14 |
| `extracts/versions-forward.txt` | Slides 2, 4, 15, 18 |
| `extracts/compatibility-table-p05.txt` | Full package×IWXXM matrix (figure capture) |
| `extracts/operational-versions-p16.txt` | 2023-1 / 2025-2 ops subset |
| `extracts/translation-metar-example-p09.txt` | METAR translation attrs + failed TAC |
| `extracts/ahl-bulletin-p11.txt` | AHL `T1T2…` bulletin format |
| `extracts/slide-images/` | Rendered PNGs (local only; not for git) |

---

## Suggested next mining passes

1. ~~Human capture of compatibility table (p.5) and operational versions (p.16)~~ — done 2026-07-14.
2. ~~Locate durable public URL for IWXXM Guidelines for OPMET Exchange~~ — done; see [OPMET notes](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md).
3. When SWIM AMOIS/AMFIS/HWIS publications appear, mine under a separate notes file — out of current F6 TAC→IWXXM cycle unless evolve adds them.
4. Re-mine Guidelines when ICAO publishes a post-2025-2 edition that may add the ≤2021-2 deprecation language from this deck.
5. If community.wmo.int publishes an updated live table that **differs** from this deck snapshot, caveat this note and update VERSION_SUPPORT_POLICY.
