# wmo-im/iwxxm-modelling (v2025-2) — focused mining notes

**Status:** working notes (not normative). Runtime encode/validate SoT remains
`vendor/schemas/iwxxm` + `schemas.wmo.int/iwxxm/2025-2/`.  
**Focus of this pass:** UML/EA model + XSLT generation pipeline (XSD post-processing,
Schematron collation from UML constraints); product coverage provenance.  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local scratch (gitignored):** `.local/reference/iwxxm-modelling-v2025-2/`  
**Vendor mirror:** `vendor/schemas/iwxxm-modelling` (bundle pin `v2025-2`)

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Companion (validation) | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Companion (creation) | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |

| Item | Value |
|------|-------|
| Title | IWXXM Modelling — UML + EA→XSD/SCH tooling |
| Publisher | WMO TT-AvData / wmo-im |
| Official landing | https://github.com/wmo-im/iwxxm-modelling |
| Pin / edition | tag **`v2025-2`** (matches active `iwxxm` vendor pin) |
| Date mined | 2026-07-14 |
| Access | **public** (GitHub); Sparx EA required to *edit* the `.eap` |
| Label | **informative** (generation tooling / model provenance — not runtime SoT) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Authoritative **UML** design package for IWXXM (Sparx EA `.eap`) aligned to namespace `http://icao.int/iwxxm/2025-2` | Published **runtime** XSD / Schematron to validate production XML |
| Documented **pipeline** to generate GML application schemas and collate Schematron from UML class constraints | TAC→IWXXM conversion recipes (`TAC-to-XML-Guidance.txt` lives in `wmo-im/iwxxm`) |
| XSLT that explains how **nilReason** / extension / WithNilReason types get into XSDs | A substitute for `codes.wmo.int` or Annex 3 SARPs |
| Provenance for **why** published `iwxxm.sch` pattern IDs look like `METAR_SPECI.*` / `SIGMET.*` | An HTTP validator or dependency of `packages/iwxxm-validate` |

