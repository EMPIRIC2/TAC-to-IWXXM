# ECCC IWXXM-CA — Canada national XML extensions (CA_ECCC)

> **Cycle**: EV-064 / [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916)  
> **Profile**: `CA_ECCC` · **Mined**: 2026-08-22  
> **Companion**: [manobs-manair-ca-mining-notes.md](./manobs-manair-ca-mining-notes.md) (TAC layer)

[Corpus: domain-profiles §CA_ECCC] [Corpus: product §F36]

## Source classification

| Source | Label | Access | Role |
|--------|-------|--------|------|
| [MSC IWXXM datamart readme (EN)](https://eccc-msc.github.io/open-data/msc-data/aviation/iwxxm/readme_aviation-iwxxm-datamart_en/) | normative-exchange | public | Ops products, IWXXM 3.0.0 pin, file naming |
| [MSC IWXXM-CA XSD](https://dd.weather.gc.ca/today/aviation/iwxxm/schema/) | normative-schema | public | `iwxxm-ca.xsd` aggregate + product extensions |
| [MSC code-ca](https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/) | normative-vocabulary | public | Canadian controlled vocabularies |
| [MSC IWXXM doc](https://dd.weather.gc.ca/today/aviation/iwxxm/doc/) | normative-conversion-notes | public | Implementation documentation |
| [MSC operational IWXXM feed](https://dd.meteo.gc.ca/today/aviation/iwxxm/) | normative-examples | public | Live conformance corpus |
| [MANOBS](https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html) | normative | public | METAR/SPECI shall disseminate IWXXM |
| [Transport Canada AIM MET](https://tc.canada.ca/en/corporate-services/acts-regulations/list-regulations/canadian-aviation-regulations.html) | normative | public | Regulatory dissemination context |

## Architecture (defer-to-latest vs app default)

Canada implements **WMO IWXXM 3.0.0** (`http://icao.int/iwxxm/3.0`) plus national extensions — **not**
the app default **2025-2** SoT line ([ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)).

```text
Canadian aviation observation/forecast
         │
         ├── TAC (MANOBS / MANAIR / Annex 3)
         │
         └── IWXXM GML
                 ├── WMO IWXXM 3.0.0 core
                 ├── ECCC *-ca.xsd extensions
                 └── ECCC code-ca vocabularies
```

**Validation stack for CA_ECCC:**

```text
IWXXM document
     ├── Well-formed XML
     ├── WMO IWXXM 3.0.0 XSD + Schematron
     ├── ECCC iwxxm-ca.xsd (national extensions)
     └── code-ca vocabulary membership (semantic)
```

## XSD tree (2026-08-17 pin)

| File | Scope |
|------|-------|
| `iwxxm-ca.xsd` | Aggregate; imports `http://schemas.wmo.int/iwxxm/3.0.0/iwxxm.xsd` |
| `common-ca.xsd` | Shared wx phenomenon types |
| `metar-speci-ca.xsd` | LWIS, SAWR, Addendum, sector visibility, icing, … |
| `taf-ca.xsd` | NonConvectiveLowLevelWindShear, Canadian forecast weather |
| `airmet-ca.xsd` | surfaceVisibility, cloudBase, surfaceWindSpeed, … |

**Vendor pin**: `vendor/manifest.json` → `iwxxm-ca` tag `3.0` · `vendor/schemas/iwxxm-ca/3.0/`  
**Core dependency**: `vendor/schemas/iwxxm/3.0.0/IWXXM/` (wmo-im/iwxxm tag v3.0.0)

### metar-speci-ca highlights (XSD annotations)

| Element | MANOBS / regulatory cite |
|---------|--------------------------|
| `LWIS` | MANOBS 8 Chap 11.3; TC AIM MET 8.5.2 |
| `SAWR` | Surface Aviation Weather Report substitution group |
| `Addendum` | observingSystemType, icing, pressureChangeIndicator, processedQuantity |
| `AerodromeVariableRVR` | Canadian RVR variability |
| `ObservedLightning` | qualitativeDistance + sector |

## code-ca vocabularies (2026-01-27)

| Directory | Example codes |
|-----------|---------------|
| `airmet_weather_phenomena/` | `FRQ_TCU_ISOL_TS`, `FRQ_TCU_ISOL_TSGR`, `OCNL_TCU_ISOL_TS`, `OCNL_TCU_ISOL_TSGR`, `SFC_VIS_and_BKN_CLD`, `SFC_VIS_and_OVC_CLD` |
| `present_and_forecast_weather/` | TAF/METAR national weather defs |
| `sigmet_weather_phenomena/` | SIGMET national phenomena |

Consumer: `iwxxm-validate` semantic checks (future); `tac2iwxxm` encode (M4/M5).

## Operational datamart

**HTTPS pattern:**

```text
https://dd.meteo.gc.ca/today/aviation/iwxxm/{product}/{code_issuer}/{HH}
```

| Product | Path segment | WMO header (examples) |
|---------|--------------|------------------------|
| METAR | `metar` | `A_LACN` |
| SPECI | `speci` | `A_LPCN` |
| TAF | `taf` | `A_LTCN` |
| AIRMET | `airmet` | `A_LWCN` / `A_LWNT` |
| SIGMET | `sigmet` | `A_LSCN-A` / `A_LYCN` / `A_LVCN` |
| VAA | `vaa` | `A_LUCN` |
| QVA | `qvaci` | TBD |

**File naming:** `A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml`

**Distribution:** HTTPS + AMQP (MSC open data). Excellent conformance corpus for paired TAC/IWXXM testing.

**EV-072 M2 harvest (pin_date 2026-08-24):**

- Script: `scripts/iwxxm/harvest_ca_eccc_ops.py` · manifest: `packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/ops_manifest.json`
- Regenerate: `make ca-ops-harvest` (rate-limited; CI uses offline fixtures only)
- At pin_date, MSC datamart publishes TAF/AIRMET/SIGMET IWXXM under COLLECT envelopes; METAR/SPECI paths return 404 — encoder-reference fixtures with manifest waiver

## Product × file matrix

| Product | TAC input artifact | IWXXM output (root / XSD) | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|-------------------|---------------------------|----------------------------|--------------|----------|
| METAR | MANOBS + Annex 3 | `iwxxm:METAR` / `metarSpeci.xsd` + `metar-speci-ca.xsd` | Datamart live XML | LWIS/SAWR/Addendum not in GIFTs | tac2iwxxm, iwxxm-validate |
| SPECI | MANOBS + Annex 3 | same package | Datamart | Canadian RMK grammar | tac2iwxxm, tac-validate |
| TAF | MANAIR 8th Ed. | `iwxxm:TAF` / `taf.xsd` + `taf-ca.xsd` | Datamart | NCLWS / Canadian weather types | tac2iwxxm |
| AIRMET | MANAIR GFA | `iwxxm:AIRMET` / `airmet.xsd` + `airmet-ca.xsd` | Datamart + code-ca | GFA phenomena codes | tac2iwxxm, iwxxm-validate |

## Domain-knowledge cross-check

| Claim | Status | Defer-to-latest |
|-------|--------|-----------------|
| Canada uses IWXXM 3.0.0 (not 2025-2) | ✅ MSC readme | App default 2025-2 ≠ CA ops line |
| Extensions are additive on WMO IWXXM | ✅ `iwxxm-ca.xsd` imports core | — |
| No public ECCC TAC→IWXXM translator API | ✅ (ingredients only) | Build validator from artifacts |
| TAC must be validated before translation | ✅ OPMET Guidelines §5.3 | MANOBS + Annex 3 + MANAIR |
| WMO latest ≠ Canadian operational | ✅ wmo.int 2025-2 vs MSC 3.0.0 | Pin CA profile to 3.0.0 |

## Promotion backlog

| Priority | Rule area | Fixture `rule_id` | Status |
|----------|-----------|-------------------|--------|
| P0 | Vendor `iwxxm-ca` + 3.0.0 core pin | `CA.VENDOR.PIN` | promoted (EV-064 M1) |
| P0 | `ca_eccc` validate profile fail-closed | `CA.VALIDATE.PROFILE` | promoted (EV-064 M2) |
| P0 | Statute-mile visibility (`SM`) | `CA.METAR.VIS.SM` | promoted (M3) |
| P0 | `A####` altimeter | `CA.METAR.ALT.A` | promoted (M3) |
| P1 | LWIS product path | `CA.METAR.LWIS` | promoted (EV-067) |
| P1 | SAWR product path | `CA.METAR.SAWR` | promoted (EV-067) |
| P1 | MANAIR TAF NCLWS | `CA.TAF.NCLWS` | promoted (M4) |
| P2 | GFA AIRMET code-ca phenomena | `CA.AIRMET.GFA` | **in progress** (EV-070 / #1041) |

## Related international sources

| Source | Relevance |
|--------|-----------|
| [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) | Core 3.0.0 XSD + Schematron |
| [wmo-im/iwxxm-translation](https://github.com/wmo-im/iwxxm-translation) | TAC/IWXXM pairs; translation centre metadata |
| [OPMET Guidelines 5th](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) | Validate TAC before translate; translation centre attrs |
| [NCAR crux](https://github.com/NCAR/crux) | Reference XSD+Schematron CLI (informative) |
