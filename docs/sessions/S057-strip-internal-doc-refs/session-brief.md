---
session_id: S057-strip-internal-doc-refs
type: feature
status: in_progress
branch: evolve/EV-048-strip-internal-doc-refs
started_at: 2026-08-08
intent: "Strip internal document references from user-facing UI and API surfaces (#951)"
orchestrator: 16-evolve
evolve_cycle_id: EV-048
prior_session: S056-m0-stabilize-operator-trust
github_issues:
  - 951
milestone: "M0 — Stabilize + operator trust + narrative"
feature_ids: []
deepen_feature_ids:
  - F7
  - F21
feature_note: "Deepen F7 operator UI copy + F21 public OpenAPI/error surfaces; no new product Fn — hygiene for #951"
preset: Standard
ui_preview: "http://localhost:5173/ (non-deployed local Vite)"
decisions:
  D-S057-open: "1 — open S057/EV-048 for #951"
  D-S057-scope: "1 — full #951 UI+OpenAPI+guard"
  D-S057-preset: "1 — Standard (amended from Lean)"
  D-S057-preset-reconfirm: "1 — Standard 00→16→01→02→04→05→07→08→09→10→11; skip 03/06/12/13"
  D-S057-ui-preview: "1 — yes non-deployed local UI"
---

# Session S057 — Strip internal doc refs (#951)

## Goal

Remove internal engineering citations (Corpus tags, ADR/session IDs, `docs/` paths,
UJ/TC/issue numbers) from **operator-visible UI copy** and **public API** surfaces
(OpenAPI descriptions, client-facing errors), and add an automated guard so they
do not regress.

[Corpus: api] [Corpus: product §F7] [Corpus: product §F21] [Corpus: tests]

## Issues

| # | Title | Map |
|---|--------|-----|
| [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951) | Strip internal document references from user-facing UI and API | Deepen **F7** UI + **F21** public API |

## In scope

1. Operator UI: labels, helpers, tooltips, banners, empty states, console/catalog copy, example tier labels, privacy/auth copy
2. Public OpenAPI: path/operation summaries, parameter/schema `description` fields that cite ADR/Corpus/session docs
3. API error/detail messages returned to clients that mention internal doc paths or corpus tags
4. Runtime `/docs` / Redoc text that leaks internal planning vocabulary
5. Automated guard (lint or test) on user-facing string catalogs / OpenAPI export
6. Frontend + backend unit/OpenAPI snapshot tests updated

## Out of scope

- Source comments, module/file docstrings for developers
- Unit/integration test names and test docstrings
- Repo docs under `docs/`, ADRs, session reports, workflow-state
- CI / agent rules that require corpus citations in commits/PRs
- Staging/prod deploy unless later decided (`12`/`13`)

## Routing

**Standard (`D-S057-preset-reconfirm=1`):**  
`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11`  
Skip `03`, `06`, `12`, `13`.

## Branch

`evolve/EV-048-strip-internal-doc-refs` from `stage@d7652d5d`.  
PR target: **`stage`** (not `main`).

## Status

- **00-context:** completed
- **16-evolve:** in_progress → 01-requirements
- **UI preview:** non-deployed local at http://localhost:5173/
