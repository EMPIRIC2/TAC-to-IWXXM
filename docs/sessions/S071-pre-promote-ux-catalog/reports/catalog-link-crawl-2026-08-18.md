# Catalog source URL crawl — 2026-08-18

**Policy:** `D-S071-links` → **`D-S071-links-resolve`** (tiered replacements; semantic IDs OK).  
**Mining note:** [docs/domain/mining/ev061-catalog-source-replacements-2026-08-18.md](../../../domain/mining/ev061-catalog-source-replacements-2026-08-18.md)

## Initial crawl

- Unique URLs: 34
- OK: 23
- FAIL: 11 (listed below — **resolved** for operator-visible hrefs)

## Failures → resolution

| Failed source | Resolution |
|---------------|------------|
| `codes.wmo.int/49-2` + children | Operator href → Codes Registry User Guide PDF; keep concept path as semantic/legacy in attribution |
| `codes.wmo.int/common/nil` | Operator href → IWXXM ReleaseNotes; semantic ID retained |
| `community.wmo.int/en/activity-areas/wis/ahl` | → knowledge-hub AHL aviation AFS page (200) |
| `github.com/wmo-im/iwxxm-us` | → `nws.weather.gov/schemas/iwxxm-us/3.0/` + vendor pin |
| ICAO APAC / meteorology pages | → APAC IWXXM FAQs 3rd Ed PDF / wmo-im/iwxxm (bot-verified) |
| `weather.gov/.../pd10-13.pdf` | → NWS iwxxm-us 3.0 landing |
| `codes.wmo.int/306/4678/{TAC` | Do not crawl templates; registry guide for humans |

## Post-retarget check (`catalog_attribution.json` `source_url`)

- Distinct HTTP `source_url` values: 6 verified 200 + 1 non-HTTP `vendor:…` pseudo-path (not an operator web link)
- **#1014 Spec/Build unblocked** under tier policy (operator links verified; semantic aliases preserved)

## Tier roots to prefer

1. https://github.com/wmo-im/iwxxm  
2. https://github.com/wmo-im/iwxxm/blob/master/IWXXM/ReleaseNotes-IWXXM.txt  
3. https://codes.wmo.int/ui/resources/WMO-Codes-Registry_user-guide-v1.0.pdf  
4. https://codes.wmo.int/  
5. https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-information-system-wis/about-manual-gts/ahls-aviation-data-over-icao-afs  
6. https://nws.weather.gov/schemas/iwxxm-us/3.0/  
7. https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2025-03_IWXXM-FAQs_3rd-Ed.pdf  
8. https://www.icao.int/2024-met-ie-wg-22-all-documents  
