# Domain documentation (rule provenance)

**Not** in the minimal corpus ([`docs/CORPUS.md`](../CORPUS.md)). Living citations for
TAC validation, TAC→IWXXM conversion, and IWXXM XSD/Schematron — no copyrighted full text.

## Canonical (standing)

| Doc | Role | Consumer |
|-----|------|----------|
| [TAC_VALIDATION.md](./TAC_VALIDATION.md) | Annex 3 / TAC template & vocab sources + **TAC validation strategy** | `tac-validate` |
| [IWXXM_CONVERSION.md](./IWXXM_CONVERSION.md) | TAC→IWXXM encode / nilReason / examples + **conversion rules** | `tac2iwxxm` |
| [IWXXM_VALIDATION.md](./IWXXM_VALIDATION.md) | XSD + Schematron + codelist pins + **IWXXM validation strategy** | `iwxxm-validate` |
| [rules/RULE_SOURCE_URLS.md](./rules/RULE_SOURCE_URLS.md) | Master URL catalog | design / UI provenance |
| [rules/COVERAGE_MATRIX.md](./rules/COVERAGE_MATRIX.md) | F6 product × role coverage | gates |
| [rules/ACCESS_AND_CITATION.md](./rules/ACCESS_AND_CITATION.md) | Paywall / citation policy | mining + PRs |

**Vendor pin (runtime):** `vendor/manifest.json` → IWXXM **`v2025-2`**. Prefer
`https://schemas.wmo.int/iwxxm/2025-2/` over older printed package tables.

**Reference-set inventory (2026-07-14):** progress against the IWXXM validation/conversion
external + file checklist lives in
[`mining/iwxxm-2025-2-reference-set-mining-notes.md`](./mining/iwxxm-2025-2-reference-set-mining-notes.md).

---

## End-to-end strategy (TAC / Annex 3 → IWXXM)

Use this pipeline for every F6 product under profile **`annex3`** (and overlay **`iwxxm_us`**
where national REMARKS/extensions apply). Stages are **separate concerns** — do not fold
Annex 3 SARPs into XSD checks or Schematron into TAC lint.

| Stage | What it proves | Strategy SoT | Engine |
|-------|----------------|--------------|--------|
| **1. TAC lint** | Input TAC matches Annex 3 / WMO-306 templates + vocab membership | [TAC_VALIDATION.md](./TAC_VALIDATION.md) §Validation strategy | `packages/tac-validate` |
| **2. Convert** | TAC tokens → correct IWXXM structure, nilReasons, `xlink:href`s | [IWXXM_CONVERSION.md](./IWXXM_CONVERSION.md) §Conversion strategy | `packages/tac2iwxxm` |
| **3. Well-formed XML** | Parseable document | [IWXXM_VALIDATION.md](./IWXXM_VALIDATION.md) | `iwxxm-validate` |
| **4. XSD** | Structure / types / required attrs against pin | same · vendored `2025-2/IWXXM/*.xsd` | `iwxxm-validate` |
| **5. Schematron** | Business rules + offline RDF codelist asserts | same · `rule/iwxxm.sch` + `rule/*.rdf` | `iwxxm-validate` |
| **6. Golden pairs** | Official TAC↔XML examples pass convert + validate | `schemas.wmo.int/iwxxm/2025-2/examples/` | CI fixtures |
| **7. Bulletin / ops** (when applicable) | COLLECT packing, AHL T1T2, translation-centre attrs | Conversion + [iwxxm/ICAO_OPMET_COMPLIANCE.md](./iwxxm/ICAO_OPMET_COMPLIANCE.md) | `tac2iwxxm` + ops |

**Release gate (domain cite):** produced IWXXM must pass **both** XSD and Schematron for the
vendored pin (OPMET Exchange Guidelines + project gates). Optional live AWC / translation
fixtures are **informative smoke only** — never encode SoT.

**Profile routing**

| Profile | TAC rules | Encode | Validate |
|---------|-----------|--------|----------|
| `annex3` | Annex 3 + WMO-306 + codes.wmo.int | pin examples + TAC-to-XML-Guidance | vendor IWXXM 2025-2 |
| `iwxxm_us` | FMH-1 / NWS + Annex 3 core | `extension` via iwxxm-us 3.0 | WMO base + US catalogs |

**Conflict rule:** when sources disagree, defer to **latest** machine pin
(`vendor/manifest.json` / `schemas.wmo.int/iwxxm/<pin>/`) over older printed FM tables or
workshop decks. See [rules/ACCESS_AND_CITATION.md](./rules/ACCESS_AND_CITATION.md).

Product × role coverage: [rules/COVERAGE_MATRIX.md](./rules/COVERAGE_MATRIX.md).

---

## Transitory

| Path | Role |
|------|------|
| [mining/](./mining/) | Focused source digs (`*-mining-notes.md`). Promote durable findings into the canonical table above; do not treat mining notes as SoT. |

## Other folders (operational / engineering)

| Path | Role |
|------|------|
| [iwxxm/](./iwxxm/) | Version switching, OPMET ops notes, elevation — product behavior, not URL mining. Ops validation order: [ICAO_OPMET_COMPLIANCE.md](./iwxxm/ICAO_OPMET_COMPLIANCE.md) §Validation / conversion strategy |
| [validation/](./validation/) | Engine architecture / failure taxonomy / Schematron render notes. **Rule SoT stays in the three canonicals** — start at [COMPREHENSIVE_VALIDATION.md](./validation/COMPREHENSIVE_VALIDATION.md) only for wiring; map layers via its domain preface |

**Rules catalog strategy:** [rules/README.md](./rules/README.md) (role routing + **apply playbooks**) ·
[rules/COVERAGE_MATRIX.md](./rules/COVERAGE_MATRIX.md) (G1–G7 gates · product × strategy cites).

**Operator / briefing (sources-first, EV-041):** [../ops/operator-ui-runbook.md](../ops/operator-ui-runbook.md) ·
[../guides/operator-sources-pptx/](../guides/operator-sources-pptx/) (PPT pack — path-cite only; not CORPUS).

**Canonical strategy deep dives (2026-07-14 continue · 2026-07-30 promote #797):**

| Doc | Added for this pass |
|-----|---------------------|
| [TAC_VALIDATION.md](./TAC_VALIDATION.md) | **A3-2** METAR/SPECI · **A5-1** TAF · **A6** SIGMET/AIRMET checklists · VAA/TCA A2 · US SPECI §2.5.2.a · **RMK→iwxxm-us keep-list** · NSC exclusivity footnote (APAC FAQ) |
| [IWXXM_CONVERSION.md](./IWXXM_CONVERSION.md) | Product encode playbook · VAA colour table · **structured RMK→iwxxm-us elements** · APAC FAQ encode/ops · translation-suite P2 policy |
| [IWXXM_VALIDATION.md](./IWXXM_VALIDATION.md) | “How to validate one document” · golden prefixes · **per-product validate playbook** · dual colour/nil/MetFeature (`VOLCANIC_ASH`) + NSC FAQ cite |


## Mining workflow

Use `.cursor/skills/mine-domain-sources/` (and `extract-pdf-to-repo` for PDFs).  
Write digs under [`mining/`](./mining/); promote durable findings into the canonical
table above + [`rules/`](./rules/). PDF binaries stay under `.local/` (gitignored).
