# Scoped context — codes.wmo.int aviation registers (#889)

**Status:** active  
**Session:** S055-wmo-aviation-registers / EV-046  
**Created:** 2026-08-08  
**Corpus:** [Corpus: product §F15/F20/F23] [Corpus: tests] · domain opt-in

## Intent

Operational follow-on to closed URL catalog [#719](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/719):
harvest → present → validate → cite → cover against WMO Code Registry, using **vendor
mirror in PR CI** (no live HTML).

**Parent:** Epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)  
**Compose with:** [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) drift ·
[#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) notify (out of scope here)

## Existing artifacts

| Artifact | Role |
|----------|------|
| `docs/domain/rules/RULE_SOURCE_URLS.md` | URL / provenance catalog |
| `docs/domain/mining/codes-wmo-int-aviation-mining-notes.md` | 2026-07-30 dig (transitory) |
| `docs/domain/rules/COVERAGE_MATRIX.md` | Product × theme coverage |
| `vendor/manifest.json` → `iwxxm-codelists` | Pin / offline SoT |
| `vendor/schemas/iwxxm*/**/codes.wmo.int-*.rdf` | Vendored RDF |

## Priority registers (#889)

| Register | TAC / IWXXM use |
|----------|-----------------|
| [49-2](https://codes.wmo.int/49-2) | Weather, recent, cloud, SigWx, AirWx, colour, MetFeature, … |
| [306/4678](https://codes.wmo.int/306/4678) | Significant weather TAC notations |
| [iwxxm](https://codes.wmo.int/iwxxm) | Prefer for colour / MetFeature / nil per pin |
| [common/nil](https://codes.wmo.int/common/nil) (+ iwxxm/nil) | nilReason |

## Lean vs full AC

| Triad element | Lean (this cycle) | Deferred Standard |
|---------------|-------------------|-------------------|
| Present | Inventory + dispositions in docs | Optional live refresh job |
| Validated | Manual/spot matrix notes; no new CI membership asserts | `tac-validate` + matrix vs harvested set |
| Cited | RULE_SOURCE_URLS / mining / matrix / rule provenance | Encode href spot-check automation |
| Cover | Coverage % + exclusions + gap children | Parameterized fixture generation |

## Resolutions (session-local)

| ID | Decision |
|----|----------|
| R1 | Preset Lean — docs/coverage first (`D-S055-open=2`) |
| R2 | Deepen F6/F12/F15/F20/F23/F24/F26/F27/F28/F32; no new Fn |
| R3 | EV-043/EV-044 remain parked |
| R4 | Full F6 product-family coverage % (`D-S055-families=3`) |
| R5 | Waive Validated for Lean; Standard follow-on (`D-S055-validated=1`) |
| R6 | Cite domain docs + ISSUE_CATALOG concept URIs (`D-S055-cite=2`) |
