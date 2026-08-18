# EV-061 — Catalog source crawl quality + replacements

> **Session:** S071-pre-promote-ux-catalog · **Cycle:** EV-061 · **Date:** 2026-08-18  
> **Decisions:** `D-S071-links`, `D-S071-links-resolve` (tiers unblock)  
> **Corpus:** [Corpus: product §F15] [Corpus: product §F7.v] [Corpus: decisions §EV-061]  
> Companion: [RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) · crawl report in session `reports/catalog-link-crawl-2026-08-18.md`

## Problem

Automated crawl of provenance / catalog attribution URLs found **11/34 failures**. These are
**source-catalogue / crawl-quality** issues — not a stop on TAC→IWXXM encode/validate engines.
`codes.wmo.int/49-2*` and `common/nil` are often **semantic identifiers** (XML `xlink:href`
vocab), not HTML landing pages that must recursively crawl.

## Policy (locked)

1. **Three tiers** of sources (normative / operational / vocabulary).
2. Operator-visible catalog `source_url` must be a **verified** HTTP 2xx link (or no href).
3. Failed endpoints remain as **legacy aliases / semantic_identifier** text — do not delete history.
4. Do **not** crawl templated URLs (`…/306/4678/{TAC`).
5. IWXXM-US attribution → **NWS published schemas** + `vendor/schemas/iwxxm-us` pin — not
   `github.com/wmo-im/iwxxm-us` (404).

## Verified replacements (2026-08-18 bot check)

| Legacy / failed | Operator-visible replacement (200) | Notes |
|-----------------|--------------------------------------|-------|
| `codes.wmo.int/49-2` (+ children) | https://codes.wmo.int/ui/resources/WMO-Codes-Registry_user-guide-v1.0.pdf | Semantic ID kept in attribution; also https://codes.wmo.int/ |
| `codes.wmo.int/common/nil` | https://github.com/wmo-im/iwxxm/blob/master/IWXXM/ReleaseNotes-IWXXM.txt | nil family documented in release notes; semantic ID retained |
| `community.wmo.int/en/activity-areas/wis/ahl` | https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs | Already SoT in IWXXM_CONVERSION |
| `github.com/wmo-im/iwxxm-us` | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | Also NOAA-MDL modelling repo; vendor pin remains |
| ICAO APAC broken paths | https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf | 3rd Ed FAQ; zh-hans node / old FAQ path left as aliases |
| `weather.gov/.../pd10-13.pdf` | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | Prefer current US schema landing over dead directive PDF |
| `codes.wmo.int/306/4678/{TAC` | *(no crawl)* | Template — semantic only; point humans to registry guide |

### Tier 1 additions (normative / structural)

- https://github.com/wmo-im/iwxxm
- https://github.com/wmo-im/iwxxm/blob/master/IWXXM/ReleaseNotes-IWXXM.txt
- Vendor schemas / Schematron / TAC-to-XML-Guidance (in-repo `vendor/schemas/iwxxm`)

### Tier 2 additions (operational)

- https://www.icao.int/2024-met-ie-wg-22-all-documents
- APAC IWXXM FAQs 3rd Ed (URL above)
- WACAF 2026 workshop PPT (verified 200; long path under icao.int/sites/default/files/WACAF/…)

### Tier 3 (vocabulary)

- https://codes.wmo.int/
- WMO Codes Registry User Guide PDF (above)
- Semantic: `http(s)://codes.wmo.int/49-2/…`, `…/common/nil`, `…/iwxxm/nil`

## Catalog schema expectation (Build)

Operator catalog rows should eventually expose (Spec for #1014):

`source_url` · `canonical_source` · `source_type` (tier1\|2\|3) · `authority` · `status`
(`verified`\|`legacy_alias`\|`semantic_only`) · `last_verified` · `replacement_url` ·
`semantic_identifier`

Until Build, Spec documents the policy; provenance JSON gets **clickable URL swaps** now.

## Out of scope

- Recursively crawling Codes Registry HTML branches
- Replacing vendor pins / encode logic because a registry HTML 404'd
- Treating ChatGPT `utm_source` tracking params as canonical (strip on store)
