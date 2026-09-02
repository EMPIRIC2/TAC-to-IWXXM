# MANOBS / MANAIR — Canada (CA_ECCC) mining notes

> **Cycle**: EV-064 / [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916); **EV-098** / [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029), [#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030)  
> **Profile**: `CA_ECCC` · **Status**: Gate C selective promote **done** 2026-09-02  
> **XML layer**: [eccc-iwxxm-ca-mining-notes.md](./eccc-iwxxm-ca-mining-notes.md)

[Corpus: domain-profiles §CA_ECCC] [Corpus: product §F36] [Corpus: decisions] ev-098

## Standards hierarchy (CA_ECCC)

```text
Level 0 — CAR / MANOBS / MANAIR / Transport Canada AIM (Canadian requirements)
Level 1 — WMO-No. 306 Vol I.1 TAC (METAR/SPECI/TAF/AIRMET templates)
Level 2 — WMO IWXXM 3.0.0 semantic model (Vol I.3 Part D / Doc 10003)
Level 3 — WMO XSD + Schematron (vendored 3.0.0 core)
Level 4 — ECCC *-ca.xsd national extensions
Level 5 — ECCC code-ca controlled vocabularies
Level 6 — Operational datamart XML (conformance corpus)
```

## Sources (catalog triage)

| Source | Edition / pin | URL | Product focus | Label |
|--------|---------------|-----|---------------|-------|
| MANOBS | 8th Ed., Amendment 2, Feb 2023 | https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html | METAR/SPECI + IWXXM shall | normative-national |
| MANOBS PDF | same | https://publications.gc.ca/collections/collection_2023/eccc/En56-238-2-2022-1-eng.pdf | Section-level citations | normative-national-copy |
| MANAIR | **8th Ed., Amendment 15, July 2026** (supersedes prior; effective 2026-07-09) | https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manair-standards-procedures-aviation-weather-forecasts-8th-ed.html | TAF/AIRMET/GFA | normative-national |
| MANAIR PDF | Amd 15 | https://publications.gc.ca/collections/collection_2026/eccc/En58-29-15-2026-eng.pdf | Section-level citations | normative-national-copy |
| MSC IWXXM-CA XSD | tag `3.0` (local `vendor/schemas/iwxxm-ca`) | https://dd.weather.gc.ca/today/aviation/iwxxm/schema/ | Extension elements | normative-schema |
| MSC code-ca | dated archive preferred over `today/` | https://dd.meteo.gc.ca/20260819/WXO-DD/aviation/iwxxm/code-ca/ | Canadian vocabularies | normative-vocabulary |
| MSC IWXXM doc | — | https://dd.weather.gc.ca/today/aviation/iwxxm/doc/ | Implementation notes | normative-conversion-notes |
| MSC datamart readme (EN) | — | https://eccc-msc.github.io/open-data/msc-data/aviation/iwxxm/readme_aviation-iwxxm-datamart_en/ | Ops: IWXXM 3.0.0 + products | normative-exchange |
| Transport Canada AIM | — | https://tc.canada.ca/en/corporate-services/acts-regulations/list-regulations/canadian-aviation-regulations.html | Regulatory dissemination | normative |

**Runtime pin (local evolve branch):** app default `iwxxm` `v2025-2`; `CA_ECCC` uses `iwxxm-ca` tag `3.0` + `iwxxm-3.0.0` compatibility bundle. Public `main` may omit `iwxxm-ca` — do not treat that as profile truth.

## XSD cross-check (2026-08-22; reaffirmed EV-098)

`metar-speci-ca.xsd` documents:

- `LWIS` substitution group on `MeteorologicalAerodromeObservationReport` — MANOBS 8 Chap 11.3; TC AIM MET 8.5.2
- `SAWR` substitution + observing-system taxonomy — **schema-backed**; EV-098/#1029 found **no MANOBS code-form** for SAWR
- National XML: `SectorVisibility`, `VariableVisibility` (§4.5.2 cite), `AerodromeVariableRVR`, `ObservedLightning`, `Addendum` (XML aggregate, not a TAC token)
- Core import: `http://schemas.wmo.int/iwxxm/3.0/iwxxm.xsd` (namespace `http://icao.int/iwxxm/3.0`)

`iwxxm-ca.xsd` aggregates: `common-ca`, `taf-ca`, `airmet-ca`, `metar-speci-ca`.

Direct datamart XSD body fetch may 403; parse **local** `taf-ca.xsd` / `airmet-ca.xsd` for QNames before goldens.

## Section mining backlog (promote → fixture `rule_id`)

| Priority | Section / claim | Fixture product | Status (EV-098 Gate C) |
|----------|-----------------|-----------------|------------------------|
| P0 | §§4.2, 4.5.1, 11.2.2.9 — SM visibility | METAR/SPECI | **promoted** provenance deepen (`CA.METAR.VIS.SM`) |
| P0 | §§9.2, 11.2.2.17 — `A` + four digits | METAR/SPECI | **promoted** deepen (`CA.METAR.ALT.A`); fixture `9999` cleanup **held** |
| P0-adj | `A////` / `CA.METAR.ALT.NOT_OBS` | METAR | **gap / reopened** — do not promote as valid |
| P0 | §11.2.2.4 — `AUTO` | METAR/SPECI | **promoted** deepen (`CA.METAR.AUTO`) |
| P1 | §§9.2.1–9.2.2, 10.2 — PRESRR/PRESFR/SLP | METAR/SPECI | **promoted** deepen |
| P1 | §11.3 + App 4 — LWIS | METAR | **promoted** reaffirm |
| P1 | SAWR | METAR | **promoted** provenance → XSD |
| P1 | §4.5.1.3 — sector visibility | METAR | **promoted** stub (`CA_REMARK_SECTOR_VIS` deepen) |
| P1/P2 | §4.5.2 — variable prevailing VIS | METAR | **promoted** stub (`CA_METAR_VIS_VAR`); fixture **held** |
| P2 | §11.2.2.10.1 — variable RVR | METAR | **promoted** stub (`CA_METAR_RVR_VAR`); fixture **held** |
| P2 | §§6.5.2–6.5.3 — LTG RMK (`CONS`) | METAR | **held** (`CA_METAR_LTG` gap) |
| exchange | §11.1 — dual IWXXM+TAC | METAR/SPECI | **promoted** provenance (`CA_METAR_IWXXM_DUAL`) |
| — | monolithic Addendum | METAR | **held** — do not promote as TAC rule |
| P1 | MANAIR §2.6.9 — NCLWS | TAF | **promoted** deepen (`CA_TAF_NCLWS`) — Amd 15 |
| P1 | MANAIR §2.6.11 — national WX | TAF | **promoted** stub (`CA_TAF_WX_NATIONAL`) |
| P1 | MANAIR §6.8.8 — AIRMET ↔ GFA | AIRMET | **promoted** (`CA_AIRMET_GFA`) |
| P1 | §6.8.3.2 / E.5 — SFC wind / VIS+cloud | AIRMET | **promoted** stubs |
| P1 | E.5 + code-ca members | AIRMET | **promoted** membership (`CA_AIRMET_PHENOMENA_MEMBERSHIP`); goldens **held** |

## EV-098 / #1029 — MANOBS METAR/SPECI deep dig (2026-09-02)

Paraphrase-only; section pointers. Gate B **accepted**.

| MANOBS pointer | CA_ECCC implication | Rule / state |
|---|---|---|
| Foreword; §§1.2–1.3.1 | MSC web copy official; Part A aeronautical standards with Annex 3/MANAIR | provenance |
| §§4.2, 4.5.1, 11.2.2.9 | Land-station VIS in statute miles; TAC uses `SM` | `CA.METAR.VIS.SM` — reaffirm |
| §4.5.1.3 | Sector visibility in Remarks | `CA.METAR.VIS.SECTOR` — pending Gate C |
| §4.5.2 | Variable prevailing VIS (low/high RMK + mean) | `CA.METAR.VIS.VAR` — pending Gate C |
| §§9.2, 11.2.2.17 | Altimeter `A` + four digits (hundredths inHg) | `CA.METAR.ALT.A` — reaffirm |
| §§9.2.1–9.2.2; §10.2 | `PRESRR` / `PRESFR` / `SLPppp` | existing RMK rules — deepen |
| §11.2.2.4 | `AUTO` = automatic observation report (≠ XSD observing-system enum) | `CA.METAR.AUTO` — reaffirm |
| §11.2.2.10.1 | Variable RVR distinct from sector/var VIS | `CA.METAR.RVR.VAR` — pending Gate C |
| §§6.5.2–6.5.3 | LTG RMK frequency/type/direction; Amd 2 uses `CONS` | `CA.METAR.LTG` — pending Gate C |
| §11.3; Appendix 4 | LWIS begins `LWIS` + `AUTO`; subject to Part A | `CA.METAR.LWIS` — reaffirm |
| §11.1 | Disseminate IWXXM in addition to TAC | provenance/exchange |
| (no SAWR match) | SAWR = ECCC schema substitution | `CA.METAR.SAWR` — provenance correction |

### Fixture audit (#1029)

| Case | Issue | Action |
|------|-------|--------|
| `metar_vis_sm` / `metar_auto` | Good P0 positives (`SM` + `A####`) | keep |
| `metar_basic` (`CA.METAR.ALT.A`) | Uses metric-style `9999` VIS | repair to `…SM` under CA_ECCC valid |
| `metar_alt_not_obs` (`A////`) | Conflicts with MANOBS `A`+4 digits + fail-safe QC | reopen / quarantine |
| `metar_rmk_sector_vis` | Exists with golden; not in active manifest | candidate for `VIS.SECTOR` |
| SPECI | Joint METAR/SPECI grammar (§11.2); thin SPECI/valid corpus | backlog |

## EV-098 / #1030 — MANAIR TAF/AIRMET/GFA deep dig (2026-09-02)

**Pin:** Eighth Edition, **Amendment 15**, July 2026 (supersedes earlier amendments including Amd 2).  
**Authority:** §1.1 — incorporated by reference CAR 804.01(1)(b); Canadian differences may supersede Annex 3 RP domestically.

### TAF

| Rule stub | MANAIR | Notes | Gate C |
|-----------|--------|-------|--------|
| `CA.TAF.NCLWS` | §2.6.9 `WShhh/dddffKT` within 1500 ft AGL; no gusts; ≥100 kt → 3 digits | Fixture `taf_nclws` already active; map to `taf-ca` `NonConvectiveLowLevelWindShear` via **local** XSD | deepen provenance |
| `CA.TAF.NCLWS.AMD` | §2.9.5.4 amendment triggers | PDF cross-ref says “2.6.7” but LLWS is §2.6.9 — record defect | deepen note only |
| `CA.TAF.WX.NATIONAL` | §2.6.11 / Table 2 | `SHPL` removed; `SA` only with `BL`/`DR` (Jul 2024) | selective promote |
| Fixture ideas | `WS015/24045KT` valid; `…G55KT` invalid; bare `SA` invalid; `SHPL` invalid | — | hold engine until promote |

### AIRMET / GFA

| Rule stub | MANAIR | code-ca / schema | Gate C |
|-----------|--------|------------------|--------|
| `CA.AIRMET.GFA` | §6.8.8 — AIRMET for hazards **not** already in current GFA; issuance amends GFA | semantic, not XSD-alone | promote provenance |
| `CA.AIRMET.SFC_WIND` | §6.8.3.2; E.5 — widespread mean **>30 KT** | `airmet-ca` `surfaceWindSpeed` (verify local) | promote |
| `CA.AIRMET.SFC_VIS.CLOUD` | VIS **<3 SM** and/or BKN/OVC base **<1000** ft AGL | `surfaceVisibility` + `cloudBase` | promote |
| Phenomena membership | E.5 enumerates allowed mixed TCU/TS | **Observed** only: `FRQ_TCU_ISOL_TS`, `FRQ_TCU_ISOL_TSGR`, `OCNL_TCU_ISOL_TS`, `OCNL_TCU_ISOL_TSGR`, `SFC_VIS_and_BKN_CLD`, `SFC_VIS_and_OVC_CLD` | promote membership rows |
| Invented combos | e.g. `FRQ_TCU_OCNL_TS`, `SFC_VIS_and_SCT_CLD` | **reject** — positive-list only | hold as negatives |

Never invent code-ca URIs; use dated datamart / local vendor snapshot.

## MANOBS regulatory findings (2026-08-22; §11.1 reaffirmed EV-098)

MANOBS requires aerodrome routine and special reports to be disseminated in **IWXXM GML in
addition to** METAR/SPECI coded form. Technical IWXXM specification cites WMO-No. 306 Vol I.3
Part D and ICAO Doc 10003; Canadian aviation requirements flow through MANOBS/MANAIR and CAR.

Transport Canada AIM confirms Canadian METAR/SPECI and TAF are disseminated in IWXXM form.

## TAC validation before translation

Per [OPMET Guidelines 5th](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) §5.3,
translation centres must validate incoming TAC against applicable ICAO Annex 3 / WMO requirements
**before** translating. For CA_ECCC this implies:

```text
TAC → MANOBS/MANAIR + Annex 3 lint → parse → canonical model → IWXXM 3.0.0 + CA extensions
```

## Contradictions (EV-098 Gate B)

| Item | Resolution |
|------|------------|
| `ALT.NOT_OBS` vs MANOBS | **Reopen** — no promote of `A////` as valid without stronger authority |
| `metar_basic` `9999` | Fixture cleanup — keep `ALT.A` rule |
| Sector / var VIS / var RVR | Three rule IDs (not one `RVR.VAR` umbrella) |
| LTG TAC vs `ObservedLightning` | Representation gap — promote TAC separately; gate conversion |
| SAWR | Keep fixture; cite XSD not MANOBS |
| MANAIR Amd 2 vs 15 | **Defer to Amd 15** |
| Public main vs CA pin | Use **local** `vendor/manifest.json` (`iwxxm-ca` 3.0 present) |
| #1041 closed | Evidence/fixtures only — do not reopen engine by default |

## Promotion rule

When a row moves to **promoted** (Gate C), add matching
`packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/<product>/valid/` TAC + golden and update
`manifest.json` with `rule_id` + `status: active` — **or** provenance-only deepen in
`RULE_SOURCE_URLS` / `PROVENANCE_MAP` / canonicals without new goldens when evidence is section-cite only.
