# ECCC MSC IWXXM doc PDFs — mining notes

> **Status:** working notes (not normative / not SoT)  
> **Cycle:** EV-098 / [#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031)  
> **Profile:** `CA_ECCC` · **Accessed:** 2026-09-02 · **Gate B:** accepted  
> **Companion:** [eccc-iwxxm-ca-mining-notes.md](./eccc-iwxxm-ca-mining-notes.md) (datamart / #1028)

[Corpus: domain-profiles §CA_ECCC] [Corpus: product §F36]

**Session return:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-098-ca-eccc-mining/reports/research-return-1031-doc-pdfs.md`

**Promote durable findings into:** `RULE_SOURCE_URLS` · `PROVENANCE_MAP` · `IWXXM_CONVERSION` / `IWXXM_VALIDATION` (exchange notes) — **only after Gate C**.

## What this source is / is not

| Is | Is not |
|----|--------|
| MSC Canadian IWXXM **implementation / encoding guides** under `doc/` | Normative WMO XSD / Schematron |
| Evidence for AIRMET/SIGMET/TAF conversion patterns + code-ca linkage | Full Annex 3 / Manual on Codes prose |
| Corroboration for AHL / filename (with WMO AHL 1.0.1 + datamart readme) | Substitute for `vendor/manifest.json` pin |

## Access / method caveats

- Live `dd.weather.gc.ca/today/aviation/iwxxm/doc/` and direct PDF fetches returned **403** in the research client.
- Dated archive (e.g. 2026-08-19) indexes the same five EN/FR pairs; datamart mtime **2026-05-19**.
- Section catalogue = **search-index-verified anchors** vs **body-anchor pending** — do not invent section numbers at Gate C.
- EN/FR pairs exist; FR body equivalence **not** proven this pass.

## Inventory (unchanged vs #1031)

| File | Version / date (indexed) | Focus | Triage |
|------|--------------------------|-------|--------|
| `Canadian_Code_Registry_1A_En.pdf` (+ FR) | 1A | Code registry catalogue | mined for provenance; section # pending |
| `IWXXM_AIRMET_1A_En.pdf` (+ FR) | 1A · Jan 2026 | AIRMET TAC→IWXXM | **mined** (strongest) |
| `IWXXM_SIGMET_1A_En.pdf` (+ FR) | 1A · Jan 2026 | SIGMET TAC→IWXXM | **mined** |
| `IWXXM_TAF_v2.8_En.pdf` (+ FR) | 2.8 · Feb 2026 | TAF encoding | mined; change-group section # pending |
| `TAC_Bulletins_IWXXM_Files_2A_En.pdf` (+ FR) | 2A | Bulletin / IWXXM file naming | mined for provenance; prefer WMO AHL for grammar |

Stable URL pattern: `https://dd.weather.gc.ca/today/aviation/iwxxm/doc/<file>`  
Archive: `https://dd.meteo.gc.ca/{YYYYMMdd}/WXO-DD/aviation/iwxxm/doc/`

**No METAR / SPECI / VAA-specific implementation PDFs** in inventory — leave gaps visible (do not fill from MANOBS/MANAIR here).

## Verified section anchors

### AIRMET (`IWXXM_AIRMET_1A_En.pdf`)

- §1 Document Information  
- §16 AIRMET Location · §16.3 Polygon · §17 AIRMET Level  
- Canadian extension / Code Registry discussion — **section pending**  
- One AIRMET bulletin per IWXXM file — **section pending** (candidate `CA-ECCC-AIRMET-ONE-BULLETIN-PER-FILE`)  
- Caution: one polygon snippet may mix SIGMET TAC under AIRMET §16.3 index — verify page before product-specific rule

### SIGMET (`IWXXM_SIGMET_1A_En.pdf`)

- §1 Document Information  
- §16 SIGMET Location · §16.3 Polygon · §17 SIGMET Level  
- Extension / Code Registry — **section pending**  
- No dedicated `sigmet-ca.xsd` established — do not invent

### TAF (`IWXXM_TAF_v2.8_En.pdf`)

- §1 Document Information  
- BECMG / TEMPO / PROB + change indicator on change forecasts (not base) — **exact section pending**  
- Candidate `CA-ECCC-TAF-CHANGE-GROUP-MAP` — validate against **3.0.0** pin (do not import 2025-2 semantics blindly)

### Code Registry + bulletin PDF

- Registry PDF: inventory confirmed; **section index pending**  
- Bulletin PDF: “WMO naming convention for IWXXM files” topic; **section # pending** — use [WMO AHL aviation AFS](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs) v1.0.1 for normative grammar

## Product × PDF × mapping

| Product | PDF evidence | Mapping | Candidate stubs | Gate C |
|---------|--------------|---------|-----------------|--------|
| METAR/SPECI | none dedicated | `metar-speci-ca.xsd` + headers `A_LACN`/`A_LPCN` | source topology only | hold semantics |
| TAF | TAF v2.8 | `taf-ca` + change groups | `CA-ECCC-TAF-CHANGE-GROUP-MAP` | hold until section verify |
| AIRMET | AIRMET 1A | `airmet-ca` + `airmet_weather_phenomena/` | LOCATION / LEVEL / PHENOMENON-EXT | highest value — hold until verify |
| SIGMET | SIGMET 1A | core + `sigmet_weather_phenomena/` (no sigmet-ca.xsd proven) | LOCATION / LEVEL / PHENOMENON-EXT | hold |
| VAA | none | header `A_LUCN` only | exchange-only | hold |
| QVACI | none | already gap under 3.0.0 (#1028) | — | no promote |

## code-ca cross-walk

| Family | PDF link | Safe interpretation |
|--------|----------|---------------------|
| `airmet_weather_phenomena/` | AIRMET guide → Canadian registry | Promote values only when schema/instance hrefs observed |
| `sigmet_weather_phenomena/` | SIGMET guide → Canadian registry | Same |
| `present_and_forecast_weather/` | directory exists | Defer METAR/SPECI/TAF semantics until XSD linkage |

**Do not invent code-ca URIs.** Families may not be exhaustive (root index 403).

## Naming reconciliation (corroborates #1028)

- MSC operational pattern ⊆ WMO AHL filename grammar.  
- Interpret `{CCC}` as **CCCC** (readme explanation + `C_CWAO` example + WMO `_C_CCCC_`).  
- Optional WMO `[_ffffff]` / `[.compression]` stay **outside** stricter `CA_ECCC` datamart rule.  
- Product headers vs WMO T1T2: METAR/SPECI/TAF/AIRMET/SIGMET/VAA families consistent; keep MSC table as national source (`CA-ECCC-PRODUCT-AHL`).

## Domain-knowledge cross-check

| Claim | Status | Defer-to-latest |
|-------|--------|-----------------|
| Guides = conversion guidance over schema | ✅ | XSD+SCH + regs win |
| Canada ops on IWXXM 3.0.0 | ✅ MSC readme | Profile pin; app default may be 2025-2 |
| Public `main` lacks `iwxxm-ca` | research-only | **Local evolve/`stage` has pin** — reconcile before semantic promote |
| QVACI from PDFs | ❌ | Keep `CA-ECCC-QVACI-VERSION-GAP` |

## Promotion backlog (pending Gate C)

| Priority | Item | Status |
|----------|------|--------|
| P0 | PDF source URL rows (5 EN landings + archive caveat) → `RULE_SOURCE_URLS` | **promoted** EV-098 / #1031 Gate C |
| P1 | Dig inventory → `PROVENANCE_MAP` | **promoted** EV-098 / #1031 Gate C |
| P1 | AHL/CCCC corroboration (bulletin PDF + WMO AHL) | **promoted** reinforce `CA-ECCC-FILENAME*` |
| P2 | AIRMET/SIGMET/TAF conversion rule stubs | **hold** until direct PDF section verify |
| — | Product conversion fixtures from PDF alone | **hold** |

## Related

- [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028) datamart Gate C  
- [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029) MANOBS · [#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030) MANAIR (next handoffs)
