---
session_id: S049-operator-sources-briefing
type: feature
status: in_progress
branch: evolve/EV-041-operator-sources-briefing
started_at: 2026-08-06
intent: "Docs-only: source-centric operator UI runbook + PPT source pack and guided walkthrough"
orchestrator: 16-evolve
evolve_cycle_id: EV-041
prior_session: S048-workbench-lint-ux
prior_evolve_cycle_id: EV-040
context_briefs:
  - docs/context/operator-sources-briefing.md
standing_docs_touched:
  - docs/ops/operator-ui-runbook.md
  - docs/guides/operator-sources-pptx/
  - docs/decisions/evolve-decisions.md
  - docs/domain/README.md
feature_ids: []
deepen_feature_ids:
  - F7
feature_note: "Docs deepen F7 narrative — no new Fn; Lean docs-only"
route_status: in_progress
current_stage: 07-build
ui_preview: n/a
preset: Lean
decisions:
  D-S049-open: "plan approve; deliverables=docs+walkthrough; audience=split"
---

# Session S049 — operator-sources-briefing

## Intent

Produce a **source-centric** operator UI runbook and a PowerPoint **source pack**
(outline, bibliography, image pointers, build walkthrough), then coach building a
personal `.pptx` — without product code or committing copyrighted binaries.
[Corpus: product §F7] [Corpus: system-spec] [docs/domain/rules/ACCESS_AND_CITATION.md]

## Goal (one sentence)

Ship operator + briefing docs that explain **what standards and vendor pins the tool
was built from**, not only how to click the UI.

## Scope

### In

- `docs/ops/operator-ui-runbook.md` — operators, with source cites per surface
- `docs/guides/operator-sources-pptx/` — slide outline, bibliography, image pointers, walkthrough
- Evolve decisions §EV-041; light pointer from domain README / ops
- Interactive PPTX build coaching (chat batches)

### Out of scope

- Product/UI/API code; binary `.pptx` or ICAO/WMO PDFs/PNGs in git
- Rewriting RULE_SOURCE_URLS / PROVENANCE_MAP (consume only)
- Deploy / H4–H5; new Fn; CORPUS membership for ops/guides

## Routing (Lean docs)

`00 → 16 → 01 → 02 → 07 → 08` — skip 03–06, 09–13

## Status

Opened 2026-08-06 from approved plan `operator_sources_docs`.
