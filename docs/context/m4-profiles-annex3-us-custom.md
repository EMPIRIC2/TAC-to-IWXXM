# Scoped context: Milestone 4 profiles (Annex 3 + US + custom)

> **Status**: active  
> **Created**: 2026-09-06  
> **Session**: `EV-m4-profiles-annex3-us-custom`  
> **Ticket**: [Milestone 4](https://github.com/EMPIRIC2/TAC-to-IWXXM/milestone/4)  
> **Corpus**: [Corpus: product §F35] [Corpus: product §F36] [Corpus: product §F7.w] [Corpus: domain-profiles] [Corpus: api] [Corpus: tests] [Corpus: journeys] [Corpus: adr/ADR-036]

## Goal

Frame milestone 4 as a single profile-oriented evolve stream spanning semantic and exchange
profile architecture, national/regional profile content, ConversionProfile editing, cross-version
profile conversion framing, operator sharing, and the remaining quality-matrix backlog so later
spec and build work stay aligned to approved corpus boundaries. [Corpus: product §F35] [Corpus:
product §F36] [Corpus: product §F7.w]

## Scope anchors

- **Architecture baseline:** semantic versus exchange profile split is already implemented and
  remains the milestone backbone; semantic ids, exchange ids, alias window, and fail-closed
  unknown ids are already defined. [Corpus: product §F35] [Corpus: api]
- **Profile content baseline:** national semantic and regional exchange profile content is the
  active deepen lane, with `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET`, thin/compat
  nationals, and regional exchange overlays tracked under the standing profile corpus. [Corpus:
  product §F36] [Corpus: domain-profiles]
- **Operator UI baseline:** the ConversionProfile editor is already a documented operator/auth
  surface with rule-pack CRUD, inspector, and signed overlays, and later milestone work must not
  regress the lighter workbench profile picker. [Corpus: product §F7.w] [Corpus: journeys]
- **Verification baseline:** milestone work inherits existing route coverage around semantic and
  exchange profile selection, ConversionProfile flows, and must-not-break FE regressions. [Corpus:
  tests] [Corpus: journeys]

## Milestone-issue map

| Issue | Context role |
|------|--------------|
| [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912) | Umbrella for multi-national semantic profiles and regional exchange overlays |
| [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913) | Authoritative-source mining and durable profile evidence |
| [#908](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/908) | Cross-version conversion framing between supported IWXXM lines |
| [#933](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/933) | ConversionProfile editor and signed overlay workflow |
| [#1050](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1050) | National report variants beyond the current API product enum |
| [#1051](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1051) | Operator sharing of semantic conversion profiles and secure dissemination destinations |
| [#970](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/970) | Remaining profile-quality RuleCases / fixture matrix fill |

Milestone 4 is therefore not a net-new feature family; it is a coordinated deepen across the
already approved F35, F36, and F7.w surfaces. [Corpus: product §F35] [Corpus: product §F36]
[Corpus: product §F7.w]

## Primary journeys and must-not-break surfaces

- **Primary operator journey:** `UJ-072` remains the strongest end-user anchor because it spans
  inspect → rule pack → overlay → convert and explicitly requires the existing light semantic /
  exchange picker and dissemination drawer to stay green. [Corpus: journeys] [Corpus: tests]
- **Adjacent operator journey:** `UJ-069` anchors semantic convert → exchange package behavior and
  keeps the semantic versus exchange split honest for both docs and future implementation. [Corpus:
  journeys] [Corpus: tests]
- **Protected surfaces from intake:** current profile picker behavior and the dissemination drawer
  must not regress while milestone 4 evolves. [Corpus: journeys §UJ-072] [Corpus: tests
  §TC-EV933-006]

## Build intent to record now

If the documenting-to-implementing gate later opens, anticipated implementation surfaces are:
`apps/frontend`, `apps/backend`, `packages/tac2iwxxm`, `packages/tac-validate`,
`packages/iwxxm-validate`, and profile corpus/docs under `docs/domain/profiles/`, with H4-H5
coverage needed for operator-facing changes and T0/T2/T3 coverage retained for profile contract
and registry flows. [Corpus: system-spec] [Corpus: tests] [Corpus: api]

## Non-goals for this intake

- No GitHub issue or PR mutation.
- No build-band implementation before a separate gate decision.
- No conflation of semantic/exchange profile selection with dissemination credentials or saved
  destination secrets. [Corpus: product §F35] [Corpus: product §F7.w] [Corpus: adr/ADR-036]
