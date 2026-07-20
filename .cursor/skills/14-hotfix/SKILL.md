---
name: 14-hotfix
description: >
  Post-deployment surgical edits for hotfix sessions: bug fixes, patches, small behavioral
  changes, and dependency updates. Open via 00-context (type hotfix) or resume active_session.
  Use for production/local bugs — not new features (16-evolve) or greenfield (pipeline).
---

# 14 — Hotfix

Surgical fix for an **existing** deployed or local failure: one bug, one repro test, one fix.

**Protocol:** [protocol-card.md](../protocol-card.md)  
**Detail:** [reference.md](reference.md) (full phases, interview banks, CI, escalation)  
**Related:** [bug-investigation](../bug-investigation/SKILL.md) · [15-service-health](../15-service-health/SKILL.md)

## Corpus first

Open only as needed ([docs/CORPUS.md](../../docs/CORPUS.md)):

| Always | As symptom requires |
|--------|---------------------|
| product (`feature-list`) + system-spec (`spec.md`) | tech-spec / api / tests / hotfix-log |

Domain deep-dives and guides are **opt-in**.

## When to use / when not

| Use | Do not use |
|-----|------------|
| Bug, regression, config/secret patch | New Fn / multi-doc feature → [16-evolve](../16-evolve/SKILL.md) |
| Small behavioral fix with repro | Greenfield → [pipeline](../pipeline/SKILL.md) |
| Continue open `BUG-*` | Ops-only health → [15-service-health](../15-service-health/SKILL.md) |

## Prerequisites

1. Prefer `active_session` type `hotfix` (via **00-context**).
2. Bug report path under `docs/bug-reports/` (create in Phase 0).
3. Failing repro test before production code change (unless user waives).

## Workflow (summary)

```
Interview (0) → Repro RED (1.25) + user confirms → Investigate (1)
  → Fix until green (2) → Layered verify (2b) → PR/deploy (3–4) → Prevent (5)
```

1. **Phase 0** — AskQuestion intent + intake; create `BUG-*.md` — [reference.md](reference.md) §Phase 0.
2. **Repro** — dedicated failing test under `tests/bugs/`; user confirms match before patch.
3. **Investigate** — logs first (Render/Supabase per infra rules); root cause in bug report.
4. **Fix** — minimal code; repro green; run lint/typecheck/relevant tests.
5. **Verify + deploy** — layers in reference §Phase 2b–4; **never deploy without approval**.
6. **Prevent** — AskQuestion countermeasures / optional Cursor rule; close BUG + hotfix-log.

## State

- Stage key: `stages.14-hotfix`.
- Batch workflow-state updates per [protocol-card.md](../protocol-card.md) §State updates.
- Do not edit `workflow-state.yaml` directly — workflow-state-manager.

## Exit criteria

- [ ] Repro was red, then green (or waived)
- [ ] Bug report complete; hotfix-log row if deployed
- [ ] User approved close (and deploy if applicable)

## Output rules

1. One bug per report / PR when possible.
2. Spec vs code: if corpus wrong, fix docs — do not silently patch around CORPUS.
3. Full interview tables, CI notes, escalation: **reference.md only**.
