# MANOBS / MANAIR — Canada (CA_ECCC) mining notes

> **Cycle**: EV-064 / [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916)  
> **Profile**: `CA_ECCC` · **Status**: in progress (parallel to [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913))  
> **XML layer**: [eccc-iwxxm-ca-mining-notes.md](./eccc-iwxxm-ca-mining-notes.md)

[Corpus: domain-profiles §CA_ECCC] [Corpus: product §F36]

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

| Source | URL | Product focus | Label |
|--------|-----|---------------|-------|
| MANOBS 8th Ed. Amd 2 | https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html | METAR/SPECI + IWXXM shall | normative |
| MANAIR 8th Ed. | https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manair-standards-procedures-aviation-weather-forecasts-8th-ed.html | TAF/AIRMET/GFA | normative |
| MSC IWXXM-CA XSD | https://dd.weather.gc.ca/today/aviation/iwxxm/schema/ | Extension elements | normative-schema |
| MSC code-ca | https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/ | Canadian vocabularies | normative-vocabulary |
| MSC IWXXM doc | https://dd.weather.gc.ca/today/aviation/iwxxm/doc/ | Implementation notes | normative-conversion-notes |
| MSC datamart readme (EN) | https://eccc-msc.github.io/open-data/msc-data/aviation/iwxxm/readme_aviation-iwxxm-datamart_en/ | Ops: IWXXM 3.0.0 + products | normative-exchange |
| Transport Canada AIM | https://tc.canada.ca/en/corporate-services/acts-regulations/list-regulations/canadian-aviation-regulations.html | Regulatory dissemination | normative |

## XSD cross-check (2026-08-22)

`metar-speci-ca.xsd` documents:

- `LWIS` substitution group on `MeteorologicalAerodromeObservationReport` — MANOBS 8 Chap 11.3; TC AIM MET 8.5.2
- Core import: `http://schemas.wmo.int/iwxxm/3.0/iwxxm.xsd` (namespace `http://icao.int/iwxxm/3.0`)

`iwxxm-ca.xsd` aggregates: `common-ca`, `taf-ca`, `airmet-ca`, `metar-speci-ca`.

## Section mining backlog (promote → fixture `rule_id`)

| Priority | MANOBS/MANAIR section | Fixture product | Status |
|----------|----------------------|-----------------|--------|
| P0 | SM visibility vs statute miles | METAR | promoted (`CA.METAR.VIS.SM`) |
| P0 | `A####` altimeter coding | METAR/SPECI | promoted (`CA.METAR.ALT.A`, `CA.METAR.ALT.NOT_OBS`) |
| P0 | AUTO / observing system types | METAR | promoted (`CA.METAR.AUTO`) |
| P1 | Canadian RMK grammar (non-US) | METAR/SPECI | promoted (`CA.METAR.RMK.PRESFR`, `CA.METAR.RMK.PRESRR`, `CA.METAR.RMK.SLP_T`) |
| P1 | LWIS product path | METAR | promoted (`CA.METAR.LWIS` / EV-067) |
| P1 | SAWR product path | METAR | promoted (`CA.METAR.SAWR` / EV-067) |
| P1 | MANAIR TAF amendment / national TAF rules | TAF | partial (`CA.TAF.NCLWS`) |
| P2 | GFA AIRMET semantics | AIRMET | pending |

## MANOBS regulatory findings (2026-08-22)

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

## Promotion rule

When a row moves to **promoted**, add matching `packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/<product>/valid/` TAC + golden and update `manifest.json` with `rule_id` + `status: active`.
