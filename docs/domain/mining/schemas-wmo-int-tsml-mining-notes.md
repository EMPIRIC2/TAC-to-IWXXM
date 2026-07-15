# schemas.wmo.int/tsml — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** OGC TimeseriesML (TSML) 1.0 mirror under WMO schema repo · role discovery (not F6 encode/validate path)  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (if any, gitignored):** none (used published HTTP)

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |

| Item | Value |
|------|-------|
| Title | TimeseriesML (TSML) 1.0 — OGC standard mirrored at schemas.wmo.int |
| Publisher | Open Geospatial Consortium (content); WMO hosts mirror at schemas.wmo.int |
| Official landing | https://schemas.wmo.int/tsml/ |
| Pin / edition | **1.0** only under landing (OGC **1.0.0** from OGC 15-042r3, 2016-08-19); IWXXM pin **v2025-2** does **not** import TSML |
| Date mined | 2026-07-14 |
| Access | public |
| Label | normative-schema (OGC TSML); **out of path** for F6 IWXXM |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Official published **TimeseriesML 1.0** XSD + Schematron + examples under `schemas.wmo.int/tsml/1.0/` | WMO METCE / OPM / COLLECT / SAF foundation for aviation IWXXM |
| OGC Standard: XML encoding of the Timeseries Profile of Observations and Measurements | Annex 3 TAC grammar or TAC→IWXXM encode SoT |
| Namespace `http://www.opengis.net/tsml/1.0` (OGC, not `def.wmo.int`) | A vocabulary register (`codes.wmo.int`) |
| Hosted sibling of metce / opm / collect under the WMO schema repository | An IWXXM product schema or Schematron input for `iwxxm-validate` |
| Byte-identical (sampled XSD/SCH/examples) to `schemas.opengis.net/tsml/1.0/` | Present in vendor `externalSchema/schemas.wmo.int/` for the iwxxm pin |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| METAR / SPECI / TAF / AIRMET / SIGMET / VAA / TCA | — | **No** `tsml:` elements; **no** `schemaLocation` to TSML on 2025-2 product XSDs | Official IWXXM examples use product roots + GML/OM as wired by IWXXM — not TSML TVP/DR | N/A (scaffolding outside aviation encode) | — |
| Hydrology / climate timeseries (non-F6) | continuous monitoring series | `tsml:TimeseriesTVP` / `TimeseriesDomainRange` / `Collection` / `MonitoringFeature` | [examples/](https://schemas.wmo.int/tsml/1.0/examples/) (discharge, soil moisture, categorical) | Outside GIFTs / this product | design only if ever bridging OM timeseries |

---

## Key findings

### Published tree

- Landing [https://schemas.wmo.int/tsml/](https://schemas.wmo.int/tsml/) lists **`<1.0/>` only** (index last-modified **2019-10-11**).
- Package [https://schemas.wmo.int/tsml/1.0/](https://schemas.wmo.int/tsml/1.0/):
  - Entry: `timeseriesML.xsd` (includes DR, TVP, Metadata, ObservationProcess, MonitoringFeature, Collection)
  - `timeseriesMetadata.xsd`, `timeseriesTVP.xsd`, `timeseriesDR.xsd`
  - `collection.xsd`, `monitoringFeature.xsd`, `observationProcess.xsd`
  - `ReadMe-tsml-1_0_0.txt` (WMO mirror; **not** on schemas.opengis.net path sampled)
  - `documents/` — OGC `15-042r3_TimeseriesXML.pdf`, `15-043r3_TimeseriesProfile.pdf`
  - `examples/` (+ `encoding_examples/`)
  - `schematron/` — requirements-class SCH files (`6-3` … `6-17`)

### Namespace, copyright, and canonical schemaLocation

- **targetNamespace:** `http://www.opengis.net/tsml/1.0`
- Schema **version** attribute: `1.0.0`
- XSD documentation: TimeseriesML 1.0 is an **OGC Standard**; Copyright (c) 2015, 2016 Open Geospatial Consortium
- ReadMe: published from **OGC 15-042r3** (2016-08-19); more info `http://www.opengeospatial.org/standards/tsml` → [ogc.org/standards/tsml](https://www.ogc.org/standards/tsml/); “most current schema” at `http://schemas.opengis.net/`
- Official example `measurement-timeseries-example.xml` sets:

```text
xsi:schemaLocation="http://www.opengis.net/tsml/1.0 http://schemas.opengis.net/tsml/1.0/timeseriesML.xsd"
```

  Prefer **OGC** schemaLocation for instance documents; WMO path is a **host mirror**.

### Core types (encode shapes — hydrology/climate, not IWXXM products)

| Area | Notable constructs |
|------|--------------------|
| TVP | `TimeseriesTVP`, `MeasurementTVP`, `CategoricalTVP`, `TimeValuePair` |
| Domain–range | `TimeseriesDomainRange`, `TimePositionList`, annotation coverage |
| Metadata | `TimeseriesMetadata`, `PointMetadata` (quality, uom, interpolationType, **nilReason**, censoredReason, uncertainty, …) |
| Process / FOI | `ObservationProcess`, `MonitoringFeature` (+ timezone helpers) |
| Bundle | `Collection` (samplingFeatureMember / observationMember) |

`PointMetadata/nilReason` is **TSML / OGC** metadata — not the IWXXM aviation `codes.wmo.int` nil registers.

### Dependencies (imports)

Relative includes among TSML XSDs; imports include:

- GML 3.2.1, OM 2.0, SWE Common 2.0, GMLCov 1.0
- sampling / samplingSpatial 2.0
- ISO 19139 GMD (`gmd.xsd`)

All via `schemas.opengis.net` (and isotc211) — **not** WMO `def.wmo.int` packages.

### Schematron

SCH files cite OGC requirements classes, e.g. `http://www.opengis.net/spec/timeseriesml/1.0/req/xsd-xml-rules` (`6-3-xsd-xml-rules.sch`: time-zone, swe-types, xlink-title, …). These do **not** participate in IWXXM `iwxxm.sch` validation.

### IWXXM pin wiring (2026-07-14)

Under `vendor/manifest.json` iwxxm **`v2025-2`**:

- **No** product XSD `schemaLocation` / import of `schemas.wmo.int/tsml/…`
- **No** `tsml` string under `vendor/schemas/`
- Vendor `externalSchema/schemas.wmo.int/` contains **collect / metce / opm / saf** only — **no** `tsml/`
- Repo docs previously had **no** TSML citations (this dig is first)

### WMO vs OGC mirror (sampled)

| Artifact | Result |
|----------|--------|
| Core XSDs, sample SCH, sample example XML | **byte-identical** WMO ↔ `schemas.opengis.net/tsml/1.0/` |
| `ReadMe-tsml-1_0_0.txt` | Present on **WMO** only (404 on OGC path sampled) |

### No wmo-im GitHub TSML repo

Org search: no dedicated `wmo-im/tsml` (or similar) repo for this package — lineage is OGC + WMO publish mirror, not a WMO GitHub product schema repo.

---

## Catalog paste rows

```text
### OGC TimeseriesML (TSML) — schemas.wmo.int mirror
- Publisher: OGC (content); WMO (schemas.wmo.int host)
- URL: https://schemas.wmo.int/tsml/ (package https://schemas.wmo.int/tsml/1.0/)
  Prefer instance schemaLocation: http://schemas.opengis.net/tsml/1.0/timeseriesML.xsd
- Stable concept pattern: namespace http://www.opengis.net/tsml/1.0 ; OGC req http://www.opengis.net/spec/timeseriesml/1.0/req/…
- Access: public
- Applies to: products=[]; profiles=[]; role=[] (not F6 iwxxm-validation/conversion)
- Gap vs GIFTs: N/A — hydrology/climate timeseries encoding, not aviation TAC→IWXXM
- Consumer: none (discovery / non-F6 only)
- Label: normative-schema (OGC); out-of-path for this repo’s F6 pin
- Caveats: not in vendor externalSchema; IWXXM v2025-2 does not import TSML; do not confuse PointMetadata nilReason with IWXXM aviation nils
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| (none in domain corpus) | First mine of `/tsml/` | Promote catalog + validation “not on path” row |
| Sibling assumption “everything under schemas.wmo.int feeds IWXXM” | TSML is OGC timeseries; independent of METCE/OPM/IWXXM import graph | Caveat: mirror ≠ IWXXM foundation dependency |
| Equal-weight “use TSML for METAR observation series” | No pin wiring; examples are discharge/soil-moisture style | Reject — keep IWXXM product types + Guidance |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Do **not** emit `tsml:` TimeValuePair / DomainRange encodings for aviation products. Encode per product XSD + TAC-to-XML-Guidance + examples.
- **tac-validate:** No TSML rules for TAC templates.
- **iwxxm-validate:** No need to catalog-resolve or Schematron-run TSML for official F6 instances. Offline catalogs should continue to use vendored METCE/OPM/COLLECT/SAF embeds only.
- **Caveats / TBD:** If a future non-F6 / research bridge needs continuous monitoring timeseries XML, cite OGC package + WMO mirror; still keep separate from `iwxxm.sch`.

---

## Suggested next mining passes

1. Sibling [schemas.wmo.int/saf/](https://schemas.wmo.int/saf/) (deprecated foundation) publish vs vendor — still open from OPM dig.
2. Optional: WaterML 2.0 / related OGC hydrology landings only if product scope expands beyond aviation IWXXM.
