---
session_id: S009-result-card-dismiss
type: hotfix
status: in_progress
branch: fix/S009-result-card-dismiss
started_at: 2026-07-12
intent: "Conversion results Card (manual_input.txt) remains visible after Cancel or Remove/Delete in FileConverter"
orchestrator: 14-hotfix
evolve_cycle_id: null
context_briefs: []
standing_docs_touched: []
---

# Session S009 — Result card dismiss failure

## Intent

After a successful METAR→IWXXM convert in the operator UI, the results `Card` for
`manual_input.txt` (Source TAC + IWXXM XML) stays on screen when the user hits
**Cancel** or the **Remove** (X) control (`aria-label="Remove … from results"`).

## Scope

**In scope**

- Frontend `FileConverter` (and related state) so Remove/Cancel dismisses the results card
- Bug report + repro regression test under `tests/bugs/` / frontend test suite as required by 14-hotfix
- Spec conformance vs F1 conversion UI / UJ convert journeys

**Out of scope**

- New conversion features (F6/F7 product UI)
- Backend convert API changes unless root cause proves server-driven
- Unrelated work-history sidebar behavior (unless it re-hydrates the stuck card)

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Component: `apps/frontend/src/app/components/FileConverter.tsx`
- Corpus: `[Corpus: product]` F1; `[Corpus: system-spec]` Frontend
- Prior remove-path unit coverage: `FileConverter.test.tsx` (remove from results)
