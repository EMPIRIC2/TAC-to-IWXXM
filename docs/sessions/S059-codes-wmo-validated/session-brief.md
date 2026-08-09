---
session_id: S059-codes-wmo-validated
type: feature
status: in_progress
branch: evolve/EV-050-codes-wmo-validated
started_at: 2026-08-09
intent: "Offline harvest + tac-validate membership checks for codes.wmo.int (#959 / #889 Validated)"
orchestrator: 16-evolve
evolve_cycle_id: EV-050
prior_session: S058-ams-2027-abstract
github_issues:
  - 959
parent_epic: 846
related_issues:
  - 889
  - 859
  - 882
feature_ids: []
deepen_feature_ids:
  - F12
  - F15
  - F20
  - F23
  - F24
  - F28
feature_note: "Deepen tac-validate / quality bars — #889 Validated triad; no new product Fn"
preset: Standard
auto_lean: false
ui_preview: N/A — no browser UI
decisions:
  D-S058-park: "1a — park S058/#958; open #959"
  D-S059-ticket: "2a — open S059/EV-050 for #959"
  D-S059-route: "1 — Standard as drafted; handoff 01"
  D-S059-families: "1a — weather+recent+cloud+SIGMET/AIRMET+nil"
  D-S059-fixtures: "2c — aggressive RE*/AIRMET_/SpaceWx/TCU"
  D-S059-882: "3a — design-only #882 compose"
  D-S059-01-ac: "4a — lock AC1–AC6"
---

# Session S059 — codes.wmo.int Validated (#959)

## Goal

Ship the **Validated** follow-on deferred from S055/EV-046: standing offline harvest from
`vendor/schemas/iwxxm-codelists` (+ vendored RDF) and wire `tac-validate` / matrix tests so
weather/phenomena/nil (and agreed) tokens are membership-checked against the harvested set
in CI — without live `codes.wmo.int` HTML in PR CI.

[Corpus: product §F12] [Corpus: product §F15] [Corpus: product §F20]
[Corpus: product §F23] [Corpus: tests] [Corpus: tech-spec]

## Issues

| # | Title | Map |
|---|--------|-----|
| [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) | Standard follow-on: harvest + tac-validate membership | #889 Validated |
| [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) | Parent (Lean present/cite/cover done) | Epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) |

## In scope (locked `D-S059-01-ac=4a`)

1. Standing **offline harvest** from `vendor/schemas/iwxxm-codelists` (+ vendored RDF)
2. Wire `tac-validate` / matrix: weather + recent + cloud + SIGMET/AIRMET phenomena + nilReason
3. **Aggressive** fixtures: `RE*`, AIRMET `_`, SpaceWxPhenomena, TCU (`D-S059-fixtures=2c`)
4. `#882` compose note **design-only** (`D-S059-882=3a`)
5. Close EV-046 gap rows in scope; residual → children/deferrals

## Out of scope

- Hand-edit `vendor/schemas/*`
- Live `codes.wmo.int` HTML in PR CI
- Replacing XSD/Schematron (`iwxxm-validate`)
- Full `#882` notification pipeline
- `#958` AMS abstract (parked S058)
- Promote `stage`→`main` unless separately approved

## Routing

**Standard (approved `D-S059-route=1`):**  
`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
Skip `03`, `06`, `10`, `12`, `13` (no UI/deploy unless later required).

## Branch

`evolve/EV-050-codes-wmo-validated` from `stage` @ tip `849af115`.  
PR target: **`stage`**. Docs scaffolding also in [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964) (open).

## Status

- **00-context:** completed (`D-S059-route=1`)
- **16-evolve:** in_progress (orchestrator)
- **01-requirements:** deltas written — **awaiting user preview / commit** (no push)
- Prior: S058 parked (`D-S058-park=1a`)
