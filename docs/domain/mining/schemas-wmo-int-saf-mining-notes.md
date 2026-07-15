# schemas.wmo.int/saf — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** SAF (Simple Aeronautical Features) · **deprecated** foundation · IWXXM **1.x** lineage only · role `iwxxm-validation` (historical resolve)  
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
| Title | WMO SAF — Simple Aeronautical Features (schemas.wmo.int) |
| Publisher | World Meteorological Organization (schemas.wmo.int) |
| Official landing | https://schemas.wmo.int/saf/ |
| Pin / edition | Published **1.0** · **1.1** only (**no 1.2**); **not** imported by IWXXM **v2025-2** |
| Date mined | 2026-07-14 |
| Access | public |
| Label | historical (deprecated foundation; publish still hosted) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Official published **SAF** XSD + Schematron under `schemas.wmo.int/saf/{1.0\|1.1}/` | Runtime import path for IWXXM **2025-2** (or any post-2.0 line) |
| Simplified AIXM-consistent aerodrome / runway / airspace / unit / service features for **IWXXM 1.0–1.1** | Replacement aerodrome model for current pin — that is **AIXM 5.1.1** (via `common.xsd`) |
| Namespaces `http://icao.int/saf/1.0` and `http://icao.int/saf/1.1` | A vocabulary register (`codes.wmo.int`) |
| Sibling of metce / opm / collect under WMO schema repo | Live TAC→IWXXM encode SoT |
| Documented as **obsoleted** since IWXXM **2.0RC1** (April 2016) | An active WMO package line (no further updates) |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| METAR / SPECI / TAF (IWXXM **1.x**) | aerodrome / runway designators | historically `saf:Aerodrome` / `saf:Runway` / `saf:RunwayDirection` | `…/saf/{1.0\|1.1}/examples/{aerodrome,runway,runwayDirection}.xml` | GIFTs never depended on SAF publish tree | lineage only |
| SIGMET / AIRMET (1.x) | FIR / MWO / FIC | historically `saf:Airspace` / `saf:Unit` (+ geometry examples) | `fir.xml`, `mwo.xml`, `fic.xml`, `airspaceVolume-*.xml` | Outside GIFTs | lineage only |
| All F6 under **2025-2** | — | **No** `saf:` — aerodrome/airspace via **`aixm:`** in `common.xsd` | AIXM embed under vendor `externalSchema/aero/…`; Eurocontrol AIXM_WX profile cited by upstream README | N/A | `tac2iwxxm`, `iwxxm-validate` |
| TCA / VAA | — | No SAF feature types (TC/VA → METCE, not SAF) | — | N/A | — |

---

## Key findings

### Published tree

