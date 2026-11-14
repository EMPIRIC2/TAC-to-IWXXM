# Domain contract

> Index: [README.md](README.md) 
> Machine index: [config/profiles/catalog.yaml](../config/profiles/catalog.yaml) 
> Rule catalogs: [config/rules/](../config/rules) 
> Last updated: 2026-11-13

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

## Automation gaps (outside live-feed refresh)

Live Traditional Alphanumeric Code (TAC) and ICAO Meteorological Information
Exchange Model (IWXXM) feed refresh, plus World Meteorological Organization
(WMO) schema change signals, do **not** close the gaps below. Track them under
GitHub issue [#884](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/884)
(parent epic [#876](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/876)).
RAID: `docs/issues.csv` **I-003**, `docs/risks.csv` **R-003**.

### No public TAC grammar API

There is no known public machine-readable grammar or Application Programming
Interface (API) that defines TAC form per weather product (for example Extended
Backus–Naur Form or JSON Schema). Lint and encode rules therefore come from
human mining of manuals, vendor examples, and licensed International Civil
Aviation Organization (ICAO) text — not from an automated grammar pull.

Do not invent an in-repo “grammar API” that claims to be that missing SoT.

### Annex 3 and PANS-MET stay licensed PDFs

ICAO Annex 3 and Procedures for Air Navigation Services — Meteorology
(PANS-MET, Doc 10157) remain licensed Portable Document Format (PDF) files on
the ICAO Store. There is no Annex 3 / PANS-MET API.

This repository cites store landings and section numbers only. It does not host
scraped ICAO text. Access and citation policy:
[config/rules/ACCESS_AND_CITATION.md](../config/rules/ACCESS_AND_CITATION.md).
URL inventory:
[config/rules/RULE_SOURCE_URLS.md](../config/rules/RULE_SOURCE_URLS.md).

### What this means for lint and encode

| Area | What automation can do | What humans or process must cover |
|------|------------------------|-----------------------------------|
| Live TAC / IWXXM pairs | Refresh regression fixtures from public feeds | Judge national or incomplete form against SARPs |
| WMO schema / Schematron pins | Detect pin and registry change | Map pin change to product encode rules |
| TAC lint (`tac-validate`) | Run the in-repo issue catalog | Add or change rules only after a licensed reader cites Annex 3 / PANS-MET (or public WMO FM / codes where those apply) |
| TAC → IWXXM encode (`tac2iwxxm`) | Encode against the selected pin | Resolve ambiguous TAC using manuals; do not treat feed shape as SARPs |

### Partial proxies (not substitutes)

These public or vendored sources help CI and mining. They do **not** replace
Annex 3 or PANS-MET prose.

| Proxy | Useful for | Caveat |
|-------|------------|--------|
| WMO Manual on Codes (FM) and [codes.wmo.int](https://codes.wmo.int/) | Alphanumeric templates; weather and nil vocabularies | Not ICAO Standards and Recommended Practices (SARPs) prose |
| Vendored IWXXM XSD / Schematron and official WMO examples | Encode and validate shape for a pin | Not a TAC grammar source of truth |
| National Aeronautical Information Publications (AIPs), FMH-1, regional guides | National or regional practice | Must not override Annex 3 |
| Live public TAC samples | Regression fixtures | Form may be incomplete or national |

## Local feeder

Narrative stubs, mining notes, and quality digs may remain under local
`docs/domain/`. Do not treat those feeders as the clone-time corpus. Update this
contract and `config/` when a rule becomes durable.
