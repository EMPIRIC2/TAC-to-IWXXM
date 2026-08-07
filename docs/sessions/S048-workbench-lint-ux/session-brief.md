---
session_id: S048-workbench-lint-ux
type: feature
status: completed
branch: evolve/EV-040-workbench-lint-ux
started_at: 2026-08-06
completed_at: 2026-08-06
intent: "Workbench lint UX, prefs slim, official AHL/Collect examples, catalog source attribution; fix example lint FPs"
orchestrator: 16-evolve
evolve_cycle_id: EV-040
prior_session: S047-sql-ingest-live-e2e
prior_evolve_cycle_id: EV-039
github_issues: [894]
parent_epic: 840
context_briefs:
  - docs/context/workbench-lint-ux.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/test-plan.md
  - docs/user-journeys.md
  - docs/api-contract.md
  - docs/decisions/evolve-decisions.md
  - docs/domain/rules/ISSUE_CATALOG.md
feature_ids: []
deepen_feature_ids:
  - F7
  - F10
  - F15
feature_note: "Deepen F7/F10/F15 — no new Fn; UI preview accepted"
route_status: completed
current_stage: 16-evolve
ui_preview: accepted
pr_number: 893
pr_status: merged
close_decision_id: D-S048-close
decisions:
  D-S048-open: "Q1=1 Q2=investigate+note+fix FPs Q3=1 Q4=1"
  D-S048-ac: "1"
  D-S048-close: "1,1,1"
---

# Session S048 — workbench-lint-ux

## Intent

Deepen operator workbench UX and lint catalog attribution: full lint console lines,
preserve TAC input on convert, New TAC + action strip above selects, slim prefs to
name/extension, official AHL + IWXXM Collect examples, and clear WMO/ICAO/IWXXM source
lines in the lint issue catalog. Fix two confirmed example lint false positives.
[Corpus: product §F7/F10/F15] [Corpus: api] [Corpus: tests] [Corpus: adr/ADR-028]

## Goal (one sentence)

Ship a clearer workbench lint/UX surface with official bulletin/collect demos and
catalog source attribution, with WMO example lint FPs documented and corrected.

## Status

**Completed** 2026-08-06 — **D-S048-close=1,1,1**: merge PR #893; file+close #894 under #840;
close EV-040/S048; stop. (`route_status: completed`)

## Phase 0 (locked 2026-08-06 — plan approve + chat `1 / investigate+note / 1 / 1`)

| ID | Decision |
|----|----------|
| Q1 | Open **S048** → **EV-040** (feature / Standard) |
| Q2 | Example lint fails are **false positives** — note + fix |
| Q3 | Prefs → name + extension; official AHL + Collect; F22 untouched |
| Q4 | UI preview: **Yes** — non-deployed local |

## Scope

### In

- Lint console: one line per issue (no `+N more` truncation)
- Preserve manual TAC input after Convert / Convert&Send
- New METAR → New TAC; action strip below header, above selects, above bench
- Slim UserPreferences to output name + extension
- Official AHL bulletin + IWXXM Collect examples in Examples catalog
- ISSUE_CATALOG + `/lint-issue-catalog` + FE catalog: source attribution
- Fix `_RVR_OK` tendency U/D; skip AHL YYGGgg for visibility scans

### Out

- F16–F19 dissemination; F8 worker; F22 privacy rewrite; new Fn ids

## False-positive notes (intake)

| Fixture | Code | Verdict |
|---------|------|---------|
| WMO A3-1 `R12/1000U` | `INVALID_RVR` | FP — regex omits ICAO tendency U/D |
| AHL `SAUS31 KZNY 121200` | `INVALID_VISIBILITY` | FP — AHL YYGGgg mistaken for vis |

## Out of scope

See plan EV-040.
