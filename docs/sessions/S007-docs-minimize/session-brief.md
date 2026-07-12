---
session_id: S007-docs-minimize
type: process
status: completed
close_note: "Closed at S008 open; 18-pr-review skipped"
branch: docs/S007-docs-minimize
started_at: 2026-07-12
intent: "Minimize docs/ root files; nest non-standing docs (conservative layout)"
orchestrator: null
evolve_cycle_id: null
context_briefs: []
standing_docs_touched:
  - docs/README.md
  - docs/decisions/*
  - docs/ops/*
  - docs/guides/*
  - docs/domain/*
  - docs/reports/*
---

# Session S007 — docs-minimize

## Intent

Cut `docs/` root down to standing pipeline specs plus a README index. Move historical,
domain, ops, guide, and report docs into organized folders without changing product behavior.

## Scope

**In**

- Reorganize `docs/` tree (conservative): standing specs stay at root
- Update broken relative links and known skill/rule path references for moved files
- Add `docs/README.md` as the tree index

**Out**

- Product/feature changes
- Nesting standing specs (`feature-list.md`, `spec.md`, etc.) — deferred (aggressive option)
- Deleting content (archive only via existing `ARCHIVE/` if needed)

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Standing: [feature-list.md](../../feature-list.md), [spec.md](../../spec.md), [skill-routing.md](../../skill-routing.md)
