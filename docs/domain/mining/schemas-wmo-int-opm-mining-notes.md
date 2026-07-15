# schemas.wmo.int/opm — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** OPM (Observable Property Model) foundation schema · role `iwxxm-validation` (transitive XSD) · lineage for METCE `Process`  
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
| Title | WMO OPM — Observable Property Model (schemas.wmo.int) |
| Publisher | World Meteorological Organization (schemas.wmo.int) |
| Official landing | https://schemas.wmo.int/opm/ |
| Pin / edition | **1.2** (latest published under landing); METCE **1.2** imports `…/opm/1.2/opm.xsd`; IWXXM **v2025-2** does **not** import OPM directly |
| Date mined | 2026-07-14 |
| Access | public |
| Label | normative-schema |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Official published **OPM** XSD + Schematron under `schemas.wmo.int/opm/{1.0\|1.1\|1.2}/` | Annex 3 TAC grammar or weather-group SARPs |
| Framework for qualifying / constraining physical properties (composite, statistical qualifier, scalar/range/category constraints) | Stand-alone aviation TAC→IWXXM encode SoT |
| Namespace `http://def.wmo.int/opm/2013` (stable across 1.0–1.2) | A vocabulary register (`codes.wmo.int`) — though `StatisticalFunctionCode` *points at* GRIB2 4.10 |
| Transitive dependency of **METCE** `procedure.xsd` (`Process` may carry `opm:ObservableProperty`) | Direct import of IWXXM product XSDs under pin **2025-2** |
| Sibling of metce / collect / saf under WMO schema repo | Replacement for product Schematron in `iwxxm.sch` |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| METAR / SPECI / TAF / AIRMET / SIGMET / VAA / TCA | — | No `opm:` elements in 2025-2 official examples; OPM only via METCE Process if instantiated | METCE `procedure.xsd` → `…/opm/1.2/opm.xsd` | N/A (scaffolding) | `iwxxm-validate` (XSD catalog resolve) |
| Catalog / GML profile | UML lineage | `gmlopm.xsd` (1.2 only) | publish 1.2 | N/A | design only |

---

## Key findings

### Published tree

