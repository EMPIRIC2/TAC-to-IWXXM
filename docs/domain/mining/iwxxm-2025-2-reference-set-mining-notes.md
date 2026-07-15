# IWXXM 2025-2 validation/conversion reference set — progress tracker

**Status:** working notes (not normative). Tracks the user-supplied reference inventory against repo mining + vendor pin.  
**Focus of this pass:** Product TAC checklists (A3-2/A5-1/A6) + US RMK→iwxxm-us map  
**Date mined:** 2026-07-14 (product checklists continue)  
**Vendor pin:** `vendor/manifest.json` → `iwxxm` **v2025-2** (SHA `35180cbe…`), `iwxxm-codelists` **49-2**, `iwxxm-modelling` **v2025-2**, `iwxxm-translation` **master**, `iwxxm-us` **3.0**

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Rules index | [../rules/README.md](../rules/README.md) |

Legend: ✅ done / catalogued · ⚠ partial / caveat · ❌ gap · ⊘ project-internal (not domain mining)

---

## §1 Authoritative external links

| Resource | Status | Where tracked | Notes (2026-07-14) |
|----------|--------|---------------|-------------------|
| [WMO IWXXM overview](https://community.wmo.int/iwxxm) | ⚠ → ✅ recovered | [Wayback dig](./community-wmo-iwxxm-wayback-mining-notes.md) · catalog | Live **404**; best snapshot [2026-03-14](https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm) (final **2025-2** table, Amd 82). Oct 2025 snapshot still **RC2** / latest→2023-1 — superseded. |
| [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) | ✅ | canonicals + catalog | Prefer vendor SHA over bare `v2025-2` tip |
| [IWXXM releases](https://github.com/wmo-im/iwxxm/releases) | ✅ | catalog | Latest = **`v2025-2`** (published 2025-11-25); Amd 82 |
| [schemas.wmo.int/iwxxm/2025-2/](https://schemas.wmo.int/iwxxm/2025-2/) | ✅ | `IWXXM_VALIDATION.md` | Production package SoT for citations |
| [ReleaseNotes-IWXXM.txt](https://schemas.wmo.int/iwxxm/2025-2/ReleaseNotes-IWXXM.txt) | ✅ | catalog | **Byte-identical** to vendor |
| [codes.wmo.int/iwxxm](https://codes.wmo.int/iwxxm) | ✅ | catalog | Needs `Accept: text/html` |
| [iwxxm-codelists](https://github.com/wmo-im/iwxxm-codelists) | ✅ | Tier A + catalog | Pin by SHA |
| [iwxxm-modelling](https://github.com/wmo-im/iwxxm-modelling) | ✅ | [modelling dig](./iwxxm-modelling-v2025-2-mining-notes.md) | Informative tooling |
| [iwxxm-translation](https://github.com/wmo-im/iwxxm-translation) | ✅ | Tier A + catalog | Informative |
| [ICAO OPMET Guidelines 5th](https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf) | ✅ | [OPMET dig](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) | PDF in `.local/` |
| [AWC Data API](https://aviationweather.gov/data/api/) | ✅ | [AWC dig](./awc-data-api-mining-notes.md) | Informative; smoke caveats below |

---

## §2 Files required for validation (IWXXM 2025-2)

Verified under `vendor/schemas/iwxxm/2025-2/IWXXM/`: `iwxxm.xsd`, `metarSpeci.xsd`, `iwxxm-collect.xsd`, `common.xsd`, `gmliwxxm.xsd`, `rule/iwxxm.sch`, `rule/` RDF — ✅. Compatibility: `2023-1/` retained — do not mix SCH across lines.

---

## §3 Canonical sample pairs

Official pairs + Guidance under `examples/` — ✅. Highest-priority golden corpus.

---

## §4 Project-specific documents

⊘ Architecture SoT (`spec` / `api-contract` / `vendor/manifest.json`) overrides older validation prose.

---

## §5 Input/output file contract

⊘ API/spec — not expanded in domain mining.

---

## §6 Required validation pipeline

| Stage | Status | Notes |
|-------|--------|-------|
| 1–2 TAC lint + convert | ✅ cited | Strategy in `TAC_VALIDATION` / `IWXXM_CONVERSION`; matrix **G1–G2** |
| 3–5 WF + XSD + SCH | ⚠ fixtures ✅ / engine | Strategy + product focus in `IWXXM_VALIDATION`; **pin SCH is `xslt2`** — engine may still skip; release still requires both layers |
| 6 Optional GML/codelist | ✅ cited | offline RDF preferred |
| 7 Golden pairs | ✅ | official examples · matrix **G6** |
| 8 Round-trip IWXXM→TAC | ✅ documented as **out of SoT** | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) · [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |

---

## Strategy supplementation (2026-07-14 continue)

| Artifact | What was added |
|----------|----------------|
| [rules/README.md](../rules/README.md) | Role → strategy routing + `normative-exchange` label |
| [rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) | **G1–G7** pipeline gates |
| [rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) | How-to-apply steps |
| [TAC_VALIDATION.md](../TAC_VALIDATION.md) | OPMET §5.3.2 TAC pre-condition |
| [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) | Quarantine / partial-translation strategy + SWX beyond-F6 pointer |
| [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) | OPMET translator checklist + product validation focus |
| [README.md](../README.md) | Stronger `rules/` / `validation/` / `iwxxm/` strategy pointers |
| [validation/COMPREHENSIVE_VALIDATION.md](../validation/COMPREHENSIVE_VALIDATION.md) | Domain SoT preface; SCH blocking-for-release; vendor paths |
| [validation/FAILURE_TAXONOMY.md](../validation/FAILURE_TAXONOMY.md) | SoT disclaimer |
| [iwxxm/ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) | Validation/conversion strategy table |
| [iwxxm/VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md) | Validate-per-requested-year-line note |

### Prior continue findings (kept)

**Community compatibility table (Wayback)** — live 404; final 2025-2 table recovered.  
**AWC smoke** — do not gate releases; TAF may omit `xmlns:xlink`.  
**Round-trip** — out of domain SoT.

---

## Domain-knowledge cross-check

| Older claim | This pass | Action |
|-------------|-----------|--------|
| Engine SCH “non-blocking” | Domain + OPMET require SCH for release | Caveat engineering docs; keep domain gate |
| Catalog “has URL?” alone | Needed apply-order + gates | G1–G7 + role routing |
| Quarantine encode ad-hoc | Guidelines §5.3.3 min fields | Conversion strategy section |
| Community page live | 404; Wayback final table recovered | Cite Wayback + Appendix A |

---

## Implications for this repo

- **F4:** Appendix A provenance ties to Wayback community table (while live 404)
- **iwxxm-validate:** need xslt2-capable Schematron runner for true §6 / G5 release gate
- **tac2iwxxm:** official examples + Guidance + quarantine strategy
- **Live smoke:** prefer AWC **raw** TAC; AWC IWXXM observational only
- **Docs consumers:** start at hub E2E → canonical strategy → catalog URL → engine wiring last

---

## Suggested next mining passes

1. Re-check live `community.wmo.int/iwxxm` when WMO restores it (**still 404** as of 2026-07-14 continue)
2. When Schematron runner executes `xslt2`, re-smoke official examples (then optional AWC METAR member XML only)
3. Retry `codes.nws.noaa.gov/FMH-1` machine tables; optional AWC REMARKS ↔ FMH-1 §12.7 live cross-walk
4. **Stop** broad reference-set mining — strategy SoT (validate/convert + product checklists) is in the three canonicals + `rules/`; only re-open on a **new vendor pin** or restored community URL

---

## Continue pass — strategy supplementation (2026-07-14 late)

Promoted durable **apply** content from existing digs (no new PDF ingest):

| Artifact | Added |
|----------|-------|
| [TAC_VALIDATION.md](../TAC_VALIDATION.md) | VAA Table A2-1 + TCA Table A2-2 TAC lint checklists; US SPECI FMH §2.5.2.a threshold table |
| [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) | Product encode playbook; VAA colour→registry encode table |
| [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) | “How to validate one document”; golden fixture prefixes per product |
| [rules/README.md](../rules/README.md) | Apply playbooks (TAC / convert / IWXXM / US / bulletin) |
| [rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) | Product × strategy cite table |
| [README.md](../README.md) | Pointers to this continue |
| [validation/IMPLEMENTATION.md](../validation/IMPLEMENTATION.md) · [ENHANCEMENTS.md](../validation/ENHANCEMENTS.md) | Domain SoT prefaces |
| [iwxxm/IWXXM_VERSION_SWITCHING.md](../iwxxm/IWXXM_VERSION_SWITCHING.md) | Domain SoT preface |

### Re-probes (still blocked)

| URL | Result |
|-----|--------|
| `community.wmo.int/iwxxm` (+ `/en/activity-areas/wis/iwxxm`) | **404** |
| `codes.nws.noaa.gov/FMH-1` | **Timeout** |

Reference-set mining for §1–§6 remains **complete**; remaining work is **ops/engine** (xslt2 SCH runner) + optional registry retries — not further broad SoT mining unless a new vendor pin lands.

---

## Continue pass — FMH-1 + App 2 (2026-07-14)

| Source | Result |
|--------|--------|
| Community IWXXM URLs | Still **404** |
| FMH-1 2019 PDF | Extracted → dig [fmh1-2019-mining-notes.md](./fmh1-2019-mining-notes.md); promoted US strategy |
| Annex 3 App 2 | Deeper Tables A2-1/A2-2 shalls → VAA/TCA matrix ✅ |
| AHL short URL | **301** → knowledge-hub AHL page (live) |
| NWS FMH-1 registry | HTTP timeout — catalog caveat |

---

## Continue pass — product TAC checklists + RMK map (2026-07-14)

Promoted from Annex 3 / FMH / iwxxm-us XSD extracts (no new PDF ingest; external probes still 404/timeout):

| Artifact | Added |
|----------|-------|
| [TAC_VALIDATION.md](../TAC_VALIDATION.md) | **A3-2** METAR/SPECI · **A5-1** TAF · **A6** SIGMET/AIRMET TAC lint checklists; **RMK→iwxxm-us** keep-list |
| [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) | Structured `RMK` → iwxxm-us element map (AO1, PK WND, SLP, `$`, …) |
| [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) | Per-product validate playbook (G3–G5) |
| [rules/README.md](../rules/README.md) · [COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) | Playbooks + product strategy cites updated |
| [README.md](../README.md) | Deep-dive table refreshed |
| [validation/FAILURE_TAXONOMY.md](../validation/FAILURE_TAXONOMY.md) | G1–G7 ↔ failure-class map |
| [validation/COMPREHENSIVE_VALIDATION.md](../validation/COMPREHENSIVE_VALIDATION.md) · [IMPLEMENTATION.md](../validation/IMPLEMENTATION.md) | Checklist pointers |
| [iwxxm/ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) · [IWXXM_VERSION_SWITCHING.md](../iwxxm/IWXXM_VERSION_SWITCHING.md) | Strategy deep-link |

### Re-probes (still blocked)

| URL | Result |
|-----|--------|
| `community.wmo.int/iwxxm` (+ `/en/activity-areas/wis/iwxxm`) | **404** |
| `codes.nws.noaa.gov/FMH-1` | **Timeout** |

Reference-set **§1–§6** remain inventoried. Strategy SoT for validate/convert is now in the
three canonicals + `rules/` (playbooks + checklists). Remaining open work is **ops/engine**
(xslt2 SCH runner) + optional registry retries — not further broad SoT mining unless a new
vendor pin or restored community URL lands.
