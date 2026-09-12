---
session_id: S013-live-decode-preview-ux
type: feature
status: completed
branch: evolve/S013-live-decode-preview-ux
started_at: 2026-07-16
completed_at: 2026-07-18
intent: "Value-aware live TAC decode translations + plain-language report summary (F9); workbench IWXXM preview pane + soft-fail/terminator lint UX clarity (F10)"
orchestrator: 16-evolve
evolve_cycle_id: EV-009
pr_url: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/723
merge_sha: 4660602
context_briefs:
  - docs/context/f7-operator-ui.md
standing_docs_touched: []
---

# Session S013 — live-decode-preview-ux

## Intent

User feedback on the F7 operator workbench (post-#716):

1. The Code | Explanation decode panel should translate **actual values**, not just group
   labels — e.g. `24/18` → "Temperature 24 °C, dewpoint 18 °C" — updating live while typing.
2. A **natural-language description** of the whole report should appear as a live
   "Plain language" block at the top of the decode panel.
3. It is unclear **where Soft-preview / Live IWXXM output appears** — add a dedicated
   side-by-side IWXXM preview pane inside the workbench.
4. `MISSING_TERMINATOR` and `LAYER12_SOFT_FAIL` messages confused the user — reword the
   soft-fail status copy, downgrade the terminator lint to an info-level hint, and add a
   one-click "Add `=`" quick fix in the editor.

## Scope

**In scope**

- F9 — Value-aware decode segments for all 7 TAC products (METAR/SPECI/TAF rich;
  SIGMET/AIRMET/VAA/TCA best-effort) + deterministic backend-built `summary` string in the
  decode-tac response; frontend renders it live in the decode panel.
- F10 — Side-by-side IWXXM preview pane in the workbench (anchors Soft-preview and
  Live IWXXM output); clearer `LAYER12_SOFT_FAIL` status copy; `MISSING_TERMINATOR`
  info-level + "Add `=`" quick fix.

**Out of scope**

- LLM/AI-generated summaries (deterministic template text only).
- Changes to Layer 1–2 validation semantics or Schematron rules.
- F5 work history, F7 session management surfaces not touched by the preview pane.

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Standing: [feature-list.md](../../feature-list.md), [spec.md](../../spec.md),
  [test-plan.md](../../test-plan.md), [api-contract.md](../../api-contract.md)
- Context: [f7-operator-ui.md](../../context/f7-operator-ui.md)
