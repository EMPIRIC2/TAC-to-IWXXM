---
session_id: S006-issue-664-output-filename
type: feature
status: completed
branch: feat/S006-issue-664-output-filename
started_at: 2026-06-25
completed_at: 2026-07-12
intent: "#664 — allow a custom output filename for manual METAR input (frontend-only; blank ⇒ manual_input)"
orchestrator: 16-evolve
evolve_cycle_id: EV-005
pr_url: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/695
context_briefs:
  - docs/context/issue-664-output-filename.md
standing_docs_touched:
  - docs/feature-list.md
github_issue: https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664
supersedes_session: null
close_note: "PR #695 merged 2026-06-25; user waived 11-verify-impl; docs reorg unblocked"
---

# Session S006 — Issue #664 custom output filename (manual input)

## Intent

Let users set a custom output filename before converting/downloading a **manually entered** METAR/SPECI.
Today every manual conversion downloads as `manual_input.xml` (`manual_input_N.xml` for multi-line). Per
[GitHub #664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664), add an optional filename
field; when blank, keep the existing `manual_input` default.

## Scope

**In scope (frontend-only — F1)**

- Optional "output filename" input near the manual TAC textarea.
- Apply the custom base name to manual-derived download (single file + ZIP entry) and result-card label.
- Sanitize the name; blank ⇒ `manual_input`; multi-line ⇒ `_1/_2` suffix (assumed, confirm in evolve).

**Out of scope**

- Backend `ConversionResult.name` / `manual_input` naming (no API contract change).
- Renaming file-upload outputs (only manual input).
- Renaming the batch ZIP archive itself.
- F5 persistence of the custom name (unless user requests).

## Key decisions (2026-06-25 intake)

| Topic | Decision |
|-------|----------|
| Layer | Frontend-only (R1) |
| Default | Blank ⇒ `manual_input` (R2) |
| Applies to | Manual input results only; uploads unchanged (R3) |
| Multi-line | `_1/_2` suffix on custom base — assumed (R4) |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- [issue-664-output-filename.md](../../context/issue-664-output-filename.md)
- [feature-list.md §F1](../../feature-list.md)
