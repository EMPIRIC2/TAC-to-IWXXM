---
session_id: S021-golden-examples-ui
type: feature
status: in_progress
branch: evolve/EV-016-golden-examples-ui
started_at: 2026-07-22
intent: "UI: pre-loaded golden examples for convert + validate (#780) — F7 deepen"
orchestrator: 16-evolve
evolve_cycle_id: EV-016
context_briefs:
  - docs/context/golden-examples-ui.md
standing_docs_touched: []
---

# Session S021 — golden-examples-ui

## Intent

Ship **frontend-only**, pre-loaded **golden examples** in the operator workbench so users
can one-click load curated TAC / AHL bulletin / IWXXM samples for conversion and validation
— no paste required ([#780](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/780)).

Complements F7 sample loaders called out in #714; does **not** change F6/F2 engines or APIs.

## Prior session

| Item | Disposition |
|------|-------------|
| S020 / EV-015 | **Completed** — F20 Done; PR #778 |

## Intake decisions (Phase 0 — locked 2026-07-22)

| ID | Decision |
|----|----------|
| E16-1 | Open `S021-golden-examples-ui` → 16-evolve / **EV-016** |
| E16-2 | Deepen **F7** only (no new Fn) |
| E16-3 | Routing **Lean+build** |
| E16-4 | Scope lock = #780 AC (FE fixtures + Examples UX + Vitest; no backend) |
| AskQuestion | Waived (written interview; UI unavailable) |

## Proposed Fn allocation

| Fn | Title | Role |
|----|-------|------|
| **F7** (deepen) | Multi-product operator UI | Pre-loaded golden examples catalog + FileConverter Examples control |

## Scope (Phase 0 **approved** 2026-07-22)

### In

- Static FE fixtures (`apps/frontend/src/fixtures/examples/` or similar): ≥2 TAC examples per
  product × METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA
- ≥1 AHL bulletin + ≥1 IWXXM COLLECT/XML loadable example
- Product-aware Examples control in `FileConverter` (and validate path when separate)
- On load: set editor body, `product`, `inputMode` when relevant; demo/non-operational labeling
- Prefer annex3 goldens; add ≥1 iwxxm_us METAR/SPECI (TAF if available) from package fixtures
- Copy fixture **content** into frontend — do not import Python packages at runtime
- Vitest: catalog completeness + click-to-load behavior

### Out

- Backend routes, fixture-serving API, DB seeds, env-var changes
- F5/F7 session persistence of examples
- Dissemination / send of demo payloads by default
- Engine quality bars (#731–#741)
- Inventing TAC that cannot round-trip

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Issue: [#780](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/780)
- Related: #714 (umbrella), #702
- Standing: [feature-list.md](../../feature-list.md) F7, [spec.md](../../spec.md),
  [test-plan.md](../../test-plan.md), [user-journeys.md](../../user-journeys.md)
- Context: [golden-examples-ui.md](../../context/golden-examples-ui.md)
- Prior modes: [manual-tac-input-modes.md](../../context/manual-tac-input-modes.md) (ADR-024)
