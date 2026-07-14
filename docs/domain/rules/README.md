# Rule-source documentation (TAC validation & TAC→IWXXM)

Living catalog of **authoritative public URLs** for TAC validation rules and
TAC → IWXXM conversion / IWXXM validation — mined for
[#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719).

**Scope:** discovery / documentation only. No engine rewrite. Do **not** commit
copyrighted full-text PDFs — URLs and citations only.

| Document | Purpose |
|----------|---------|
| [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md) | Master URL catalog (validation + conversion + profiles) |
| [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) | F6 product × profile × role matrix |
| [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md) | Paywall / register friction + citation rules |
| [../validation/ANNEX3_TAC_VALIDATION_SOURCES.md](../validation/ANNEX3_TAC_VALIDATION_SOURCES.md) | Annex 3 / TAC template & business-rule sources |
| [../iwxxm/IWXXM_CREATION_SOURCES.md](../iwxxm/IWXXM_CREATION_SOURCES.md) | TAC→IWXXM creation / encoding sources |
| [../iwxxm/IWXXM_VALIDATION_SOURCES.md](../iwxxm/IWXXM_VALIDATION_SOURCES.md) | XSD / Schematron / codelist validation landings |
| [../iwxxm/WMO-306-vI-3-2023-mining-notes.md](../iwxxm/WMO-306-vI-3-2023-mining-notes.md) | Focused FM 205 / Manual on Codes working notes |
| [../iwxxm/PPT-02-IWXXM-Framework-WMO-mining-notes.md](../iwxxm/PPT-02-IWXXM-Framework-WMO-mining-notes.md) | Informative TT-AvData / ESAF workshop overview (landings, translation attrs, 2025-2) |

## Labeling convention

| Label | Meaning |
|-------|---------|
| **normative** | Binding WMO/ICAO/national regulation or machine artifact (XSD, Schematron, registry) |
| **normative-vocabulary** | Official coded vocabularies (`codes.wmo.int`, etc.) |
| **normative-schema** | Official IWXXM XSD/Schematron packages |
| **normative-conversion-notes** | Official TAC→XML guidance shipped with schemas |
| **normative-examples** | Official paired TAC/XML examples |
| **informative** | Useful fixtures / community notes — not binding |
| **historical-GIFTs** | Baseline gap reference only (ADR-014); not ongoing SoT |

## Consumers

| Package / surface | Typical use of this catalog |
|-------------------|-----------------------------|
| `packages/tac-validate` | TAC syntax / template / vocab rule SoT citations (#698) |
| `packages/tac2iwxxm` | Field mappings, nilReasons, codelist hrefs (#693) |
| `packages/iwxxm-validate` | Schema/Schematron release pointers (#699) |
| UI decode / F7 (#702, #714) | Operator-facing provenance |

## Vendor pin (runtime truth)

See `vendor/manifest.json`. Active IWXXM schema line: **`v2025-2`**
(`http://icao.int/iwxxm/2025-2`). Prefer
`https://schemas.wmo.int/iwxxm/2025-2/` over older FM 205 printed package tables
when validating live XML.

## Mining new sources

Use the project skill **`.cursor/skills/mine-domain-sources/`** to mine URLs,
`wmo-im` repos, `codes.wmo.int`, and vendor mirrors into this tree (catalog rows,
coverage matrix, companion `*_SOURCES.md`, optional ticket comments). For PDF
binaries, use **`extract-pdf-to-repo`** first (extracts stay under `.local/`).
