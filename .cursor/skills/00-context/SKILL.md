---
name: 00-context
description: >
  Recommended entry for every work session. Classifies session type (greenfield, feature,
  hotfix, integration, new_service, ops, process), allocates SNNN-slug, writes session-brief
  and routing-plan, sets active_session. Also gathers context: project mode writes
  docs/context-brief.md; scoped mode writes docs/context/<slug>.md. Re-invokable for mid-project
  discovery. Use before requirements, features, live E2E, integrations, or evolve cycles.
---

# 00 — Context Gathering

Open sessions and produce context briefs for downstream skills.

**Protocol:** [protocol-card.md](../protocol-card.md)  
**Detail:** [reference.md](reference.md) (Phase 1A–1C detail, ecosystem scan, templates)  
**Routing:** [docs/skill-routing.md](../../docs/skill-routing.md)

## Corpus first

| Mode | Open |
|------|------|
| Session / routing | `docs/CORPUS.md` + existing `feature-list` / `spec` if present |
| Scoped feature | product + system-spec rows for touched Fn only |
| Project greenfield | Full discovery; template via [template-registry.md](../template-registry.md) |

Do not dump `docs/domain/**` unless the scope is domain mining.

## Invocation modes

| Mode | When | Output |
|------|------|--------|
| **session** (default) | Any bounded work | `docs/sessions/SNNN-slug/` + optional context |
| **project** | Greenfield / first brief | `docs/context-brief.md` |
| **scoped** | Feature / evolve / mid-project | `docs/context/<slug>.md` |
| **resume** | `active_session` exists | Continue routing-plan |

### Session type → orchestrator

| Type | Next |
|------|------|
| `greenfield` | [pipeline](../pipeline/SKILL.md) |
| `feature` / `new_service` | [16-evolve](../16-evolve/SKILL.md) |
| `hotfix` | [14-hotfix](../14-hotfix/SKILL.md) |
| `integration` / `ops` / `process` | First stage in routing-plan |

## Routing presets (AskQuestion)

Default for **existing apps**: **Lean**.

| Preset | Stages |
|--------|--------|
| **Lean** | `00 → 16 → 01 → 02 → 10 → 13` (+ hotfix/ops overrides) |
| **Standard** | Lean + `04 → 07 → 08 → 09 → 11 → 12` |
| **Full** | Standard + `03` / `05` / `06` / greenfield extras |

Record choice + skip rationale in `routing-plan.md`.

## Phase 0 — Session open

1. If `active_session` exists: AskQuestion — resume / close+new / abandon.
2. Classify session type; `open_session` → `S{NNN}-{slug}`.
3. Write `session-brief.md` + propose `routing-plan.md` (preset above).
4. AskQuestion — approve/edit plan; set `active_session`; create branch.
5. Hand off to orchestrator / first stage.

## Context phases (abbreviated)

| Phase | Project | Scoped |
|-------|---------|--------|
| 1A agents | paper/repo/docs as needed | subset for scope |
| 1B ecosystem | optional — [reference.md](reference.md) | skip unless cross-repo |
| 1C template | classify — [reference.md](reference.md) | skip (use existing) |
| 2–3 issues | cross-ref + AskQuestion | scope-only |
| 4 brief | `context-brief.md` | `docs/context/<slug>.md` + index |

**Anti-bloat:** never append scoped findings into `docs/context-brief.md`.

## State

- Stage key: `stages.00-context`; batch updates per protocol-card.
- **00** opens sessions — does not require pre-existing `active_session`.

## Exit criteria

- [ ] Session allocated (or waived) with approved routing-plan
- [ ] Context brief written when mode requires it
- [ ] Next orchestrator / stage identified
