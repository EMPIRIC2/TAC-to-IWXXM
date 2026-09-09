# #913 source triage — EV-M1-five-remaining

> **Ticket:** [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913)  
> **Cycle:** EV-M1-five-remaining · **Date:** 2026-09-09  
> **Corpus:** [Corpus: domain-profiles]  
> **Status legend:** `mined` | `redirected` | `dead` | `deferred`

Standing index for the mine ticket’s initial URL list. Durable citations live in
`catalog.yaml` / `RULE_SOURCE_URLS` / `PROVENANCE_MAP`; this table is the closeout AC.

## Per-URL triage

| URL | Status | Profile(s) | Proves | Notes |
|-----|--------|------------|--------|-------|
| https://community.wmo.int/media/news/services-aviation-newsletter-issue-22025-december-2025 | mined | `ICAO_2025` | Annex 3 Amd 82 / PANS-MET / IWXXM 2025-2 context | In `catalog.yaml` |
| https://github.com/wmo-im/iwxxm | mined | `ICAO_2025` | XSD + Schematron upstream | Vendor pin via `vendor/manifest.json` |
| https://github.com/wmo-im/iwxxm-modelling | mined | `ICAO_2025` | Modelling / Schematron prep | Dig: `iwxxm-modelling-v2025-2-mining-notes.md` |
| https://wis.wmo.int/AvXML/AvXML-1.1/EARoot/EA5/EA1/EA126.htm | mined | `ICAO_2025` | METAR/SPECI observation model (CAVOK etc.) | AvXML legacy model reference |
| https://community.wmo.int/site/knowledge-hub/.../ahls-aviation-data-over-icao-afs | mined | `GLOBAL_AFS` | AHL / AFS product designators | Exchange packaging |
| https://www.icao.int/APAC/apac-electronic-documents | mined | `APAC_ROBEX` | APAC OPMET / ROBEX entry | Handbook pin EV-090 |
| https://www.icao.int/APAC/meetingdocs?fid=38396 | mined | `AU_BOM` | AU TAF extensions pointer | Working-paper index |
| https://www.icao.int/2024-met-ie-wg-22-all-documents | mined | `APAC_ROBEX`, nationals | APAC MET IE / national IWXXM status | Meeting bundle |
| https://www.faa.gov/.../part1_gen_section_1.7.html | mined | `US_FAA_NWS` | FAA GEN 1.7 differences | In catalog |
| https://nws.weather.gov/schemas/iwxxm-us/3.0/ | mined | `US_FAA_NWS` | IWXXM-US 3.0 schemas | Vendor `iwxxm-us` pin |
| https://nws.weather.gov/schemas/iwxxm-us/3.0/uml/EARoot/EA3.html | mined | `US_FAA_NWS` | US extensions UML | Model browse |
| https://nws.weather.gov/schemas/iwxxm-us/2.0/uml/.../EA47.html | mined | `US_FAA_NWS` | VariationsInObservedProperties / RMK | Historical 2.0 UML |
| https://nws.weather.gov/schemas/iwxxm-us/3.0/uml/.../EA79.htm | mined | `US_FAA_NWS` | TAF US extension | UML |
| https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/airmets/ | mined | `US_FAA_NWS` | US AIRMET examples | Fixture seed |
| https://nws.weather.gov/schemas/iwxxm-us/2.0/uml/.../EA67.html | mined | `US_FAA_NWS` | USSIGMETSupplement | UML |
| https://forecast.weather.gov/product.php?...&product=SIG&... | mined | `US_FAA_NWS` | Convective SIGMET sample form | Promoted this cycle (example SoT) |
| https://forecast.weather.gov/product.php?...&product=PNS&... | mined | `US_FAA_NWS` | VOR→airport ID transition notes | Promoted this cycle |
| https://www.canada.ca/.../manobs-surface-observations.html | mined | `CA_ECCC` | MANOBS surface obs | Section-level dig → `#1028`/`#1031` |
| https://www.canada.ca/.../manair-...html | mined | `CA_ECCC` | MANAIR aviation forecasts | Same |
| https://www.canada.ca/.../weather-manuals-documentation.html | mined | `CA_ECCC` | Manuals index | Hub |
| https://dd.weather.gc.ca/today/aviation/iwxxm/schema/ | mined | `CA_ECCC` | `iwxxm-ca` XSD tree | Vendor `iwxxm-ca` pin |
| https://eccc-msc.github.io/.../readme_aviation-iwxxm-datamart_fr/ | mined | `CA_ECCC` | Ops IWXXM 3.0.0 + CA extensions | Datamart note |
| https://www.bom.gov.au/aviation/forecasts/international-taf/ | mined | `AU_BOM` | INTER / TAF3 / RMK T/Q | EV-087 |
| https://www.aviation.govt.nz/.../aviation-weather-products/ | mined | `NZ_CAA_MET` | Domestic vs intl TAF; METAR AUTO | EV-087 |
| https://www.caa.co.uk/.../cap-746/ | mined | `UK_METOFFICE` | UK CAP 746 | Thin/compat |
| https://aim-india.aai.aero/eAIP_Archive/19-03-2026/...GEN%203.5... | deferred | `IN_IMD` | India GEN 3.5 | Date-stamped archive — unstable; harden durable pin later (catalog gap) |
| https://amo.kma.go.kr/eng/iwxxm/iwxxm-intro.do | mined | `KR_KMA` | KMA IWXXM program intro | Promoted this cycle |
| https://www.metoffice.gov.uk/sadis/news/1626710838.html | mined | thin / GAMET | SADIS catalogue; GAMET TAC-only note | GAMET spike |

