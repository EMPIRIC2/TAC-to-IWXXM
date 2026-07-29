# ADR-032: WMO default golden parity + extensible decode glossary

> **Status**: Accepted  
> **Date**: 2026-07-29  
> **Deciders**: User (E20-D3; E20-B=2+3; S02.M2 Batch F)  
> **Stage**: 02-verify-plan  
> **Related**: F24, F25, F9 deepen, F7.g deepen; ADR-025 (summary); feature-list  
> **Session**: S026-airmet-quality-wmo-examples / EV-020

## Context

Operators expect workbench Examples and convert output to match **official WMO IWXXM
examples** shipped under `vendor/schemas/iwxxm/2025-2/IWXXM/examples/`. F23 already
achieves `canonicalize_xml` equality for SIGMET A6-1a/CNL. AIRMET and METAR/SPECI/TAF still
diverge structurally. Separately, decode explanations for SIGMET/AIRMET use category labels
("Hazard phenomenon") instead of English token meanings ("Thunderstorm").

## Decision

1. **Default-settings WMO golden bar (F24/F25)**: A case **passes** when
   `convert(tac, product=…, profile=annex3, iwxxm_version=<default pin>)` yields XML such that
   `canonicalize_xml(ours) == canonicalize_xml(vendor_xml)`. No requirement to match under
   non-default profiles, alternate IWXXM versions, or special flags. Encoder may use stable
   `gml:id` strategy as needed for equality (same pattern as F23).
2. **UI catalog gate (F7.g deepen)**: Examples control lists **only** demos that pass (1) for
   in-scope products; SIGMET keepers retained; translation-failed WMO fixtures are not
   happy-path Examples.
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