README explicitly points consumers at [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) for schemas/rules and [wmo-im/iwxxm-codelists](https://github.com/wmo-im/iwxxm-codelists) for RDF registers.

---

## Repo inventory (v2025-2)

| Path | Kind | Role |
|------|------|------|
| `EA/icao-iwxxm-v2025-2.eap` | Sparx EA project (~48 MB Access DB) | UML model: features, constraints, notes citing Annex 3 / WMO 49-2 / PANS-MET |
| `import_package/AIXM_5.1.1.xmi` | XMI | AIXM 5.1.1 dependency import |
| `import_package/ISO TC211 2015-11-19.xml` | XML/XMI | ISO/TC 211 base models |
| `tool/Transformation-Guidance.txt` | text | Step-by-step EA + Saxon HE workflow |
| `tool/ICAO_IWXXM_pre-conditioning.xslt` | XSLT 2.0 | XMI → fragment XSLT (nillable, `use=required`, extensions, unions/enums) |
| `tool/ICAO_IWXXM_post-processing-base.xslt` | XSLT | Static post-process (WithNilReason, AIXM workarounds, common.xsd inserts) |
| `tool/ICAO_IWXXM_post-processing.xslt` | XSLT (~414 KB) | Base + generated attribute/association fragments used inside EA |
| `tool/SCHFromXMI.xslt` | XSLT | Collect UML constraints → `iwxxm.sch` (+ auto codelist/nil RDF asserts) |
| `tool/GMLClassMapping.xml` | XML | ISO 19103/… UML type → GML/XSD mapping for EA config |
| `tool/GMLNamespaces.xml` | XML | Dependent namespaces (GML, AIXM, METCE, COLLECT, …) for EA |
| `tool/IWXXM_UMLProfile.xml` (+ `.eap`) | UML profile | Stereotypes: `featureType`, `codeList`, `IWXXMXML`, tagged values (`vocabulary`, `xsdAsAttribute`, …) |

**No PDFs** in this repository — extract-pdf-to-repo does not apply.

Release tags of interest: `v2025-2`, `v2023-1`, `v2021-2`, `v3.0.0` (align modelling tag with schema line when comparing lineage).

---

## Generation pipeline (from `Transformation-Guidance.txt`)

### GML application schema (XSD)

1. Export IWXXM from EA as XMI (`icao-iwxxm.xml`).
2. Saxon HE: `ICAO_IWXXM_pre-conditioning.xslt` → XSLT fragment.
3. Insert fragment into `ICAO_IWXXM_post-processing-base.xslt` → `ICAO_IWXXM_post-processing.xslt`.
4. Install stylesheet under EA Resources; ensure `GMLClassMapping.xml` + `GMLNamespaces.xml` live under EA `config/GML`.
5. Generate GML Application Schema in EA (select IWXXM post-processing stylesheet).

### Schematron collation

1. Same XMI export.
2. Saxon HE: `SCHFromXMI.xslt` → `iwxxm.sch`.

UML constraint **template** expected by `SCHFromXMI.xslt` (comments, last updated 2025-11-17):

- `Pattern ID:` unique id within the SCH file  
- `Description:` assertion failure message  
- `Assertion:` XPath/XSLT2 assert body  

`SCHFromXMI` also synthesizes **codelist** / **nilReason** checks that load offline RDF
(`document('codes.wmo.int-….rdf')` … `skos:Concept`) — matching the packaged RDF beside
published Schematron in `wmo-im/iwxxm`.

**Caveat:** Guidance still describes `SCHFromXMI-MultiVersion.xslt`, but that file is **not**
present under tag `v2025-2` / `tool/` (guidance drift).

---

## Product × artifact matrix

| Product | UML / SCH pattern prefix (from EAP strings) | IWXXM output (published) | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|---------------------------------------------|--------------------------|-----------------------------|--------------|----------|
| METAR / SPECI | `METAR_SPECI.*` (largest constraint set) | `metarSpeci.xsd` · `iwxxm:METAR`/`SPECI` | `wmo-im/iwxxm` examples + TAC-to-XML-Guidance | GIFTs METAR-only heritage | `iwxxm-validate` (runtime); modelling = provenance only |
| TAF | `TAF.*` | `taf.xsd` | same | outside GIFTs | same |
| SIGMET (+ TC/VA) | `SIGMET.*`, `TropicalCycloneSIGMET.*`, `VolcanicAshSIGMET.*` | `sigmet.xsd` | same | outside GIFTs | same |
| AIRMET | `AIRMET.*` | `airmet.xsd` | same | outside GIFTs | same |
| TCA | `TropicalCycloneAdvisory.*` (+ `TCA`/`MeteorologicalFeature`) | `tropicalCycloneAdvisory.xsd` | same | outside GIFTs | same |
| VAA | `VolcanicAshAdvisory.*` | `volcanicAshAdvisory.xsd` | same | outside GIFTs | same |
| COLLECT / bulletin | `COLLECT.*` | COLLECT / collect NS | AHL page + examples | outside GIFTs | `bulletin` / validate |
| Non-F6 (present in model) | `SpaceWeatherAdvisory.*`, `WAFSSignificantWeatherForecast.*`, … | matching XSDs in package | examples as tagged | N/A | optional |
| Shared | `Common.*` / `COMMON.*`, `METCE.*`, OPM | `common.xsd` | — | — | encode structure |

Rough EAP inventory: **~200** unique `Pattern ID:` strings (some truncated by binary `strings`);
published `IWXXM/rule/iwxxm.sch` carries the **generated** pattern set — always prefer the
SCH file under the `iwxxm` pin for CI.

---

## Key findings

### 1. Modelling is provenance for Schematron, not the runtime rule package

Older repo notes sometimes call `iwxxm-modelling` “Schematron sources.” More precise:

- **Authoring / generation:** UML constraints in the `.eap` + `SCHFromXMI.xslt`
- **Published artifact CI must use:** `vendor/schemas/iwxxm/IWXXM/rule/iwxxm.sch` (+ RDF)

Do not point `iwxxm-validate` at the modelling tree.

### 2. nilReason / WithNilReason are first-class in the EA→XSD path

Pre-conditioning and post-processing explicitly patch EA GML issues so nillable properties
gain `@nilReason`, and measure types
`Angle|Length|Distance|Measure|Velocity|StringWithNilReason` get correct extension bases —
this is **why** encode guidance talks about those property types.

### 3. Extension hooks and `IWXXMXML` stereotype

- Profile stereotype `IWXXMXML`: constraint-only objects (no spurious GML elements).
- Tagged value `noIWXXMExtension=true` suppresses extension elements on selected classes.
- Pre-conditioning adds IWXXM extension elements to most non-abstract classes (national /
  US extension story connects here; runtime US content still from `iwxxm-us`).

### 4. UML notes cite newer SARP family than Doc 10003-2014

EAP embedded notes heavily cite **Annex 3**, **WMO No. 49-2**, and frequently
**PANS-MET (Doc 10157)** alongside product definitions. Treat those as **model documentation
pointers** — paywalled ICAO docs remain paywall; do not dump prose into git. For encode, still
prefer TAC-to-XML-Guidance + examples + codes registry.

### 5. `translationFailedTAC` min-field Schematron lives in the UML

Constraint assertions in the EAP implement the familiar quarantine shapes (e.g. failed
translate still requires issueTime + aerodrome + validTime on TAF-like reports). Runtime
truth: published SCH + failed examples under `iwxxm` examples/.

### 6. Namespace pin in the EAP is 2025-2

Strings include `http://icao.int/iwxxm/2025-2` and `schematronVersion` `1.0.0`.
`GMLNamespaces.xml` still has a **commented** `2024-x` iwxxm entry and a typo
`http://schemas.wmo/int/collect/...` on the collect `xsdDocument` (harmless for our
consumers who do not run EA generation).

### 7. Dependent stacks

Import packages pin **AIXM 5.1.1** and ISO/TC 211 baselines; SCH namespaces include GML 3.2,
AIXM, METCE, XLink, RDF/SKOS/OWL — consistent with published IWXXM validation context.

---

## Catalog paste rows

```text
### wmo-im/iwxxm-modelling (UML + EA→XSD/SCH tooling)
- Publisher: WMO TT-AvData / wmo-im
- URL: https://github.com/wmo-im/iwxxm-modelling/tree/v2025-2
- Stable concept pattern: (generation only) UML Pattern ID → sch:pattern @id; namespace http://icao.int/iwxxm/2025-2
- Access: public
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA,+SWX/WAFS]; profiles=[annex3]; role=[iwxxm-validation] (provenance) · conversion (nilReason/WithNilReason lineage only)
- Gap vs GIFTs: full multi-product Schematron authoring outside GIFTs METAR encoder
- Consumer: design / UI-decode provenance; NOT runtime iwxxm-validate input
- Label: informative
- Caveats: Prefer published iwxxm.sch + XSD under vendor iwxxm pin; do not validate against .eap; SCHFromXMI-MultiVersion.xslt named in guidance but absent from v2025-2 tree
- Mined: 2026-07-14 · pin v2025-2 · #719
- Detail: docs/domain/mining/iwxxm-modelling-v2025-2-mining-notes.md
```

---

## Domain-knowledge cross-check

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| `IWXXM_VERSION_SWITCHING.md` / `COMPREHENSIVE_VALIDATION.md`: `iwxxm-modelling` = “Schematron sources/rules” | Modelling **generates** SCH from UML; runtime rules ship in `wmo-im/iwxxm` | **Caveat** those docs — runtime SoT = `vendor/schemas/iwxxm/.../iwxxm.sch` |
| Catalog sibling row: “UML / generation” only | Still correct label **informative**; expand with tag pin + notes link | **Keep** label; enrich row |
| Doc 10003 Advance 2014 UML primer as lineage | Current model is EA 2025-2 + Doc 10157 cites in notes | Keep 2014 notes **historical**; defer runtime to 2025-2 package |
| FM 205 printed package tables vs 2025-2 | Modelling EAP namespace = `…/iwxxm/2025-2` | Defer encode/validate to vendor pin (unchanged policy) |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Do not encode from the `.eap`. Use for understanding *why* WithNilReason /
  extension / `translationFailedTAC` shapes exist; keep mappings from TAC-to-XML-Guidance + examples.
- **tac-validate:** Out of scope except as citations inside UML notes (Annex 3 / PANS-MET).
- **iwxxm-validate:** Continue validating against **vendored `iwxxm` SCH+XSD+RDF**. Modelling
  explains SCH provenance / pattern-ID taxonomy (`METAR_SPECI.*`, …).
- **Caveats / TBD:** Opening the `.eap` in Sparx for a full diagram pass is optional and needs
  EA licensing; XMI export was not regenerated in this mine (binary EAP only). Doc 10157
  paywall landing not yet catalogued as a standing row.

---

## Suggested next mining passes

1. Optional: export XMI from EA (if available) and list complete `Pattern ID` ↔ SCH `@id` diff vs pin.
2. Add a paywall cite row for **ICAO Doc 10157 (PANS-MET)** if #719 wants Annex 3 companion coverage.
3. When refreshing Schematron docs, replace “modelling = rules” wording with “modelling = UML generators”.