## Mapping (source family → profile → products → dig)

| Source family | Profile id | Products | Dig / rule pointer |
|---------------|------------|----------|--------------------|
| WMO/ICAO baseline | `ICAO_2025` | METAR…VONA | `icao-annex-3-*`, `iwxxm-2025-2-*`, `WMO-306-*` |
| IWXXM-US + FMH-1 + FAA GEN | `US_FAA_NWS` | METAR, SPECI, SIGMET, AIRMET | `fmh1-2019-*`, `iwxxm-us-*` |
| MANOBS/MANAIR + iwxxm-ca | `CA_ECCC` | METAR family, TAF, AIRMET, SIGMET, VAA | `manobs-manair-ca-*`, `eccc-iwxxm-ca-*` (deepen `#1028`/`#1031`) |
| BoM intl TAF | `AU_BOM` | TAF (+ METAR family) | AU mining / stub |
| NZ CAA products | `NZ_CAA_MET` | METAR, TAF | NZ mining / stub |
| CAP 746 | `UK_METOFFICE` | METAR, TAF | UK stub |
| India AIP GEN 3.5 | `IN_IMD` | METAR, SPECI, TAF, SIGMET | `in-imd-tac-mining-notes.md` (URL deferred) |
| KMA IWXXM intro | `KR_KMA` | METAR, SPECI, TAF, SIGMET, AIRMET | `kr-kma-tac-mining-notes.md` |
| APAC ROBEX / EUR RODEX / AFI | exchange overlays | packaging | EV-090 pins; rule matrices deepen residual |
| CAR/SAM regional handbook | `CAR_SAM` | packaging | **deferred gap** — global OPMET guidelines baseline only |
| SADIS / GAMET | GAMET spike | GAMET | `GAMET-spike.md` |

## Gaps (explicit)

| Gap | Disposition |
|-----|-------------|
| `CAR_SAM` region-specific handbook URL | **deferred** — keep on global OPMET IWXXM Exchange Guidelines |
| India / KR / HK AIP GEN 3.5 durable public pin | **deferred** — catalog already lists gap; India archive URL unstable |
| CA MANOBS/MANAIR section-level rule stubs | **out of #913** — `#1028` / `#1031` |
| `community.wmo.int/iwxxm` live page | **dead** (404) — Wayback dig already in PROVENANCE_MAP |
| ROBEX/RODEX full handbook rule matrices | Exchange deepen residual (URLs mined; matrices not #913 AC) |

## Vendor pin recommendations

| Schema | Status |
|--------|--------|
| `iwxxm` 2025-2 | Already pinned in `vendor/manifest.json` |
| `iwxxm-us` 3.0 | Already pinned |
| `iwxxm-ca` (+ WMO 3.0.0 line for CA) | Already pinned; confirm on closeout PR |

## Closeout checklist

- [x] All listed `#913` URLs triaged
- [x] Mapping table present
- [x] Gaps explicit
- [x] Promote newly mined URLs into catalog / RULE_SOURCE_URLS (this PR)
- [x] README Open gaps refreshed
- [ ] Comment + close `#913`; then `#912` epic
