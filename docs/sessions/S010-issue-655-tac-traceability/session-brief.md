---
session_id: S010-issue-655-tac-traceability
type: feature
status: completed
completed_at: 2026-07-13
branch: evolve/EV-007-issue-655-tac-traceability
started_at: 2026-07-12
intent: "F6 UI input traceability — show original TAC with each conversion result (GitHub #655)"
orchestrator: 16-evolve
evolve_cycle_id: EV-007
context_briefs:
  - docs/context/issue-655-tac-traceability.md
standing_docs_touched: []
---

# Session S010 — Issue #655 TAC traceability UX

## Intent

[GitHub #655](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/655) (parent
[#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)): operators need the
**exact TAC** that produced each IWXXM result — not only the `manual_input.txt` filename.

EV-003 shipped API `tac_input` and a **Source TAC** panel; production still shows filename-only
results per user report. This cycle is a **F6 delta** — UI-only UX hardening + frontend redeploy.

## Approved scope (Phase 0)

**In scope**

- `FileConverter` results cards: always show Source TAC (with client-side fallback when API omits
  `tac_input`), TAC snippet in card header, clearer multi-line mapping, more prominent Source TAC
- Vitest + Playwright updates (TC-001b extension)
- Production **frontend** redeploy (12/13)

**Out of scope**

- API/schema changes (`tac_input` already populated on prod `/api/v1/convert`)
- ZIP sidecar / bulletin UI / convert-bulletin operator surface
- REQ-016 migration rewrites

## Feature mapping

- **F6** — general converter operator UI (delta on input traceability)

## Evidence (2026-07-12)

- Prod API `POST /api/v1/convert` returns `tac_input` for manual METAR (verified live).
- Repo `FileConverter.tsx` has conditional Source TAC panel (`file.originalContent` truthy gate).

## Routing (lean)

00 scoped → 01 delta → 04 delta → 07–13 (skip 02/03/05/06)

## Close

Closed **2026-07-13** after prod Source TAC smoke ([deploy-smoke.md](./reports/deploy-smoke.md)).
PR [#715](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/715) merged; issue #655 closed.