- Landing [https://schemas.wmo.int/saf/](https://schemas.wmo.int/saf/) lists **1.0/** and **1.1/** only (index last-modified **2019-10-11**). **No 1.2** (unlike METCE/OPM/COLLECT).
- Each version package: `saf.xsd`, `features.xsd`, `dataTypes.xsd`, `measures.xsd`, `rule/saf.sch`, `ReleaseNotes-SAF.txt`, `examples/` (8 XML samples).
- Vendor README at `externalSchema/.../saf/README`: *“IWXXM SAF has been obsoleted since the publishing of IWXXM 2.0RC1 in April 2016. There will be no further updates to this directory.”*

### Namespace and 1.0 → 1.1

- **1.0** targetNamespace / `xmlns:saf`: `http://icao.int/saf/1.0`
- **1.1** targetNamespace / `xmlns:saf`: `http://icao.int/saf/1.1`
- Package files **1.0 → 1.1** differ by **namespace (and root schema `@version` on `saf.xsd`) bump only** — feature content otherwise aligned.
- ReleaseNotes **1.1** section is literally **“Nil”**; functional history is under **1.0** (Sep 2013) + RC notes (name change *Aviation→Aeronautical*, AIXM-class simplifications, **FIR/UIR** airspace type).

### Feature inventory (`features.xsd`)

| Element | Role (paraphrase) |
|---------|-------------------|
| `Aerodrome` | Simplified aerodrome (designator, ICAO/IATA indicators, name, ARP, …) |
| `Runway` / `RunwayDirection` | Runway association + direction designator |
| `Airspace` (+ `AirspaceVolume`) | FIR / UIR / etc. + geometry components |
| `Unit` | Organisational unit (e.g. MWO / FIC style in examples) |
| `Service` | Abstract service featuring unit provider |

`dataTypes.xsd` `CodeAirspaceTypeType` enumerations: **`FIR`**, **`UIR`**, **`FIR_UIR`**, **`CTA`** (AIXM-subset; ReleaseNotes cite Annex 3 FIR/UIR support).

`measures.xsd`: `DistanceWithNilReason`, `LengthWithNilReason` (nilReason-capable measures).

### Schematron (`rule/saf.sch`)

- Stand-alone SCH mirrors pattern regex checks also embedded in `features.xsd` (Aerodrome designator / ICAO / IATA, Runway / RunwayDirection, Airspace, Unit, Service name/designator patterns).
- Also mirrored historically under centralized [schemas.wmo.int/rule/1.0|1.1/saf.sch](https://schemas.wmo.int/rule/) — **dropped** from `/rule/1.2/` (see [rule dig](./schemas-wmo-int-rule-mining-notes.md)).

### Examples (published; **not** in vendor embed)

Under each version: `aerodrome.xml`, `runway.xml`, `runwayDirection.xml`, `fir.xml`, `fic.xml`, `mwo.xml`, `airspaceVolume-CircleByCenterPoint.xml`, `airspaceVolume-LinearRing.xml`.

### Vendor vs publish

| Artifact | Result |
|----------|--------|
| `{1.0,1.1}/{saf,features,dataTypes,measures}.xsd`, `rule/saf.sch`, `ReleaseNotes-SAF.txt` | **byte-identical** to published |
| `{1.0,1.1}/examples/*.xml` | Published only — **not** copied into vendor `externalSchema/.../saf/` |
| Stand-alone GitHub [`wmo-im/saf`](https://github.com/wmo-im/saf) | **Archived**; tip ~2017-09-27; README: used in IWXXM **1.0/1.1**; replaced by **profiling AIXM**; weather profiles → [Eurocontrol AIXM_WX](https://ext.eurocontrol.int/aixmwiki_public/bin/view/Profiles/AIXM_WX) |

Vendor path: `vendor/schemas/iwxxm/externalSchema/schemas.wmo.int/saf/{1.0,1.1}/` (also under `iwxxm-translation/externalSchema/`).

### Successor under pin **v2025-2**

- No `icao.int/saf` / `schemas.wmo.int/saf` references outside the vendored SAF tree.
- `2025-2/IWXXM/common.xsd` imports **AIXM 5.1.1** (`http://www.aixm.aero/schema/5.1.1`) and refs `aixm:AirportHeliport`, `aixm:Airspace`, `aixm:Unit`, `aixm:RunwayDirection`, …
- Vendor also embeds `externalSchema/aero/…` (incl. `AIXM_WX` profile trees) for offline resolve — **not** SAF.

### Precedence caveat (from schema documentation)

References to WMO/ICAO Technical Regulations in SAF XSD documentation have **no formal status**; where they differ, **Technical Regulations take precedence**.

---

## Catalog paste rows

```text
### WMO SAF (schemas.wmo.int) — historical
- Publisher: WMO
- URL: https://schemas.wmo.int/saf/ (packages …/saf/1.0/ · …/saf/1.1/)
- Stable concept pattern: namespaces http://icao.int/saf/{1.0|1.1} ; no package 1.2
- Access: public
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET] under IWXXM 1.x only; profiles=[annex3]; role=[iwxxm-validation]
- Gap vs GIFTs: historical aerodrome/airspace feature model; superseded before F6 pin
- Consumer: iwxxm-validate (lineage / IWXXM 1.x docs only)
- Label: historical
- Caveats: obsolete since IWXXM 2.0RC1 (2016-04); prefer AIXM 5.1.1 via common.xsd for 2025-2; vendor XSD+SCH ≡ publish; examples not vendored; GitHub wmo-im/saf archived
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| Tier B / OPM / METCE / rule digs: “saf publish vs vendor still open” | XSD+SCH+ReleaseNotes **byte-identical**; examples public-only | **Close TBD** — cite this dig |
| Org / RULE: GitHub saf = deprecated lineage | Confirmed archived; README → AIXM_WX; publish still hosts 1.0/1.1 | Keep GitHub **historical**; prefer schemas.wmo.int/saf/ as citation landing for 1.x |
| Doc 10003 Advance 2014: SAF logical/XML with IWXXM 1.0RC2 | Aligns with namespaces / early package story; not runtime for 2025-2 | Keep Doc 10003 dig as **historical**; do not encode `saf:` under pin |
| Equal-weight “use SAF for aerodrome in F6” | Pin uses **`aixm:`** via `common.xsd`; zero SAF imports | **Demote** SAF to historical; AIXM is current feature path |
| Centralized `/rule/1.2/` dropped `saf.sch` | Confirmed; package-local `saf/{1.0\|1.1}/rule/saf.sch` remain | Prefer package-local URLs if citing 1.x SCH |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Do **not** emit `saf:` elements for pin **2025-2**. Encode aerodrome / airspace / unit features per product XSD + official examples (AIXM-backed properties from `common.xsd`). SAF examples are IWXXM **1.x** lineage only.
- **tac-validate:** No SAF rules for TAC templates.
- **iwxxm-validate:** No need to run `saf.sch` for official F6 **2025-2** examples. Keep vendor SAF embed for offline resolution of **historical** documents that still import `icao.int/saf/{1.0|1.1}` — do not treat as current Schematron root.
- **Caveats / TBD:** None for publish↔vendor XSD/SCH. Optional: whether any informative iwxxm-translation fixtures still use `saf:` (out of F6 golden path).

---

## Suggested next mining passes

1. Spot-check vendor `externalSchema/aero/…/AIXM_WX` vs Eurocontrol AIXM_WX landing for citation hygiene (successor of SAF — only if a conversion/validation dig needs profile pins).
2. ~~schemas.wmo.int/saf~~ — **done** this pass.
3. [schemas.wmo.int/collect/](https://schemas.wmo.int/collect/) full HTTP package landing if bulletin dig needs more than vendor 1.2 byte-identity (already Tier B).
