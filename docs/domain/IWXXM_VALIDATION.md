# IWXXM validation

**Purpose:** Pointer catalog for **validating produced IWXXM XML** (XSD + Schematron + codelist RDF).  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) · feeds [#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699).  
**Does not** re-litigate packaging design — cite official landings + vendor pins only.

Hub: [README.md](README.md) · Runtime: `packages/iwxxm-validate` · Engine notes: [validation/COMPREHENSIVE_VALIDATION.md](validation/COMPREHENSIVE_VALIDATION.md).  
Source digs (not SoT): [mining/](mining/).

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

**Pin vs GitHub tag tip (2026-07-14):** vendored commit `35180cbe…` is **ahead of** remote tag `v2025-2` tip `2c4db03…` and uses versioned paths `2025-2/IWXXM/` (+ `2023-1/`). Prefer vendor / `schemas.wmo.int` over a fresh `git checkout v2025-2`. Local clones: `.local/reference/wmo-im-tier-a/` — [mining/wmo-im-tier-a-mining-notes.md](mining/wmo-im-tier-a-mining-notes.md).

FM 205-2023-1 in WMO-No. 306 Vol I.3 still indexes many tables to the **2023-1** package — treat that as historical lineage; **do not** mix 2023-1 Schematron with 2025-2 XML. Working AsciiDoc in the pin tree is titled **FM 205-2025-2** (`documentation/manual/FM205.adoc`).

---

## Validation strategy (produced IWXXM)

Pipeline placement: **stages 3–6** of the domain E2E flow ([README.md](README.md)
§End-to-end strategy). Input is XML from `tac2iwxxm` (or an official fixture). This
strategy is **rule provenance** — engine wiring lives under [validation/](validation/).

### Required stages (release gate)

| Order | Stage | Pass criterion | Artifact |
|-------|-------|----------------|----------|
| 1 | Well-formed XML | Parses without fatal error | lxml / parser |
| 2 | **XSD** | Valid against vendored product + import graph | `2025-2/IWXXM/*.xsd` via catalog |
| 3 | **Schematron** | No failed asserts for the document | `rule/iwxxm.sch` (+ RDF `document()`) |
| 4 | Golden regression | Official `*.xml` examples still pass 1–3 | `examples/` |
| 5 | Optional RDF / live vocab | Codelist membership already mostly in SCH; live codes.wmo.int optional | Prefer offline `rule/*.rdf` in CI |

**Domain release gate:** both **XSD and Schematron** must pass for the **same** IWXXM year
line as the document namespace (`http://icao.int/iwxxm/2025-2` ↔ vendor `2025-2/`). Mixing
2023-1 SCH with 2025-2 XML (or the reverse) is a documented failure class.

### Resolver strategy

| Do | Do not |
|----|--------|
| Resolve via XML catalog / vendored `externalSchema/` tree | Fetch schemas from the network in CI |
| Compile product XSD that pulls METCE/AIXM/GML imports | Assume `iwxxm.xsd` alone is enough |
| Use pin-local `…/iwxxm/2025-2/rule/iwxxm.sch` | Use top-level `schemas.wmo.int/rule/` (IWXXM **1.x** index) |
| Run SCH with RDF snapshots next to `iwxxm.sch` | Invent concept URIs not in XSD `vocabulary=` / examples |

### Blocking vs advisory (domain intent)

| Class | Typical layers | Stance |
|-------|----------------|--------|
| **Blocking** | Well-formed, XSD | Reject / fail CI |
| **Blocking for release** | Schematron (OPMET Guidelines require SCH on translator outputs) | Fail release gate even if some engines historically labeled SCH “non-blocking” |
| **Advisory / smoke** | Extra GML id checks beyond SCH; live AWC XML; iwxxm-translation extras | Informational regression only |

Engine layer names (`AIRPORT_ICAO`, `TAC_SYNTAX`, …) are implementation detail — see
[COMPREHENSIVE_VALIDATION.md](validation/COMPREHENSIVE_VALIDATION.md). Domain SoT for
*what* must pass remains this document + OPMET Guidelines dig.

### Profile strategy

| Profile | Catalogs |
|---------|----------|
| `annex3` | Vendor IWXXM 2025-2 XSD + SCH + RDF only |
| `iwxxm_us` | Same **plus** iwxxm-us 3.0 combined catalogs / examples for `extension` content |

### Fixture priority

Same as conversion golden strategy — official pin examples are **P0**; US examples for US
profile; translation / AWC are informative.

### Translator / aggregator compliance (OPMET Guidelines)

Public [OPMET IWXXM Exchange Guidelines 5th](mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md)
§5.3.2 / §5.3.5 expect Translation Centres to:

| Check | Domain mapping |
|-------|----------------|
| IWXXM vs **most recent** official XSD + Schematron | Vendored pin year line (not network-latest tip) |
| Test TAC set | Official `examples/*.tac` (+ project fixtures) |
| Translation metadata | `common.xsd` attrs — [IWXXM_CONVERSION.md](IWXXM_CONVERSION.md) |
| Monitoring / SCH success **per IWXXM version** | Ops stats — [ICAO_OPMET_COMPLIANCE.md](iwxxm/ICAO_OPMET_COMPLIANCE.md) |

Do **not** mark release green if Schematron is skipped (`xslt2` path not executed) — domain
fixtures are ready; engine gap is tracked in the [reference-set dig](mining/iwxxm-2025-2-reference-set-mining-notes.md).

### How to validate one IWXXM document

1. Confirm namespace year line (`http://icao.int/iwxxm/2025-2` ↔ vendor `2025-2/`).
2. **Well-formed** (incl. `xmlns:xlink` when `xlink:href` is used — AWC TAF smoke fails here).
3. Resolve XSD via **XML catalog / vendored** tree (product XSD + METCE/AIXM imports).
4. Run **Schematron** `rule/iwxxm.sch` with sibling `rule/*.rdf` (`queryBinding="xslt2"`).
5. Prefer official `examples/*.xml` as control; AWC / translation extras = informative only.
6. If SCH is skipped by the engine → **do not** mark release green (fixture corpus is ready; runner gap is tracked).

### Product validation focus (2025-2)

| Product | Primary XSD | Golden fixture prefix | Schematron / codelist notes |
|---------|-------------|----------------------|-----------------------------|
| METAR / SPECI | `metarSpeci.xsd` | `metar-A3-1` · `speci-A3-2` | `common/nil` in official METAR examples; no runway-state types on 2025-2 |
| TAF | `taf.xsd` | `taf-A5-1` · `taf-A5-2` | CNL / NIL shapes; `VV///` absent (no nil) |
| SIGMET (+ TC/VA) | `sigmet.xsd` | `sigmet-A6-*` · `sigmet-VA-*` | SigWxPhenomena; METCE for TC/VA members |
| AIRMET | `airmet.xsd` | `airmet-A6-1a-TS` | AirWxPhenomena + VIS-cause |
| TCA | `tropicalCycloneAdvisory.xsd` | `tc-advisory-A2-2` | METCE `TropicalCyclone` |
| VAA | `volcanicAshAdvisory.xsd` | `va-advisory-A7-2` | METCE `Volcano`; AviationColourCode RDF |
| COLLECT bulletin | `iwxxm-collect.xsd` + collect 1.2 | collect examples | Validate **members** individually; AWC may wrap METAR in COLLECT |
| Translation-failed | product XSD | `*-translation-failed*` | Min-field / quarantine attrs only |

### Per-product validate playbook (copy into tickets)

| Step | Action |
|------|--------|
| 0 | TAC lint passed for product ([TAC_VALIDATION.md](TAC_VALIDATION.md) checklists) |
| 1 | Namespace year = requested pin line |
| 2 | Match structure to golden prefix above (or quarantine shell) |
| 3 | G3 well-formed → G4 product XSD → G5 `iwxxm.sch` + RDF |
| 4 | US profile: re-run catalogs including `iwxxm-us` 3.0 for `extension` |
| 5 | Do **not** green-light on AWC IWXXM or engine SCH-skip |

Gates: [rules/COVERAGE_MATRIX.md](rules/COVERAGE_MATRIX.md) **G1–G7**.

---

## Core machine artifacts

| Artifact | Official URL (2025-2) | Vendor path |
|----------|----------------------|-------------|
| Aggregate XSD | https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd | `2025-2/IWXXM/iwxxm.xsd` (also repo-root `IWXXM/` mirror) |
| Schematron | https://schemas.wmo.int/iwxxm/2025-2/rule/iwxxm.sch | `2025-2/IWXXM/rule/iwxxm.sch` |
| Codelist RDF snapshots | (with Schematron package) | `2025-2/IWXXM/rule/codes.wmo.int-*.rdf` |
| Release notes | https://schemas.wmo.int/iwxxm/2025-2/ReleaseNotes-IWXXM.txt | `2025-2/IWXXM/ReleaseNotes-IWXXM.txt` (**byte-identical** to publish) |
| Examples (fixtures) | https://schemas.wmo.int/iwxxm/2025-2/examples/ | `2025-2/IWXXM/examples/` |
| GML IWXXM helpers | https://schemas.wmo.int/iwxxm/2025-2/gmliwxxm.xsd | `2025-2/IWXXM/gmliwxxm.xsd` |
| Collect entry | https://schemas.wmo.int/iwxxm/2025-2/iwxxm-collect.xsd | `2025-2/IWXXM/iwxxm-collect.xsd` |
| Common types | https://schemas.wmo.int/iwxxm/2025-2/common.xsd | `2025-2/IWXXM/common.xsd` |

**§2 validation file set (inventory 2026-07-14):** `iwxxm.xsd`, `metarSpeci.xsd`, `iwxxm-collect.xsd`, `common.xsd`, `gmliwxxm.xsd`, `rule/iwxxm.sch`, and `rule/` RDF snapshots are all present under the vendor pin. Resolve the full import graph via XML catalog / local vendor tree — do not rely on one XSD alone. Compatibility tree: `vendor/schemas/iwxxm/2023-1/IWXXM/` (do **not** mix SCH across year lines). Tracker: [mining/iwxxm-2025-2-reference-set-mining-notes.md](mining/iwxxm-2025-2-reference-set-mining-notes.md).

**Path caveat — `schemas.wmo.int/rule/`:** the top-level [https://schemas.wmo.int/rule/](https://schemas.wmo.int/rule/) tree is a **centralized / early-line Schematron index** (packages **1.0–1.2**, listing dated **2019-10-11**). It is **not** the runtime Schematron for year-versioned IWXXM. Prefer `…/iwxxm/<pin>/rule/iwxxm.sch`. `/rule/1.0|1.1/iwxxm.sch` bind ns `http://icao.int/iwxxm/1.0|1.1` (63 patterns; no AIRMET/VAA/TCA; includes removed runway-state rules). `/rule/1.2/` dropped IWXXM/SAF SCH and only mirrors foundation files that are **byte-identical** to `metce/1.2/rule/`, `opm/1.2/rule/`, `collect/1.2/rule/` (vendor embeds those package-local paths — no top-level `externalSchema/.../rule/`). Dig: [mining/schemas-wmo-int-rule-mining-notes.md](mining/schemas-wmo-int-rule-mining-notes.md).

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
| Collect / bulletin | COLLECT + `iwxxm-collect.xsd` (see examples); XSD from vendor `externalSchema/.../collect/1.2/` (= [wmo-im/collect](https://github.com/wmo-im/collect) 1.2 — [Tier B dig](mining/wmo-im-tier-b-mining-notes.md)) |
| METCE (foundation) | https://schemas.wmo.int/metce/1.2/ — imported by TCA / VAA / SIGMET XSDs (`schemaLocation` → `metce/1.2/metce.xsd`); vendor `externalSchema/.../metce/1.2/` (= published content). Namespace `http://def.wmo.int/metce/2013`. Feature types: TropicalCyclone, Volcano, EruptingVolcano. Ancillary SCH: `rule/metce.sch` (MeasurementContext / RangeBounds). Dig: [mining/schemas-wmo-int-metce-mining-notes.md](mining/schemas-wmo-int-metce-mining-notes.md) |
| OPM (foundation) | https://schemas.wmo.int/opm/1.2/ — **not** imported by IWXXM product XSDs; METCE `procedure.xsd` imports `opm/1.2/opm.xsd`. Namespace `http://def.wmo.int/opm/2013`. Vendor `externalSchema/.../opm/1.2/` (= published content). Ancillary SCH: `rule/opm.sch` (CompositeObservableProperty / RangeBounds; several asserts vacuous; `OPM.COP1` XPath malformed as published). Dig: [mining/schemas-wmo-int-opm-mining-notes.md](mining/schemas-wmo-int-opm-mining-notes.md) |
| SAF (historical foundation) | https://schemas.wmo.int/saf/ — packages **1.0** / **1.1** only (**no 1.2**). Namespaces `http://icao.int/saf/{1.0\|1.1}`. **Obsolete** since IWXXM **2.0RC1** (2016-04); **not** imported by **2025-2**. Aerodrome/airspace under pin = **AIXM 5.1.1** via `common.xsd`. Vendor XSD+SCH ≡ publish; examples not vendored. Dig: [mining/schemas-wmo-int-saf-mining-notes.md](mining/schemas-wmo-int-saf-mining-notes.md) |
| TSML (OGC TimeseriesML) | https://schemas.wmo.int/tsml/1.0/ — **not** on the IWXXM F6 path: product XSDs do not import it; **no** vendor `externalSchema/.../tsml/`. OGC namespace `http://www.opengis.net/tsml/1.0` (mirror of `schemas.opengis.net/tsml/1.0/`). Dig: [mining/schemas-wmo-int-tsml-mining-notes.md](mining/schemas-wmo-int-tsml-mining-notes.md) |

Non-F6 but present: `spaceWxAdvisory.xsd`, `WAFSSigWxFC.xsd`, `vona.xsd`, `qvaci.xsd`, `metFeature.xsd`.

---

## Sibling vendor bundles

| Bundle | Tag | Upstream | Role in validation |
|--------|-----|----------|--------------------|
| `iwxxm-codelists` | `49-2` | https://github.com/wmo-im/iwxxm-codelists | Codelist RDF SoT (**pin by SHA** — no Git tag named `49-2`) |
| `iwxxm-modelling` | `v2025-2` | https://github.com/wmo-im/iwxxm-modelling/tree/v2025-2 | UML + XSLT **generators** for XSD/SCH (not runtime). See [mining/iwxxm-modelling-v2025-2-mining-notes.md](mining/iwxxm-modelling-v2025-2-mining-notes.md) |
| `iwxxm-translation` | `master` pin | https://github.com/wmo-im/iwxxm-translation | Extra fixtures — **informative**; Amd79-80-2023 = METAR/TAF/VAA/TCA only · suite XML is **2023-1** — re-encode under pin **2025-2** for SCH; no byte-match ([parity dig](mining/iwxxm-translation-parity-mining-notes.md) · #797) |
| `iwxxm-us` | `3.0` | https://nws.weather.gov/schemas/iwxxm-us/3.0/ | Combined WMO+US catalogs when profile = US |

US landing: https://nws.weather.gov/schemas/iwxxm-us/  
Examples: https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/

**Nil / colour / MetFeature registers (2025-2):** Schematron ships **both** `codes.wmo.int-common-nil.rdf` (`IWXXM.nilReasonCheckLegacy`) and `codes.wmo.int-iwxxm-nil.rdf` (`IWXXM.nilReasonCheck`), plus `49-2` and `iwxxm` AviationColourCode RDF. Official METAR examples use `common/nil`; VONA uses `iwxxm/AviationColourCode` and often `iwxxm/nil`. Encode per XSD `vocabulary=` + official examples — see [mining/wmo-im-tier-a-mining-notes.md](mining/wmo-im-tier-a-mining-notes.md) · live inventory refresh [mining/codes-wmo-int-aviation-mining-notes.md](mining/codes-wmo-int-aviation-mining-notes.md) (2026-07-30): `49-2/AviationColourCode` has NIL/NOT_GIVEN/UNKNOWN; `iwxxm/AviationColourCode` has **UNASSIGNED** instead; `iwxxm/MeteorologicalFeature` is **28** members vs **27** on `49-2/` (**+`VOLCANIC_ASH`**) — pin SCH RDF matches live. Live HTML browse needs `Accept: text/html` (bare curl often 404). Weather table **`306/4678`**: prefer vendor CSV (**402** stable notations) — live HTML browse shows only a **~101** subset.

**NSC vs layered cloud (informative FAQ):** APAC IWXXM FAQs 3rd §14.3 — when NSC is reported, layered `cloud` content is not required and co-occurrence can fail format validation. Prefer convert omit + SCH fixture under #797; cite [mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](mining/icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md).

---

## Live vocabulary (optional online checks)

Prefer offline RDF in CI; optional live:

| Register | URL |
|----------|-----|
| Root | https://codes.wmo.int/ |
| IWXXM lists | https://codes.wmo.int/iwxxm (`AviationColourCode`, `MeteorologicalFeature`, `nil`) |
| Nil (legacy classic F6) | https://codes.wmo.int/common/nil |
| Nil (IWXXM-native) | https://codes.wmo.int/iwxxm/nil |
| Weather / phenomena | https://codes.wmo.int/49-2/… · weather tokens https://codes.wmo.int/306/4678 |

Inventory dig (2026-07-30): [mining/codes-wmo-int-aviation-mining-notes.md](mining/codes-wmo-int-aviation-mining-notes.md). Prefer offline RDF in CI; live browse is optional smoke / discovery.

Community index: https://community.wmo.int/iwxxm (**404** as of 2026-07-14) — recovered package table: [Wayback 2026-03-14](https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm) · [mining/community-wmo-iwxxm-wayback-mining-notes.md](mining/community-wmo-iwxxm-wayback-mining-notes.md) · [VERSION_SUPPORT_POLICY Appendix A](iwxxm/VERSION_SUPPORT_POLICY.md#appendix-a--package--iwxxm-line-matrix-informative).  
Live / recent operational METAR·TAF TAC+IWXXM (informative only): [Aviation Weather Center Data API](https://aviationweather.gov/data/api/) — [mining/awc-data-api-mining-notes.md](mining/awc-data-api-mining-notes.md).  
ICAO OPMET exchange Guidelines (5th Ed., Oct 2023, **public**): [mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md](mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) — require Schematron on translator/aggregator/databank outputs; ROC stats include Schematron success **per IWXXM version**; operational package selection historically from the community compatibility table (not printed in the Guidelines).
Informative workshop overview (2025-10 TT-AvData): [mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md](mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md) — deck messaging that **IWXXM 2021-2 and earlier** are to be deprecated in OPMET Guidelines once **2025-2** is official (**not yet in** the Oct 2023 5th Edition text); package×line matrix captured from slides 5/16 (matches vendored **2023-1** / **2025-2** XSD versions); still validate runtime XML only against the **vendored** pin.  
Historical Doc 10003 Advance 2014 (IWXXM **1.0RC2** sample / no COLLECT): [mining/ICAO-Doc-10003-draft-2014-mining-notes.md](mining/ICAO-Doc-10003-draft-2014-mining-notes.md) — lineage only; do not mix with 2025-2 validation.  
UML / EA modelling provenance (how SCH pattern IDs and nilReason types are *authored*): [mining/iwxxm-modelling-v2025-2-mining-notes.md](mining/iwxxm-modelling-v2025-2-mining-notes.md) — **informative**; still validate only against the **vendored** `iwxxm` SCH+XSD+RDF.  
METCE foundation (TropicalCyclone / Volcano imports for TCA·VAA·SIGMET TC/VA): [mining/schemas-wmo-int-metce-mining-notes.md](mining/schemas-wmo-int-metce-mining-notes.md) — publish https://schemas.wmo.int/metce/1.2/; runtime via vendor `externalSchema`.  
OPM foundation (Observable Property Model; transitive via METCE Process only): [mining/schemas-wmo-int-opm-mining-notes.md](mining/schemas-wmo-int-opm-mining-notes.md) — publish https://schemas.wmo.int/opm/1.2/; no `opm:` in 2025-2 F6 examples.  
SAF foundation (**historical** Simple Aeronautical Features): [mining/schemas-wmo-int-saf-mining-notes.md](mining/schemas-wmo-int-saf-mining-notes.md) — publish https://schemas.wmo.int/saf/{1.0,1.1}/; obsolete since IWXXM 2.0RC1; pin uses AIXM via `common.xsd` instead.  
TSML (OGC TimeseriesML 1.0 mirror): [mining/schemas-wmo-int-tsml-mining-notes.md](mining/schemas-wmo-int-tsml-mining-notes.md) — publish https://schemas.wmo.int/tsml/1.0/; **not** imported by IWXXM; prefer OGC `schemas.opengis.net` for instance `schemaLocation`.

---

## Validation fixture strategy

| Fixture type | Source | Assert |
|--------------|--------|--------|
| Success pairs | Official `*.xml` under examples/ | XSD + Schematron pass |
| Translation-failed | `*-translation-failed*.xml` | SCH min-field / quarantine attributes |
| US documents | iwxxm-us examples | Combined catalogs |
| Informative extras | iwxxm-translation (METAR/TAF/VAA/TCA trees) | Non-blocking regression |
| Informative live | AWC Data API `format=iwxxm` | Optional smoke only — expect KKCI attrs / RC1 schemaLocation / COLLECT METAR wrap; **TAF may omit `xmlns:xlink`** (not well-formed) — [awc dig](mining/awc-data-api-mining-notes.md) |

See also §Validation strategy above for release-gate ordering.

---

## What IWXXM validation does *not* cover

| Gap | Use instead |
|-----|-------------|
| TAC syntax before convert | [TAC_VALIDATION.md](TAC_VALIDATION.md) · `tac-validate` |
| Encode mapping correctness | [IWXXM_CONVERSION.md](IWXXM_CONVERSION.md) golden TAC→XML pairs |
| **IWXXM → TAC round-trip** | **No F6 product-wide official reverse SoT** in the WMO package (examples are TAC→XML direction). Some products are **IWXXM-only** (WAFS / QVACI / VONA). Treat reverse decode as optional / out of release gate unless separately specified. |
| Annex 3 observing obligations | ICAO Annex 3 (paywall) — [mining dig](mining/icao-annex-3-mining-notes.md) |
| Strict Schematron when engine skips `xslt2` | Official examples remain the fixture corpus; engine must eventually execute pin `rule/iwxxm.sch` (`queryBinding="xslt2"`) for a true XSD+SCH gate — see package skip warnings |

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

- Layer implementation: [COMPREHENSIVE_VALIDATION.md](validation/COMPREHENSIVE_VALIDATION.md)
- Schematron deploy notes: [SCHEMATRON_RENDER_CHANGES.md](validation/SCHEMATRON_RENDER_CHANGES.md)
- Version switching: [IWXXM_VERSION_SWITCHING.md](iwxxm/IWXXM_VERSION_SWITCHING.md)
