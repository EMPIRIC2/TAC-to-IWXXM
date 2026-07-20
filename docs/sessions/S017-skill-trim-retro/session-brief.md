---
session_id: S017-skill-trim-retro
type: process
status: in_progress
branch: chore/S017-skill-trim-retro
started_at: 2026-07-20
intent: "Skill trim retrospective (RET-001) — corpus-first, lean routing, archive legacy twins"
orchestrator: null
evolve_cycle_id: null
retrospective_cycle_id: RET-001
context_briefs: []
standing_docs_touched: []
---

# Session S017 — skill-trim-retro

## Intent

Run **17-retrospective** cycle **RET-001** to implement the approved skill-trim package:

- Corpus-first routing
- Lean / standard / full presets
- Archive legacy twins
- Split fat skills
- Protocol card
- Batch workflow-state updates
- Stop full-skill attach

## Conflict / prior session

| Item | Disposition |
|------|-------------|
| S016 / EV-012 | **Paused** 2026-07-20 — was `active_session` (feature, 13-deploy-smoke / PR #746). Parked so this process session could open (`D-S017-open`). |
| EV-012 | Remains `in_progress` — resume after RET closes; not deleted. |

## Intake

| ID | Decision |
|----|----------|
| D-S017-open | Park S016; open S017 process; allocate RET-001 |
| D-S017-RET001-aq-waive | AskQuestion waived — written blanket approval; AskQuestion UI unavailable |

## Routing plan

See [routing-plan.md](./routing-plan.md) — **17-retrospective only**.

## Links

- Cycle: `workflow-state.yaml` §`retrospective_cycles` → RET-001
- Skill: `.cursor/skills/17-retrospective/SKILL.md`
