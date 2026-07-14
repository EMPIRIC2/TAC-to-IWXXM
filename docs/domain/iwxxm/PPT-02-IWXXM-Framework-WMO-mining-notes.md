# PPT-02 IWXXM Framework (WMO / TT-AvData) — mining notes

**Status:** working notes (not normative). Prefer XSD / FM 205 / Annex 3 for binding claims.  
**Focus of this pass:** full deck (slides 1–19) — status, resource landings, TAC→IWXXM prep/exchange, version lifecycle, SWIM forward look.  
**Local PDF + extracts (gitignored):** `.local/reference/ppt-02-iwxxm-framework-wmo/`

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| IWXXM creation | [IWXXM_CREATION_SOURCES.md](./IWXXM_CREATION_SOURCES.md) |
| IWXXM validation | [IWXXM_VALIDATION_SOURCES.md](./IWXXM_VALIDATION_SOURCES.md) |
| FM 205 notes | [WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) |
| Translation attrs | [ICAO_OPMET_COMPLIANCE.md](./ICAO_OPMET_COMPLIANCE.md) |

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
| Date mined | 2026-07-14 |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| 2025 workshop overview of IWXXM status, landings, exchange, and migration messaging | Binding Annex 3 / Doc 10003 / FM 205 text |
| Convenient pointer cluster to WMO + ICAO landings (slides 6–7, 10) | Machine SoT for XSD, Schematron, or nilReason encodings |
| Operator-facing translation & AHL reminders useful for `tac2iwxxm` / bulletin | Product-by-product encode cookbook (use TAC-to-XML-Guidance + examples) |
| Forward look: 2025-2 ops versions, TAC sunset ~2030, SWIM services | Authority to change this repo’s vendor pin without ADR / release process |

Image-only slides (**5, 9, 11, 12, 16, 17**) have almost no extractable text — treat captions below as TBD until human review of the PDF figures.

---

## Document map

| Slides | Topic | Approx. PDF pages | Relevance |
|--------|-------|-------------------|-----------|
| 1 | Title / TT-AvData / workshop | 1 | Provenance |
| 2–3 | Standard status; what IWXXM is; exchange vs TAC presentation | 2–3 | F1/F2 framing; UI-decode |
| 4–5 | Package versioning; Annex 3 compatibility table | 4–5 | F4; community table URL |
| 6–7 | WMO + ICAO resource locations | 6–7 | Catalog landings |
| 8–9 | Prepare at source; ROC translation attrs | 8–9 | `tac2iwxxm` metadata |
| 10–12 | AMHS/FTBP + AHL filenames; global AOP IWXXM availability | 10–12 | `bulletin` |
| 13–14 | Consuming/render; IWXXM ≻ TAC content; IWXXM-only products | 13–14 | Conversion gaps; WAFS/QVA |
| 15–17 | Deprecate ≤2021-2; SWIM AMOIS/AMFIS/HWIS; new design figure | 15–17 | Version policy / future |
| 18–19 | Boss messages; TAC sunset ~2030 | 18–19 | Product roadmap only |

---

## Product × artifact matrix (from deck)

| Product | Deck claim | Official SoT to prefer | Gap vs GIFTs | Consumer |
|---------|------------|------------------------|--------------|----------|
| METAR | Can carry **>4 RVRs**; temp to **0.1 °C** (p.14) | `metarSpeci.xsd` + examples + TAC-to-XML-Guidance | Extra RVR / tenth-degree beyond TAC template | `tac2iwxxm`, UI-decode |
| SPECI | Same package story as METAR (implicit) | same | same | same |
| SIGMET | Polygons may have **>7 points** (p.14) | `sigmet.xsd` + examples | Entire product outside GIFTs | `tac2iwxxm` |
| TAF / AIRMET / TCA / VAA | Covered only as “packages” + F6 family context | product XSDs + examples | Outside GIFTs depth | encode/validate |
| WAFS SigWx | **IWXXM-only** (no TAC) (p.14) | `WAFSSigWxFC.xsd` | N/A (no TAC path) | future / optional |
| QVA (QVACI) | **IWXXM-only** (p.14) | `qvaci.xsd` | N/A | future / optional |
| Bulletin | Compressed AMHS FTBP attachment; AHL filename rules (p.10) | AHL community page | Outside GIFTs | bulletin / F8 |

---

## Key findings

### Status & amendment cycle (p.2–4)

- IWXXM became an ICAO Annex 3 **Standard** with Amendment **79** (Nov 2020) (PDF p.2).
- Schema updates follow Annex 3 and **PANS-MET** amendment cycles (p.2).
- Deck states Amendment **82** + new PANS-MET (Doc **10157**) → IWXXM **2025-2** targeted for publication **Nov 2025** (p.2). Align messaging with local pin `v2025-2` (verify live `schemas.wmo.int` when citing “operational after Nov 2025”).
- From **2021-2**, packages have **independent version numbers**; a **compatibility table** maps IWXXM / package versions to Annex 3 amendments (p.4–5). Landing cited:  
  <https://community.wmo.int/en/activity-areas/wis/iwxxm>  
  (same family as VERSION_SUPPORT_POLICY community links; prefer this longer path when the short `/iwxxm` redirect is ambiguous).

### What IWXXM is (p.3)

