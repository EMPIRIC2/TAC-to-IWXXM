# schemas.wmo.int/metce — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** METCE foundation schema · role `iwxxm-validation` + `conversion` types for SIGMET TC/VA · VAA · TCA  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (if any, gitignored):** none (used published HTTP + vendor embed)

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
| Title | WMO METCE application schema (schemas.wmo.int) |
| Publisher | World Meteorological Organization (schemas.wmo.int) |
| Official landing | https://schemas.wmo.int/metce/ |
| Pin / edition | **1.2** (latest published under landing); IWXXM pin **v2025-2** imports `…/metce/1.2/metce.xsd` |
| Date mined | 2026-07-14 |
| Access | public |
| Label | normative-schema |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Official published **METCE** XSD + Schematron under `schemas.wmo.int/metce/{1.0\|1.1\|1.2}/` | Annex 3 TAC grammar or weather-group SARPs |
| Shared meteorological feature / process model imported by IWXXM product XSDs | Stand-alone aviation TAC→IWXXM encoder SoT |
| Namespace `http://def.wmo.int/metce/2013` (stable across 1.0–1.2) | A vocabulary register (`codes.wmo.int`) |
| Feature types **TropicalCyclone**, **Volcano**, **EruptingVolcano**; **Process** / **MeasurementContext** / **RangeBounds** | GIFTs / METAR REMARKS rules |
| Sibling of collect / opm / saf under WMO schema repo | Replacement for product Schematron in `iwxxm.sch` |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| TCA | tropical cyclone advisory TAC | `tropicalCycloneName` → `metce:TropicalCyclonePropertyType` | IWXXM `tropicalCycloneAdvisory.xsd` imports metce **1.2**; examples `tc-advisory-*` | Entire product outside GIFTs | `tac2iwxxm`, `iwxxm-validate` |
| VAA | volcanic ash advisory TAC | `volcano` → `metce:VolcanoPropertyType` (2025-2) | `volcanicAshAdvisory.xsd` → metce 1.2; `va-advisory-*` | Entire product outside GIFTs | same |
| SIGMET TC | WC-series TAC | `tropicalCyclone` → `metce:TropicalCyclonePropertyType` | `sigmet.xsd` → metce 1.2; `sigmet-A6-2-TC` | Outside GIFTs | same |
| SIGMET VA | WV-series TAC | `eruptingVolcano` → `metce:VolcanoPropertyType` | `sigmet.xsd`; `sigmet-VA-*` | Outside GIFTs | same |
| METAR / SPECI / TAF / AIRMET | — | No direct METCE feature import for classic F6 roots | — | N/A | — |
| Catalog / HTML / zip | UML docs | `html/`, `zip/METCE-1.2-{schema,html,XMI}.zip` | informative EA HTML | N/A | design only |

---

## Key findings

### Published tree

