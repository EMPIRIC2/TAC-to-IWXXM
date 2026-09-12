---
session_id: S001-convert-send-buttons
type: feature
status: in_progress
branch: feat/S001-convert-send-buttons
started_at: 2026-06-22
intent: "Add Convert and Convert&Send buttons to the converter UI (GitHub #656)"
orchestrator: 16-evolve
evolve_cycle_id: null
context_briefs:
  - docs/context/convert-send-buttons.md
standing_docs_touched: []
github_issue: https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656
---

# Session S001 — convert-send-buttons

## Intent

Implement clearer convert vs convert-and-send workflow in the main converter UI per
[GitHub issue #656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656),
following initial user feedback in [issue #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555).

## Scope

**In scope (issue #656)**

- Explicit **Convert** action (conversion only).
- **Convert&Send** action (convert then immediately upload/send output).
- Success/failure feedback for the send step (partially exists via upload dialog toasts).

**Likely out of scope (issue #555 siblings — confirm via routing/decisions)**

- Auto-clear / overwrite previous METAR input panel without manual close.
- In-app error log preview.

**Constraints**

- Maps to **F1** (conversion UI) + existing Supabase database upload path.
- No backend API changes expected unless evolve adds upload defaults endpoint.
- Monorepo targets: `apps/frontend/`, `apps/e2e/`.

## Current state (discovery)

| Capability | Status | Location |
|------------|--------|----------|
| Convert button | **Exists** | `apps/frontend/src/app/components/FileConverter.tsx` |
| Upload to Database (manual 2-step) | **Exists** | `FileConverter.tsx` → `DatabaseUploadDialog.tsx` |
| Convert&Send (one-click) | **Missing** | — |
| Upload API | **Exists** | Supabase `POST .../database/upload` |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Scoped context: [convert-send-buttons.md](../../context/convert-send-buttons.md)
- Standing: [feature-list.md](../../feature-list.md), [user-journeys.md](../../user-journeys.md), [test-plan.md](../../test-plan.md)
- Parent feedback: GitHub #555
