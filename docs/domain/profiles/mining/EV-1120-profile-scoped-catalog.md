# EV-1120 / #1122 — Profile-scoped catalog mining notes

**Status**: Phase A complete on stage (#1148); deepen pass 2026-09-29 (EV-1121-1122)  
**Session**: `EV-1121-1122-catalog-profile-filters`  
**Corpus**: [Corpus: domain-profiles] · [Corpus: product] F15/F36 · [Corpus: adr/ADR-028]

## Filter semantics (API #1121)

- Omit `semantic_profile` → all rows (unchanged).
- Set → `shared/global ∪ profile-applicable`.
- National-only codes must **not** appear under `ICAO_2025` unless also marked shared.
- Unknown semantic / exchange ids → HTTP 400 (`invalid_semantic_profile` / `invalid_exchange_profile`).
- Provenance: public URLs / citations only; no planning ids in `source_attribution` (EV-048).

## Catalog content (#1122)

| Semantic profile | TAC national-only (examples) | IWXXM-family |
|------------------|------------------------------|--------------|
| `US_FAA_NWS` | `US_TAF_BECMG_FORBIDDEN`, `US_TAF_TEMPO_MAX_4H`, `US_TAF_PROB40_NOT_USED`, `US_METAR_STATUTE_MILE_VIS`, `US_METAR_INHG_ALTIMETER` | `IWXXM_US_EXTENSION`, `IWXXM_US_ADDENDUM_REMARKS` |
| `CA_ECCC` | `CA_METAR_LWIS`, `CA_METAR_UP_AWOS_ONLY`, MANOBS remark family, … | `IWXXM_CA_EXTENSION`, `IWXXM_CA_CODE_REGISTRY` |
| Thin packs | Stub tags OK | Shared IWXXM rows |

## Internet mining pass (2026-09-29)

Public landings consulted (no Annex prose copied into operator templates):

| Source | Landing | Catalog impact |
|--------|---------|----------------|
| FAA AIM meteorology / ICAO weather formats | https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap7_section_1.html | NWS does not use **PROB40** or **BECMG**; US METAR uses **SM** visibility and **A####** inHg altimeter → new US TAC rows |
| NWS TAF directive (PD 10-0813 archive) | weather.gov directives PDF | Confirms TEMPO ≤ 4 h (already `US_TAF_TEMPO_MAX_4H`) |
| NWS IWXXM-US schemas | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | Addendum / METAR+SPECI extension PDF → `IWXXM_US_ADDENDUM_REMARKS` |
| ECCC MANOBS HTML | https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html | **UP** present weather AWOS-only → `CA_METAR_UP_AWOS_ONLY` |
| ECCC IWXXM schema + code-ca | https://dd.weather.gc.ca/today/aviation/iwxxm/schema/ · …/code-ca/ | `IWXXM_CA_EXTENSION` (existing) + `IWXXM_CA_CODE_REGISTRY` |

## Out of this deepen

Full national convert/validate detectors for every new code; thin-pack national mining beyond stubs.

## UI follow (#1123 / #1145)

- #1123 closed via #1302 (Rule catalogs + workbench Profile/Exchange binding; TC-EV1120-009).
- Fail-closed regression locks: TC-EV1120-018.
- #1145 closed: workbench twin retained; Profiles-page AC waived (ADR-044).
- Epic #1120 closed 2026-09-29. Residual: #1149 count/error clarity.
