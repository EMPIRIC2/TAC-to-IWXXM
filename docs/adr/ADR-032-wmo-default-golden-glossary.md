# ADR-032: WMO default golden parity + extensible decode glossary

> **Status**: Accepted  
> **Date**: 2026-07-29  
> **Deciders**: User (E20-D3; E20-B=2+3; S02.M2 Batch F)  
> **Stage**: 02-verify-plan  
> **Related**: F24, F25, F26, F27, F9 deepen, F7.g deepen; ADR-025 (summary); feature-list  
> **Session**: S026-airmet-quality-wmo-examples / EV-020 (origin); S027 / EV-021 applies same bar to VAA/TCA

## Context

Operators expect workbench Examples and convert output to match **official WMO IWXXM
examples** shipped under `vendor/schemas/iwxxm/2025-2/IWXXM/examples/`. F23 already
achieves `canonicalize_xml` equality for SIGMET A6-1a/CNL. AIRMET and METAR/SPECI/TAF still
diverge structurally. Separately, decode explanations for SIGMET/AIRMET use category labels
("Hazard phenomenon") instead of English token meanings ("Thunderstorm").

## Decision

1. **Default-settings WMO golden bar (F24/F25; also F26/F27)**: A case **passes** when
   `convert(tac, product=…, profile=annex3, iwxxm_version=<default pin>)` yields XML such that
   `canonicalize_xml(ours) == canonicalize_xml(vendor_xml)`. No requirement to match under
   non-default profiles, alternate IWXXM versions, or special flags. Encoder may use stable
   `gml:id` strategy as needed for equality (same pattern as F23). Applies to VAA
   (`va-advisory-A7-2`) and TCA (`tc-advisory-A2-2`) under S027 / EV-021 (E21-2).
2. **UI catalog gate (F7.g deepen)** — **amended S031 / EV-024 (E24-C)**:
   - **Strict passers** (`wmoPass`): demos that satisfy (1) for in-scope products; SIGMET
     keepers retained.
   - **WMO reference samples** (EV-024): official WMO example stems with TAC peers for
     product-in-scope may appear in the Examples / sample menu and **load TAC into the
     workbench** even when convert is not yet `canonicalize_xml`-equal. UI must distinguish
     strict passers from reference samples (badge / copy). Encode gaps stay on child issues.
   - **Still excluded** from happy-path Examples: translation-failed / quarantine WMO fixtures;
     IWXXM-US examples in the WMO catalog; roadmap-only IWXXM-only products (WAFS/QVACI)
     unless a later decision opts them in.
3. **Extensible decode glossary (F9 deepen)**: Prefer **official / near-official** token
   meanings (WMO code lists, Annex 3 / Manual on Codes cites, in-repo domain tables, F3 /
   OpenAIP names when resolvable). Ship a versioned YAML/JSON file as **overrides / additions**
   on top of those sources (not the sole authority). Explanations prefer official meaning, then
   YAML override, then category fallback. On OpenAIP/F3 miss, keep ICAO designator — decode
   must not fail.
4. **API**: Keep `POST /api/v1/decode-tac` response shape (`summary`, `segments`, `residuals`).
   No new required fields in v1 of this cycle; richer explanation strings only (backward
   compatible). Optional additive fields only if 04 proves necessary (document in api-contract).
5. **Glossary path**: Default packaged file under
   `packages/tac2iwxxm/src/tac2iwxxm/data/decode_glossary.yaml` (or equivalent); optional env
   override `TAC2IWXXM_DECODE_GLOSSARY_PATH` for operator/maintainer overlays (E20-E2).

## Alternatives considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Require golden match for all profiles/versions | Out of scope; user: “match on default” |
| 2 | Strip all gml:ids before compare | Looser than F23; rejected (E20-D3=1) |
| 3 | LLM-generated explanations | Non-deterministic; conflicts ADR-025 |
| 4 | Hard-fail decode when OpenAIP unavailable | Breaks offline/CI; rejected |

## Consequences

- Multi-milestone encode work for METAR/SPECI/TAF/AIRMET under F25/F24.
- New package data file(s) for glossary; config-spec documents path/override if any.
- 11-verify-impl signs off F24/F25 AC explicitly (routing C=1).
- **EV-024**: Sample menu can grow with official WMO reference stems without waiting for
  encode equality; operators must still see which demos are strict passers vs reference.
  `FIXTURE_GAPS.md` / catalog tests track both tiers (**UJ-039** / TC-EV024-*).
