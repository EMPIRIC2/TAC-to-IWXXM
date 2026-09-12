---
session_id: S016-manual-tac-input-modes
type: feature
status: in_progress
branch: evolve/EV-012-manual-tac-input-modes
started_at: 2026-07-20
intent: "Validate Manual TAC Input modes (TAC / AHL bulletin / IWXXM COLLECT) per #730 / ADR-024"
orchestrator: 16-evolve
evolve_cycle_id: EV-012
context_briefs:
  - docs/context/manual-tac-input-modes.md
standing_docs_touched: []
---

# Session S016 — manual-tac-input-modes

## Intent

Manually and automatically **test and validate** the FileConverter **Manual TAC Input**
control surface ([#730](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/730),
ADR-024): mode toggle, product Auto-detect, AHL → `POST /api/v1/convert-bulletin`, and
IWXXM COLLECT → `POST /api/v1/ingest-collect` (**501** placeholder until member extract).

## Intake decisions (Phase 0 — locked 2026-07-20)

| ID | Decision |
|----|----------|
| E12-1 | Cycle **A**: F7 validation under ADR-024; **no new Fn**; COLLECT stays **501** |
| E12-2 | **All tests green**: Vitest anchors + Playwright T1–T4 + live staging |
| E12-3 | Auto-switch on paste/upload is **required** (T3 fails if missing) |
| E12-4 | Include **13-deploy-smoke** after merge |
| E12-5 / D-S016-EV012-route-1 | **Lean + 13**: 00 → 16 → 01 → 02 → 10 → 13 |

## Scope

### In

- Mode toggle UX (TAC / AHL / COLLECT); helper copy; read-only disable
- TAC report happy path with Product = Auto-detect
- AHL bulletin → `/convert-bulletin` + summary / per-report results (no silent `/convert`)
- IWXXM COLLECT → `/ingest-collect` → **501** as placeholder notice (not success)
- Paste/upload auto-switch (required)
- Playwright T1–T4 under `apps/e2e/`; Vitest regression anchors
- Staging: H4–H5 + authenticated AHL + COLLECT 501
- Corpus deltas: `test-plan.md` / UJ rows; gaps vs H6′ / H7 called out
- Defects from validation → separate bug issues linked from #730

### Out

- Full COLLECT member extract (backend beyond 501)
- Replacing UJ-011 / H7 bulletin API gate design
- Product-matrix convert completeness beyond mode routing
- Flipping F7 → Implemented

## Feature mapping

| Fn | Role |
|----|------|
| **F7** (deepen validation only) | Operator UI input modes (ADR-024); status remains **Planned** |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Issue: [#730](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/730)
- ADR: [ADR-024](../../adr/ADR-024-operator-input-modes.md)
- Corpus: F7, UJ-011, test-plan H6′/H7
- UI: `apps/frontend/src/app/components/FileConverter.tsx`