- XML/GML implementation of Annex 3 SARPs; machine-checkable against schemas.
- Deck framing: IWXXM for **exchange**; TAC still favoured for **presentation** — relevant to UI-decode / F7 (#702/#714), not encode SoT.

### WMO resource landings (p.6)

Paraphrase of the slide pointer list (normalize `http://` → usual https where catalogs already do):

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
| IWXXM Guidelines for OPMET Exchange | public (not fully URL’d on slide) | Prep + exchange; deck (p.15) says update when 2025-2 is official and **deprecate IWXXM 2021-2 and earlier** |
| ICAO Doc **10003** — Manual on the ICAO Meteorological Information Exchange Model | **paywall** ($) | Structure of IWXXM; [RULE_SOURCE_URLS](../rules/RULE_SOURCE_URLS.md); Advance 2014 draft notes [ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) (no §7 / translation attrs in that draft) |

### Preparation & translation metadata (p.8–9)

- Prefer production of IWXXM **at the source**.
- If another State/ROC translates TAC→IWXXM, set translation attributes (deck names): `translatedBulletinID`, `translationCentreName`, etc. (p.8). If the **producer** translates itself, **do not** set those attributes.
- Align field names with in-repo [ICAO_OPMET_COMPLIANCE.md](./ICAO_OPMET_COMPLIANCE.md) / Doc 10003 (`translationCentreDesignator`, `translatedBulletinReceptionTime`, …). Slide 9 figure is image-only — review PDF for attribute list completeness.

### Exchange / AHL (p.10–12)

- Exchange over **AMHS with FTBP**; compressed attachment; filename follows AHL rules for aviation data over AFS.
- Explicit link: <https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data> (already catalogued as **normative-exchange**).
- Slides 11–12 are availability figures (image-only) — global AOP IWXXM availability; ops context only.

### Consuming & TAC gap widening (p.13–14)

- Consumers need software to **render** IWXXM; TAC often still used for presentation (p.13).
- Content richer than TAC counterparts (p.14): METAR RVR count / temperature precision; SIGMET polygon vertex limit; new **IWXXM-only** products (WAFS SigWx, QVA).
- Mentions a **global repository of IWXXM schema extensions** for national schemas → possible future core inclusion (watch TT-AvData / community; do not invent extension SoT here).

### Moving forward / versions (p.15–18)

- After 2025-2 official: Guidelines update to mark **≤2021-2 deprecated** (p.15).
- SWIM information-service names (informative): **AMOIS**, **AMFIS**, **HWIS**; METP WG-MIE visualization + MET-SWIM guidelines (p.15).
- Slides 16–17: “Operational IWXXM versions after Nov 2025” and “new IWXXM design for SWIM” — **figures only**; capture by opening the PDF, do not invent numbers from empty extract.
- Conclusion (p.18): AFS IWXXM uptake lagging; plans for **TAC sunset clauses by ~2030**; new Annex 3 / PANS-MET info will be **IWXXM-only**; prioritize implementation of prep + exchange.

---

## Catalog paste rows

```text
### PPT-02 IWXXM Framework (ESAF workshop, TT-AvData)
- Publisher: WMO TT-AvData (B.L. Choy); ICAO ESAF workshop materials
- URL: https://www.icao.int/filebrowser/download/26741?fid=26741
- Stable concept pattern: n/a (briefing); cites community.wmo.int/…/iwxxm, schemas.wmo.int, codes.wmo.int
- Access: public filebrowser (Cloudflare challenge for bots); local extract under .local/reference/ppt-02-iwxxm-framework-wmo/
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,WAFS,QVACI]; profiles=[annex3]; role=[conversion, iwxxm-validation, bulletin] (overview only)
- Gap vs GIFTs: highlights METAR>4 RVR / 0.1°C; SIGMET>7 vertices; IWXXM-only WAFS/QVA; translation-centre attrs; AHL/AMHS
- Consumer: tac2iwxxm | iwxxm-validate | bulletin | UI-decode
- Label: informative
- Caveats: not SoT for encode/validate; image slides 5/9/11/12/16/17 unextracted; prefer vendor pin v2025-2 over deck publication calendar language
- Mined: 2026-07-14 · pin v2025-2 · notes PPT-02-IWXXM-Framework-WMO-mining-notes.md
```

---

## Implications for this repo

- **F6 / tac2iwxxm:** Reinforce translation-attribute policy (set only for third-party/ROC translation). Treat extra METAR RVR / tenth-degree and SIGMET vertex counts as **schema-capacity** reminders — encode from XSD + examples, not from TAC hard limits alone.
- **iwxxm-validate / F4:** Deck deprecation of ≤2021-2 after 2025-2 aligns with keeping runtime pin on **v2025-2**; do not mix Schematron lines (see IWXXM_VALIDATION_SOURCES).
- **bulletin / F8:** AHL + AMHS FTBP compressed-filename story → keep AHL community URL as exchange SoT.
- **UI-decode / F7:** Exchange-vs-presentation + visualization gap messaging supports operator provenance citations — label **informative**.
- **Caveats / TBD:** OCR or human note of compatibility table (p.5) and operational-versions figure (p.16) if numbers are needed in VERSION_SUPPORT_POLICY.

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `extracts/resources-landings.txt` | Slides 6–7, 10 (WMO/ICAO/AHL URLs) |
| `extracts/translation-and-gap.txt` | Slides 8, 14 |
| `extracts/versions-forward.txt` | Slides 2, 4, 15, 18 |

---

## Suggested next mining passes

1. Human capture of **compatibility table** (p.5) and **operational versions** figure (p.16) into VERSION_SUPPORT_POLICY if not already duplicated on community.wmo.int.
2. Locate durable public URL for **IWXXM Guidelines for OPMET Exchange** (slide 7/15) and promote a catalog row if missing.
3. When SWIM AMOIS/AMFIS/HWIS publications appear, mine under a separate notes file — out of current F6 TAC→IWXXM cycle unless evolve adds them.