- Landing [https://schemas.wmo.int/opm/](https://schemas.wmo.int/opm/) lists **1.0**, **1.1**, **1.2** only (index last-modified **2019-10-11**).
- **1.2** package: `opm.xsd`, `observable-property.xsd`, `gmlopm.xsd`, `rule/opm.sch`, `ReleaseNotes-OPM.txt`.
- **1.1** / **1.0**: same core XSDs + SCH; **1.0** has **no** published `ReleaseNotes-OPM.txt`; **1.2** adds GML profile and drops embedded Schematron-in-XSD (ReleaseNotes Apr–Aug 2016) — same pattern as METCE 1.2.

### Namespace and versioning

- **targetNamespace** for all published lines: `http://def.wmo.int/opm/2013`.
- Package **version** attribute: `1.0` | `1.1` | `1.2`. Runtime selects the **URL path** (`…/opm/1.2/…`), not a new namespace year.

### Core types (`observable-property.xsd`)

- **AbstractObservableProperty** → **ObservableProperty**, **QualifiedObservableProperty**, **CompositeObservableProperty**.
- Constraints: **ScalarConstraint**, **RangeConstraint**, **CategoryConstraint**; **RangeBounds**; **StatisticalQualifier** (+ `StatisticalFunctionCode`).
- Codelist vocabulary tag: `http://codes.wmo.int/grib2/codeflag/4.10` (WMO-No. 306 Vol I.2 GRIB 4.10 / supplemental BUFR 0 08 023) — **not** an IWXXM aviation nil/weather register.
- Intended use (schema prose): OM_Observation / METCE Process `parameter` NamedValue with name `http://def.wmo.int/opm/2013/observable-property#property`.

### Schematron (`rule/opm.sch`)

| Pattern | Assert (summary) |
|---------|------------------|
| `OPM.SC1` | Vacuous `true()` (“unitOfMeasure appropriate…”) |
| `OPM.COP1` | `count` attribute should equal `count(opm:property)` — **published test expression is `{if(...)}` (malformed XPath)**; do not rely on this assert as-shipped |
| `OPM.RC1` / `OPM.QOP1` | Vacuous `true()` UoM checks |
| `OPM.RB1` | `rangeStart` &lt; `rangeEnd` |

Product IWXXM Schematron remains primary for F6 instance validation.

### IWXXM / METCE wiring (defer to vendor + schemas.wmo.int)

Under `vendor/manifest.json` iwxxm **`v2025-2`**:

- Product XSDs (**no** direct `schemaLocation` to OPM).
- METCE **1.2** `procedure.xsd`:

```text
http://schemas.wmo.int/opm/1.2/opm.xsd
```

(older METCE 1.0 / 1.1 packages import matching `/opm/1.0/` or `/opm/1.1/` paths).

No official `2025-2/examples/*.xml` contain `opm:` elements (spot-check 2026-07-14).

### Vendor embed vs published HTTP (2026-07-14)

| Artifact | Result |
|----------|--------|
| 1.0 / 1.1 XSD + SCH; 1.2 `gmlopm.xsd`, `ReleaseNotes-OPM.txt`, `rule/opm.sch` | **byte-identical** to published |
| 1.2 `opm.xsd`, `observable-property.xsd` | **same XML after C14N**; published uses CRLF, vendor LF |
| Stand-alone GitHub [`wmo-im/opm`](https://github.com/wmo-im/opm) | **archived**; tip through **1.2** @ `0230b10` (2017-10-24) — lineage only |

Vendor path: `vendor/schemas/iwxxm/externalSchema/schemas.wmo.int/opm/{1.0,1.1,1.2}/` (also under `iwxxm-translation/externalSchema/`).

### GitHub README (governance note)

Archived README: OPM derived from OGC SWE / INSPIRE-style work; “*as an interim measure, the WMO Logical Data Model METCE includes the Observable Property Model*” — governance pending. Prefer **publish URL + vendor** over GitHub tip.

### Precedence caveat (from schema documentation)

References to WMO Technical Regulations in OPM XSD documentation have **no formal status**; where they differ, **Technical Regulations take precedence**.

---

## Catalog paste rows

```text
### WMO OPM (schemas.wmo.int)
- Publisher: WMO
- URL: https://schemas.wmo.int/opm/ (runtime import via METCE: …/opm/1.2/opm.xsd)
- Stable concept pattern: namespace http://def.wmo.int/opm/2013 ; versions under /opm/{1.0|1.1|1.2}/
- Access: public
- Applies to: products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3]; role=[iwxxm-validation]
- Gap vs GIFTs: Observable-property scaffolding; not used in classic F6 example instance trees
- Consumer: iwxxm-validate
- Label: normative-schema
- Caveats: prefer vendor externalSchema embed (= published 1.2 content); GitHub wmo-im/opm archived; no direct IWXXM product import; OPM.COP1 SCH test XPath looks malformed
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| Tier B: “Same check still open for opm/saf” (vendor vs publish) | Published **1.2** ≡ vendor after C14N (EOL only on main XSDs) | Close OPM TBD; ~~saf still open~~ → closed in [SAF dig](./schemas-wmo-int-saf-mining-notes.md) |
| Org / RULE catalog: GitHub opm = lineage only | Confirmed archived; official publish is schemas.wmo.int/opm/ | Promote publish URL as SoT cite; keep GitHub row historical |
| Doc 10003 Advance 2014: OPM `schemas.wmo.int/opm/1.0` | Landing still serves 1.0; METCE/IWXXM pin path uses **1.2** | Caveat: historical docs may cite 1.0; runtime resolve = 1.2 |
| Equal-weight “encode observables via OPM for METAR/TAF” | No `opm:` in 2025-2 F6 examples; product values use IWXXM types + codes.wmo.int | Keep OPM as foundation resolve only — not encode SoT |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Do **not** invent OPM wrappers for temperatures, winds, etc. Encode per product XSD + Guidance + examples. OPM is irrelevant unless emitting METCE `Process` with observable-property parameters (outside current F6 golden paths).
- **tac-validate:** No OPM rules for TAC templates.
- **iwxxm-validate:** Resolve OPM via vendor `externalSchema` when validating documents that pull METCE procedure (offline catalog). Do not require a separate `opm.sch` pass for official F6 examples; if ever enabled, treat `OPM.COP1` as unreliable until upstream fixes the assert XPath.
- **Caveats / TBD:** ~~Sibling schemas.wmo.int/saf/ publish vs vendor~~ — **closed** 2026-07-14 ([schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md): XSD+SCH ≡ publish; examples public-only). Collect publish already covered via Tier B.

---

## Suggested next mining passes

1. ~~Same treatment for sibling [schemas.wmo.int/saf/](https://schemas.wmo.int/saf/)~~ — **done** 2026-07-14: [schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md). Centralized Schematron index [schemas.wmo.int/rule/](https://schemas.wmo.int/rule/) mined 2026-07-14 — [schemas-wmo-int-rule-mining-notes.md](./schemas-wmo-int-rule-mining-notes.md) (`/rule/1.2/opm.sch` ≡ package-local).
2. Spot-check whether any non-F6 pin examples (SWX / WAFS / MetFeature) ever instantiate `opm:` — currently none expected for classic F6.
