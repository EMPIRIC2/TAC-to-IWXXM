---
name: pipeline
description: >
  Greenfield session orchestrator: runs stages 00-context through 13-deploy-smoke for a new
  project inside an active_session with type greenfield. Requires 00-context to open the session
  and approve routing-plan.md (recommended). Combines phase gates, transition checks, and
  connectivity gates. Expects Plan-compatible handoffs (Build Plan Card) from 04 into 07;
  SwitchMode → Plan in 16/04/07 only. Post-deployment work uses other session types.
  Use when building from scratch with an approved greenfield routing plan.
---

# Pipeline

**Greenfield session orchestrator** — requirements through deploy inside `active_session` type
`greenfield`.

**Protocol:** [protocol-card.md](../protocol-card.md)  
**Detail:** [reference.md](reference.md) (phase diagrams, gate tables, inputs)  
**Routing:** [docs/skill-routing.md](../../docs/skill-routing.md)

## Prerequisites

1. **00-context** opened a `greenfield` session; user approved `routing-plan.md`.
2. `active_session.orchestrator` is `pipeline`.
3. If `active_session` is null → [00-context](../00-context/SKILL.md).

## Not for

| Need | Use |
|------|-----|
| Feature on existing app | [16-evolve](../16-evolve/SKILL.md) |
| Bug / patch | [14-hotfix](../14-hotfix/SKILL.md) |
| Process / skill trim | [17-retrospective](../17-retrospective/SKILL.md) |

## Phase map

```
A Product:  00 → 01 → 02 → 03
B Tech:     04 → 05 → 06     (Plan only in 04; card from 04; 05–06 Agent)
C Build:    07 ◄── 08        (Plan = next batch; Agent = Task Loop)
D Verify:   09 + 10 → 11 → 12 → 13
```

On-demand after: 14 / 15 / 16 / 17 / 18 / 19.

**Preset:** greenfield defaults to **Full**. Existing-app work must not use this orchestrator.

**Plan ↔ Agent:** [plan-mode-loop.md](../plan-mode-loop.md). SwitchMode → Plan in **16**
(orchestrator), **04**, and **07**; earlier product stages are Plan-compatible producers.

## Corpus first

Per stage band in [docs/CORPUS.md](../../docs/CORPUS.md) §Skill obligations — open those rows
only when entering that stage. Do not preload all corpus docs at pipeline start.

## Orchestration rules

1. Run **one** child skill at a time (except 09+10 parallel).
2. Phase gates A→B, B→C, C→D, deploy — block on failure; fix in place ([considerations.md](../considerations.md) §2).
3. Batch state updates per protocol-card (start + exit per stage).
4. Child skills own detail — read child `SKILL.md` when invoking; `reference.md` on failure.

## Connectivity

Cumulative checklist: [connectivity-gates.md](../connectivity-gates.md). Hybrid UI+API never
“API-only done.”

## Exit criteria

- [ ] Routed stages completed or waived with rationale
- [ ] Build Plan Card present when 04+ ran (Plan-compatible handoff)
- [ ] Deploy smoke (13) done or explicitly deferred
- [ ] Session close AskQuestion when routing-plan complete

## Additional resources

- Full gates, inputs, overview diagram → [reference.md](reference.md)
- Shared conventions → [pipeline-preamble.md](../pipeline-preamble.md)