- Landing [https://schemas.wmo.int/metce/](https://schemas.wmo.int/metce/) lists **1.0**, **1.1**, **1.2** only (all last-modified **2019-10-11** on the index).
- **1.2** package contents: `metce.xsd`, `phenomena.xsd`, `procedure.xsd`, `gmlmetce.xsd` (GML profile), `rule/metce.sch`, `ReleaseNotes-METCE.txt`, `html/`, `zip/`.
- **1.0 / 1.1** lack `gmlmetce.xsd` / `html/` / `zip/`; Schematron was historically embeddable in XSD — **1.2** moved SCH to `rule/metce.sch` and added GML profile (ReleaseNotes April–August 2016).

### Namespace and versioning

- **targetNamespace** for all published lines: `http://def.wmo.int/metce/2013`.
- Package **version** attribute on root schema: `1.0` | `1.1` | `1.2`. Runtime IWXXM selects the **URL path** (`…/metce/1.2/…`), not a new namespace year.

### Feature types (`phenomena.xsd`)

- **TropicalCyclone** — required `name` (string); AbstractFeature.
- **Volcano** — `name` + `position` (`gml:PointPropertyType`).
- **EruptingVolcano** — extends Volcano with `eruptionDate` (`dateTime`); substitutionGroup `metce:Volcano`.
- Prose cites BUFR table 0 08 011 meteorological features as *future* expansion candidates; schema itself only implements TC + volcano family.
- Informative volcano naming tip: Smithsonian Global Volcanism Program (legacy URL in schema docs).

### Procedure package

- **Process** (OM_Process implementation), **MeasurementContext**, **RangeBounds**.
- Typo preserved in schema: element name **`measureand`** (not “measurand”).
- Not required for current F6 TCA/VAA/SIGMET TC/VA property encodings (those use phenomena types).

### Schematron (`rule/metce.sch`)

| Pattern | Assert |
|---------|--------|
| `METCE.MC2` | If `measuringInterval` or `resolutionScale` present → `unitOfMeasure` required |
| `METCE.MC1` | Vacuous `true()` (“unitOfMeasure appropriate for measurand”) |
| `METCE.RB1` | `rangeStart` &lt; `rangeEnd` |

No Schematron rules on TropicalCyclone / Volcano naming.

### IWXXM pin wiring (defer to vendor + schemas.wmo.int)

Under `vendor/manifest.json` iwxxm **`v2025-2`**, product XSDs import:

```text
http://schemas.wmo.int/metce/1.2/metce.xsd
```

Seen on:

- `2025-2/IWXXM/tropicalCycloneAdvisory.xsd`
- `2025-2/IWXXM/volcanicAshAdvisory.xsd`
- `2025-2/IWXXM/sigmet.xsd`

**Property-type note (2023-1 vs 2025-2):** VAA in **2023-1** typed `volcano` as `metce:EruptingVolcanoPropertyType`; **2025-2** uses `metce:VolcanoPropertyType`. Prefer pin examples + 2025-2 XSD.

### Vendor embed vs published HTTP (2026-07-14)

| Artifact | Result |
|----------|--------|
| `gmlmetce.xsd`, `ReleaseNotes-METCE.txt`, `rule/metce.sch` | byte-identical to published 1.2 |
| `metce.xsd`, `phenomena.xsd`, `procedure.xsd` | **same XML after C14N**; published uses CRLF, vendor LF |
| Stand-alone GitHub `wmo-im/metce` | lineage only — prefer published URL + vendor `externalSchema/.../metce/1.2/` |

Vendor path: `vendor/schemas/iwxxm/externalSchema/schemas.wmo.int/metce/{1.0,1.1,1.2}/` (also mirrored under `iwxxm-translation/externalSchema/`).

### Precedence caveat (from schema documentation)

References to WMO Technical Regulations in METCE XSD documentation have **no formal status**; where they differ, **Technical Regulations take precedence**.

---

## Catalog paste rows

```text
### WMO METCE (schemas.wmo.int)
- Publisher: WMO
- URL: https://schemas.wmo.int/metce/ (runtime import: …/metce/1.2/metce.xsd)
- Stable concept pattern: namespace http://def.wmo.int/metce/2013 ; versions under /metce/{1.0|1.1|1.2}/
- Access: public
- Applies to: products=[SIGMET,VAA,TCA]; profiles=[annex3]; role=[iwxxm-validation,conversion]
- Gap vs GIFTs: TC/VA/VAA/TCA feature types entirely outside GIFTs METAR encoder
- Consumer: tac2iwxxm | iwxxm-validate
- Label: normative-schema
- Caveats: prefer vendor externalSchema embed (= published 1.2 content); GitHub wmo-im/metce = historical tip; METCE SCH is Process/RangeBounds only
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| Tier B: “Diff vendor metce vs tip (expect pin-frozen)” | Published **1.2** ≡ vendor after C14N (EOL only) | Close that TBD; cite schemas.wmo.int/metce/1.2 + vendor path |
| Org / RULE catalog: GitHub metce = lineage only | Confirmed; official publish is schemas.wmo.int/metce/ | Promote publish URL as SoT cite; keep GitHub row historical |
| Doc 10003 Advance 2014: METCE `schemas.wmo.int/metce/1.0` | Landing still serves 1.0; IWXXM **2025-2** imports **1.2** | Caveat: historical docs may cite 1.0; runtime = 1.2 |
| Equal-weight “use any metce version” | Pin `schemaLocation` is explicitly **1.2** | Defer to latest path used by pin (= 1.2) |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Encode TCA / SIGMET-TC cyclone **name** via `metce:TropicalCyclone`; VAA / SIGMET-VA volcano via `metce:Volcano`(+ erupting subtype when examples require). Do not invent METCE vocabulary hrefs — names are plain strings; colour/phenomenon vocab stays on IWXXM/codelists.
- **tac-validate:** No METCE rules for TAC templates.
- **iwxxm-validate:** Resolve METCE via vendor `externalSchema` (or offline catalog map to published 1.2). Product `iwxxm.sch` remains primary; METCE SCH is ancillary for Process/RangeBounds if those elements appear.
- **Caveats / TBD:** Whether CI Schematron run includes `metce.sch` as a second pass (today product SCH dominates); confirm any future IWXXM tag that bumps METCE beyond 1.2.

---

## Suggested next mining passes

1. ~~Same treatment for sibling [schemas.wmo.int/opm/](https://schemas.wmo.int/opm/)~~ — **done** 2026-07-14: [schemas-wmo-int-opm-mining-notes.md](./schemas-wmo-int-opm-mining-notes.md). ~~Centralized [schemas.wmo.int/rule/](https://schemas.wmo.int/rule/)~~ — **done**: [schemas-wmo-int-rule-mining-notes.md](./schemas-wmo-int-rule-mining-notes.md) (`/rule/1.2/metce.sch` ≡ package-local). Collect already covered via Tier B; ~~saf still open~~ — **done** 2026-07-14: [schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md).
2. Spot-check official VAA/TCA examples for `metce:` element shapes vs GIFTs absence.
3. If operator UI needs volcano authority names, mine Smithsonian GVP separately as **informative** naming aid (not METCE SoT).
