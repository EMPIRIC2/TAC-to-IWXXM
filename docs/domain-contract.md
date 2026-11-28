# Domain contract

> Index: [README.md](README.md) 
> Machine index: [config/profiles/catalog.yaml](../config/profiles/catalog.yaml) 
> Rule catalogs: [config/rules/](../config/rules) 
> Last updated: 2026-11-26

This document states domain rules for TAC lint, TAC to IWXXM conversion, IWXXM
validation, and conversion profiles. Detailed mining notes may stay in the local
`docs/domain/` feeder.

**Rebaseline (EV-requirements-baseline-csv / epic #1688):** M1 drops national
US/CA (and other national) semantic wire ids, LWIS/SAWR variants, and the
G-AIRMET live-map layer. Convert/API/catalog ship ICAO baseline only. Target
pins remain `3.0`, `2021-2`, `2023-1`, `2025-2` with official Schematron and
matching XSD fetched at build or runtime (FR-077 / NFR-016; D-019). Shared
quality-bar regression uses those official releases (FR-032 / NFR-017; D-018).
Do not add new work on dropped national paths. Emit packages and
`catalog.yaml` rows may remain on disk until a later delete pass.

## Terms

| Term | Meaning |
|------|---------|
| TAC | Traditional Alphanumeric Code (aviation text such as METAR) |
| IWXXM | WMO XML form of the same aviation products |
| Semantic profile | Rules for how TAC maps into IWXXM content |
| Exchange profile | Rules for bulletin, filename, and routing packaging |
| Pin | Official IWXXM release line (`3.0`, `2021-2`, `2023-1`, `2025-2`); resolved from schema cache |

## Pipeline order

1. Lint TAC with `tac-validate`.
2. Convert TAC to IWXXM with `tac2iwxxm`.
3. Make sure that the XML is well-formed.
4. Validate against XSD for the selected pin.
5. Validate against Schematron for the selected pin.
6. Compare golden examples when the product quality bar requires them.

Schematron is blocking for release quality bars.

## Translation-failed quarantine (convert hard fail)

When convert cannot build an operational report for **product-shaped** TAC, it
still emits an official-shaped IWXXM shell with `@translationFailedTAC` set to
the original TAC text ([Corpus: product §F6], #1563, D-031). The shell must not
invent phenomenon tokens, encode illegal geometry, or pretend parse succeeded.

| Layer | Policy |
|-------|--------|
| Convert | Soft-ok (`ok=true`) with issue code `TRANSLATION_FAILED` (warning); XML present |
| XSD | Soft / dedicated layer — official `*-translation-failed` examples are the shape bar; quarantine is not an operational publish claim |
| Schematron | Not treated as operational pass; may warn or soft-fail depending on pin rules |
| Live eval | Count as convert failure / `TRANSLATION_FAILED` — **not** `iwxxm_validation.skip` and **not** operational IWXXM pass |

Regional ICAO guidance for failed translation is cited in the session RAIDD
decision (tracked SoT: `docs/decisions.csv`; no ADR tree this rebaseline per
D-025). Do not put internal doc ids on operator UI surfaces.

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

Wire aliases `annex3` / `iwxxm_us` were removed after 2026-10-31
([#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)). Callers use
canonical ids. Internal emit keys (`annex3` / `iwxxm_us`) remain for plugin
dispatch only.

| ID | Former wire alias (removed) | Status |
|----|-----------------------------|--------|
| `ICAO_2025` | `annex3` | Implemented |
| `US_FAA_NWS` | `iwxxm_us` | Implemented (emit package; product ship list is ICAO-only per M1) |
| `CA_ECCC` | — | Implemented (national reference; product ship list ICAO-only per M1) |
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

## METAR and SPECI handbook quality (WMO-No. 782)

`tac-validate` applies combination checks for METAR and SPECI that follow the
aerodrome report handbook code format. Key behaviors:

1. Group order is fixed: identification, wind, visibility, RVR, weather, cloud,
   temperature, QNH, supplementary, optional TREND, then national remarks.
2. Wrong station / time / wind order is an error.
3. CAVOK requires visibility, cloud, and weather conditions at the same time.
4. VRB must not appear with a directed variation group.
5. Missing mandatory digits as solidus warn on non-AUTO reports.
6. Visibility reporting steps, directional minimum format, AUTO `////`, RVR
   limits, weather pairing, cloud height order, TREND limits, and wind calm /
   gust / high-speed forms emit registry codes.
7. A remarks section after RMK is national. Convert may omit it from IWXXM when
   the operator turns off national remarks.

Operator catalog examples for each code live in the frontend rule-catalog
example map. Session extraction notes are not a substitute for this contract.

## Labeling

| Label | Meaning |
|-------|---------|
| normative | Binding regulation or machine artifact |
| normative-vocabulary | Official coded vocabularies |
| normative-schema | Official XSD or Schematron packages |
| normative-examples | Official paired TAC/XML examples |
| informative | Fixtures or community notes; not binding |

## Automation gaps (outside live-feed refresh)

Live TAC and IWXXM feed refresh, plus WMO schema change signals, do not close
the gaps below. Track them under GitHub issue
[#884](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/884)
(parent epic [#876](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/876)).
RAID: `docs/issues.csv` I-003, `docs/risks.csv` R-003.

### No public TAC grammar API

There is no known public machine-readable grammar or API that defines TAC form
per weather product (for example EBNF or JSON Schema). Lint and encode rules
come from human mining of manuals, vendor examples, and licensed ICAO text,
not from an automated grammar pull.

Do not invent an in-repo "grammar API" that pretends to be that missing source
of truth.

### Annex 3 and PANS-MET stay licensed PDFs

ICAO Annex 3 and Procedures for Air Navigation Services — Meteorology
(PANS-MET, Doc 10157) remain licensed PDFs on the ICAO Store. There is no
Annex 3 / PANS-MET API.

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

These public or vendored sources help CI and mining. They do not replace
Annex 3 or PANS-MET prose.

| Proxy | Useful for | Caveat |
|-------|------------|--------|
| WMO Manual on Codes (FM) and [codes.wmo.int](https://codes.wmo.int/) | Alphanumeric templates; weather and nil vocabularies | Not ICAO SARPs prose |
| Vendored IWXXM XSD / Schematron and official WMO examples | Encode and validate shape for a pin | Not a TAC grammar source of truth |
| National Aeronautical Information Publications (AIPs), FMH-1, regional guides | National or regional practice | Must not override Annex 3 |
| Live public TAC samples | Regression fixtures | Form may be incomplete or national |

## Local feeder

Narrative stubs, mining notes, and quality digs may remain under local
`docs/domain/`. Do not treat those feeders as the clone-time corpus. Update this
contract and `config/` when a rule becomes durable.
