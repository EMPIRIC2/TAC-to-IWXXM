# IWXXM validation — schema & Schematron sources

**Purpose:** Pointer catalog for **validating produced IWXXM XML** (XSD + Schematron + codelist RDF).  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699).  
**Does not** re-litigate packaging design — cite official landings + vendor pins only.

Runtime engine: `packages/iwxxm-validate` · HTTP wrapper in `apps/backend`.  
Layered architecture notes: [COMPREHENSIVE_VALIDATION.md](../validation/COMPREHENSIVE_VALIDATION.md).

---

## Pin vs publish URL

| Item | Value |
|------|-------|
| Vendor pin | `vendor/manifest.json` → bundle `iwxxm` tag **`v2025-2`** |
| Commit (example at last mine) | `35180cbe3bec0bc536a78714dd78d2e7ba60931f` |
| Local path | `vendor/schemas/iwxxm` |
| Canonical publish | https://schemas.wmo.int/iwxxm/2025-2/ |
| Source repo | https://github.com/wmo-im/iwxxm/tree/v2025-2 |
| XML namespace | `http://icao.int/iwxxm/2025-2` |

Always validate against the **vendored** tree in CI; use schemas.wmo.int for citations and upgrade discovery.

FM 205-2023-1 in WMO-No. 306 Vol I.3 still indexes many tables to the **2023-1** package — treat that as historical lineage; **do not** mix 2023-1 Schematron with 2025-2 XML.

---

## Core machine artifacts

| Artifact | Official URL (2025-2) | Vendor path |
|----------|----------------------|-------------|
| Aggregate XSD | https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd | `IWXXM/iwxxm.xsd` |
| Schematron | https://schemas.wmo.int/iwxxm/2025-2/rule/iwxxm.sch | `IWXXM/rule/iwxxm.sch` |
| Codelist RDF snapshots | (with Schematron package) | `IWXXM/rule/codes.wmo.int-*.rdf` |
| Examples (fixtures) | https://schemas.wmo.int/iwxxm/2025-2/examples/ | `IWXXM/examples/` |

### Product XSDs

| Product | XSD URL suffix under `/iwxxm/2025-2/` |
|---------|----------------------------------------|
| METAR/SPECI | `metarSpeci.xsd` |
| TAF | `taf.xsd` |
| SIGMET (+ TC/VA) | `sigmet.xsd` |
| AIRMET | `airmet.xsd` |
| TCA | `tropicalCycloneAdvisory.xsd` |
| VAA | `volcanicAshAdvisory.xsd` |
| Common | `common.xsd` |
| Collect / bulletin | COLLECT + `iwxxm-collect.xsd` (see examples) |

Non-F6 but present: `spaceWxAdvisory.xsd`, `WAFSSigWxFC.xsd`, `vona.xsd`, `qvaci.xsd`, `metFeature.xsd`.

---

## Sibling vendor bundles

| Bundle | Tag | Upstream | Role in validation |
|--------|-----|----------|--------------------|
| `iwxxm-codelists` | `49-2` | https://github.com/wmo-im/iwxxm-codelists | Codelist RDF SoT |
| `iwxxm-modelling` | `v2025-2` | https://github.com/wmo-im/iwxxm-modelling | UML / generation (not runtime) |
| `iwxxm-translation` | `master` pin | https://github.com/wmo-im/iwxxm-translation | Extra fixtures — **informative** |
| `iwxxm-us` | `3.0` | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | Combined WMO+US catalogs when profile = US |

US landing: https://nws.weather.gov/schemas/iwxxm-us/  
Examples: https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/

---

## Live vocabulary (optional online checks)

Prefer offline RDF in CI; optional live:

| Register | URL |
|----------|-----|
| Root | https://codes.wmo.int/ |
| IWXXM lists | https://codes.wmo.int/iwxxm |
| Nil | https://codes.wmo.int/common/nil |
| Weather / phenomena | https://codes.wmo.int/49-2/… |

Community index: https://community.wmo.int/en/activity-areas/wis/iwxxm (compatibility table / amendment↔package map).  
Informative workshop overview (2025-10 TT-AvData): [PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) — deck messaging that **IWXXM 2021-2 and earlier** are to be deprecated in OPMET Guidelines once **2025-2** is official; still validate runtime XML only against the **vendored** pin.

---

## Validation fixture strategy

| Fixture type | Source | Assert |
|--------------|--------|--------|
| Success pairs | Official `*.xml` under examples/ | XSD + Schematron pass |
| Translation-failed | `*-translation-failed*.xml` | SCH min-field / quarantine attributes |
| US documents | iwxxm-us examples | Combined catalogs |
| Informative extras | iwxxm-translation | Non-blocking regression |

---

## What IWXXM validation does *not* cover

| Gap | Use instead |
|-----|-------------|
| TAC syntax before convert | [ANNEX3_TAC_VALIDATION_SOURCES.md](../validation/ANNEX3_TAC_VALIDATION_SOURCES.md) · `tac-validate` |
| Encode mapping correctness | [IWXXM_CREATION_SOURCES.md](./IWXXM_CREATION_SOURCES.md) golden TAC↔XML |
| Annex 3 observing obligations | ICAO Annex 3 (paywall) |

---

## Catalog paste rows (#699 pointer-only)

```text
### IWXXM XSD + Schematron releases
- Publisher: WMO TT-AvXML
- URL: https://schemas.wmo.int/iwxxm/2025-2/ (+ GitHub wmo-im/iwxxm tag v2025-2)
- Access: public
- Applies to: all F6 IWXXM outputs; profile annex3 (+ iwxxm-us overlay)
- Role: iwxxm-validation
- Consumer: iwxxm-validate
- Label: normative-schema
- Caveats: pin via vendor/manifest.json; do not mix line versions

### Offline codelist RDF
- Publisher: WMO (bundled with IWXXM / iwxxm-codelists)
- URL: https://codes.wmo.int/ (live); vendor IWXXM/rule/*.rdf (offline)
- Role: WMO_CODELISTS layer
- Label: normative-vocabulary
```

---

## Related

- Layer implementation: [COMPREHENSIVE_VALIDATION.md](../validation/COMPREHENSIVE_VALIDATION.md)
- Schematron deploy notes: [SCHEMATRON_RENDER_CHANGES.md](../validation/SCHEMATRON_RENDER_CHANGES.md)
- Version switching: [IWXXM_VERSION_SWITCHING.md](./IWXXM_VERSION_SWITCHING.md)
