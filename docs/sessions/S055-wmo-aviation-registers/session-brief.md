---
session_id: S055-wmo-aviation-registers
type: feature
status: completed
branch: evolve/EV-046-wmo-aviation-registers
started_at: 2026-08-08
intent: "Mine codes.wmo.int aviation registers → TAC code verification + fixture coverage (#889)"
orchestrator: 16-evolve
evolve_cycle_id: EV-046
prior_session: S054-rust-ci-crates
github_issues:
  - 889
parent_epic: 846
related_issues:
  - 859
  - 882
  - 719
feature_ids:
  - F6
  - F12
  - F15
  - F20
  - F23
  - F24
  - F26
  - F27
  - F28
  - F32
deepen_feature_ids:
  - F6
  - F12
  - F15
  - F20
  - F23
  - F24
  - F26
  - F27
  - F28
  - F32
preset: Lean
ui_preview: N/A — no browser UI
decision_open: D-S055-open=2
scope_locked: D-S055-families=3 D-S055-validated=1 D-S055-cite=2 D-S055-phase01=1
---

# Session S055 — WMO aviation registers (#889)

## Goal

Document and operationalize present → validated → cited coverage of aviation-relevant
`codes.wmo.int` notations for TAC lint/convert/fixtures — **Lean first**: inventory,
citations, coverage matrix / gap report; defer full standing harvest wiring and
`tac-validate` enforcement loops to a follow-on Standard cycle if needed.

[Corpus: product §F15] [Corpus: product §F20] [Corpus: product §F23] [Corpus: tests]
[Corpus: product] · Epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) ·
[#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889)

## In scope (Lean)

- Harvest **documentation** of sources + offline SoT path (`vendor/schemas/iwxxm-codelists`,
  vendored RDF) with pin/cadence notes vs `vendor/manifest.json`
- **Present** inventory: notations we depend on vs live/vendor; dual-register / prefer-`iwxxm`
  / 404 / obsolete dispositions
- **Cite** updates: `RULE_SOURCE_URLS.md`, mining notes, coverage-matrix rows, rule/fixture
  provenance where a concept URI exists
- **Cover** report: % of priority-register members exercised by TAC fixtures per product
  family; intentional exclusions with cite + reason
- **Gap report**: registry members with no fixture / lint / encode / citation → backlog
  children or deferrals on #846 / #889
- Cross-links to [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) (drift) and
  [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) (notify) — compose, do not
  implement those tickets here

## Out of scope

- Hand-editing `vendor/schemas/*` outside normal sync PRs
- Live `codes.wmo.int` HTML fetches in PR CI
- Replacing XSD/Schematron validation (`iwxxm-validate`)
- Full #882 change-notification pipeline
- Dumping non-aviation trees (`wmdr` / `bufr4` / `grib2` / …)
- **Deferred (not Lean):** standing machine harvest job + automated TAC-token membership
  checks wired into `tac-validate` / matrix CI (follow-on Standard if ACs require)

## Routing

**Lean** (approved `D-S055-open=2`):  
`00 → 16 → 01 → 02`  
Skip `03`–`13` for this Lean docs/coverage pass (see `routing-plan.md`).

## Prior work parked

`D-park-doks=1` — S052/EV-043 and S053/EV-044 remain parked (DOKS). Do not resume for #889.

## Board sync

Project #7 Status → `In progress` when GraphQL rate limit clears (deferred at open).
