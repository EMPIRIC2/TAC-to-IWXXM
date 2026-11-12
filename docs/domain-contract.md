# Domain contract

> Index: [README.md](README.md) 
> Machine index: [config/profiles/catalog.yaml](../config/profiles/catalog.yaml) 
> Rule catalogs: [config/rules/](../config/rules) 
> Last updated: 2026-11-10

This document states domain rules for TAC lint, TAC to IWXXM conversion, IWXXM
validation, and conversion profiles. Detailed mining notes may stay in the local
`docs/domain/` feeder.

## Terms

| Term | Meaning |
|------|---------|
| TAC | Traditional Alphanumeric Code (aviation text such as METAR) |
| IWXXM | WMO XML form of the same aviation products |
| Semantic profile | Rules for how TAC maps into IWXXM content |
| Exchange profile | Rules for bulletin, filename, and routing packaging |
| Pin | Vendor schema release line under `vendor/schemas/` |

## Pipeline order

1. Lint TAC with `tac-validate`.
2. Convert TAC to IWXXM with `tac2iwxxm`.
3. Make sure that the XML is well-formed.
4. Validate against XSD for the selected pin.
5. Validate against Schematron for the selected pin.
6. Compare golden examples when the product quality bar requires them.

Schematron is blocking for release quality bars.

## Roles

| Role | Question | Engine |
|------|----------|--------|
| validation | Is the TAC legal for this product and profile? | `tac-validate` |
| conversion | How does TAC map to IWXXM elements? | `tac2iwxxm` |
| iwxxm-validation | Is the produced XML valid for the pin? | `iwxxm-validate` |
| bulletin | How do COLLECT, AHL, and packaging rules apply? | convert plus ops path |

## Semantic vs exchange profiles

Semantic profiles own TAC parse rules, REMARKS policy, and national IWXXM
extensions. Exchange profiles own bulletin and routing packaging. Destination
credentials for dissemination are not profile data. Those credentials stay in
memory only for one send.

Machine catalog: [config/profiles/catalog.yaml](../config/profiles/catalog.yaml).

### Baseline semantic ids

| ID | Legacy alias | Status |
|----|--------------|--------|
| `ICAO_2025` | `annex3` | Implemented |
| `US_FAA_NWS` | `iwxxm_us` | Implemented |
| `CA_ECCC` | — | Implemented (national reference) |
| Other nationals in catalog | — | Thin, planned, or deepen in progress |

### Baseline exchange ids

| ID | Status |
|----|--------|
| `GLOBAL_AFS` | Implemented default |
| `APAC_ROBEX`, `EUR_RODEX`, `AFI`, `CAR_SAM` | Catalogued; deepen by priority |

## Rule catalogs (tracked under config)

| Asset | Path | Purpose |
|-------|------|---------|
| Issue catalog | `config/rules/ISSUE_CATALOG.json` (+ `.md`) | Lint issue registry twin |
| Provenance map | `config/rules/PROVENANCE_MAP.json` (+ `.md`) | Dig to rule to source map |
| Coverage matrix | `config/rules/COVERAGE_MATRIX.md` | Product by profile by role gates |
| Source URLs | `config/rules/RULE_SOURCE_URLS.md` | Master URL inventory |
| Access policy | `config/rules/ACCESS_AND_CITATION.md` | Paywall and citation rules |

## Labeling

| Label | Meaning |
|-------|---------|
| normative | Binding regulation or machine artifact |
| normative-vocabulary | Official coded vocabularies |
| normative-schema | Official XSD or Schematron packages |
| normative-examples | Official paired TAC/XML examples |
| informative | Fixtures or community notes; not binding |

## Local feeder

Narrative stubs, mining notes, and quality digs may remain under local
`docs/domain/`. Do not treat those feeders as the clone-time corpus. Update this
contract and `config/` when a rule becomes durable.
