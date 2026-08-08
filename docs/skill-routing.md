# Skill routing

Quick reference for which `.cursor/skills/` stage to invoke. Short shared rules:
[protocol-card.md](../.cursor/skills/protocol-card.md). Full conventions:
[pipeline-preamble.md](../.cursor/skills/pipeline-preamble.md) and
[sessions-reference.md](../.cursor/skills/sessions-reference.md).

## Routing presets (00 / 16)

Default for **existing apps**: **Lean**. Greenfield uses **Full** via [pipeline](../.cursor/skills/pipeline/SKILL.md).

| Preset | Typical stages | When |
|--------|----------------|------|
| **Lean** | `00 → 16 → 01 → 02 → 10 → 13` | UX/docs/tests; no API/arch change |
| **Standard** | Lean + `04 → 07 → 08 → 09 → 11 → 12` | New Fn / contract change |
| **Full** | Standard + `03` / `05` / `06` as needed | New guardrails, stack change, greenfield |

Record the preset and skip rationale in `docs/sessions/SNNN-slug/routing-plan.md`.

## Session-first entry (recommended)

```
User has work to do (any magnitude)
        │
        ▼
   00-context  ← recommended entry; classifies session type + routing plan
        │
        ├─ greenfield ──► pipeline (greenfield session orchestrator)
        ├─ feature / new_service ──► 16-evolve
        ├─ hotfix ──► 14-hotfix
        ├─ integration ──► 10-e2e, 11-verify-impl, 15-service-health (per plan)
        ├─ ops ──► 15-service-health
        └─ process ──► 17 / 18 / 19
        │
        ▼
   Stages in approved routing-plan.md (docs/sessions/SNNN-slug/)
```

**01-requirements** may be entry when project/scoped context already exists — agent still
requires `active_session` unless waived.

## Decision tree (existing app)

```
Does the repo already have docs/feature-list.md + deployable code?
│
├─ NO  → 00-context → greenfield session → pipeline (00–13)
│
└─ YES → 00-context (recommended) → session type?
         │
         ├─ Bug / regression / small surgical patch
         │    → hotfix session → 14-hotfix
         │
         ├─ Production health / ops (no product change)
         │    → ops session → 15-service-health
         │
         ├─ New feature(s), scope change, API/arch change, large refactor
         │    → feature session → 16-evolve
         │
         ├─ New deployable in monorepo
         │    → new_service session → 16-evolve (or direct 04→07 per plan)
         │
         ├─ Live E2E / staging integration / connectivity
         │    → integration session → 00 scoped, 10, 11, 15
         │
         ├─ Lessons learned / improve pipeline skills
         │    → process session → 17-retrospective
         │
         ├─ Review an open PR
         │    → process session → 18-pr-review
         │
         └─ Fix findings after PR review
              → process session → 19-address-pr-review
```

## By user phrase

| You say… | Session type | Skill |
|----------|--------------|-------|
| "Build this from scratch" / "run the pipeline" | greenfield | [00-context](../.cursor/skills/00-context/SKILL.md) → [pipeline](../.cursor/skills/pipeline/SKILL.md) |
| "Add feature X" / "new capability" / "implement Fn" | feature | [00-context](../.cursor/skills/00-context/SKILL.md) → [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "New service" / "new app in monorepo" | new_service | [00-context](../.cursor/skills/00-context/SKILL.md) → [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "Large refactor" / "change the API" | feature | [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "Live E2E" / "staging integration" | integration | [00-context](../.cursor/skills/00-context/SKILL.md) → 10 / 11 / 15 |
| "Fix this bug" / "hotfix" | hotfix | [14-hotfix](../.cursor/skills/14-hotfix/SKILL.md) |
| "Check production health" | ops | [15-service-health](../.cursor/skills/15-service-health/SKILL.md) |
| "Retrospective" | process | [17-retrospective](../.cursor/skills/17-retrospective/SKILL.md) |
| "Review this PR" | process | [18-pr-review](../.cursor/skills/18-pr-review/SKILL.md) |
| "Address review comments" | process | [19-address-pr-review](../.cursor/skills/19-address-pr-review/SKILL.md) |

## Change magnitude (existing app)

| Magnitude | Examples | Session type | Skill |
|-----------|----------|--------------|-------|
| **Surgical** | One bug, typo, config tweak | hotfix | 14-hotfix |
| **Medium** | Single new Fn, one endpoint + specs | feature | 16-evolve |
| **Large** | Multi-service, API redesign, migration | feature | 16-evolve (full routing plan) |
| **General** | Scope/API change without clean Fn | feature | 16-evolve (`cycle_type: general`) |

When magnitude is unclear, start **00-context** — it classifies and proposes routing plan.

## Active session

Once **00-context** opens a session (`active_session` in `workflow-state.yaml`), child stages
**00–19** run per `docs/sessions/SNNN-slug/routing-plan.md`. Invoking **07-build** or
**01-requirements** directly is allowed **only** when `active_session` exists and lists that stage.

## Plan ↔ Agent (Cursor modes)

See [plan-mode-loop.md](../.cursor/skills/plan-mode-loop.md).

| Skill | Mode |
|-------|------|
| **16-evolve** | Plan = **default orchestrator** (Phase 0–1 + re-routes); Agent runs child stages |
| **04-tech-plan** / **07-build** | Plan = execution structure / next milestone batch; Agent = write files / Task Loop |
| **00–03, 05–06, 08–15** | Agent only (Plan-compatible seeds/gates where noted) |

## 16-evolve vs 14-hotfix

| Criterion | 14-hotfix | 16-evolve |
|-----------|-----------|-----------|
| Session type | hotfix | feature / new_service |
| New row in `feature-list.md` | No | Yes (typical) |
| Updates multiple spec docs | Rarely | Often |
| Needs execution-plan tasks | No | Yes |
| User-visible new capability | No | Yes |

## DOKS promote to main (F30 / ADR-034)

After dual-env CD (EV-043/044): **never** merge feature branches to `main`. Path is
feature → PR → `stage` → **Staging smoke** green → PR **`stage`→`main`** → **Staging gate**
→ prod Deploy. See [docs/deploy.md](deploy.md) §Promote and
`.cursor/rules/optional/doks-promote-from-stage.mdc`.

## Numbered stages (00–19)

| Range | Phase | Purpose |
|-------|-------|---------|
| 00–03 | A — Product planning | Specs and plan guardrails |
| 04–06 | B — Technical planning | Execution plan and dev tooling |
| 07–08 | C — Build | Implementation |
| 09–13 | D — Verify & deploy | QA, E2E, deploy |
| 14–15 | E — Maintenance | Hotfix, health |
| 16 | F — Evolve | Feature / new_service session orchestrator |
| 17 | F — Learn | Retrospective |
| 18–19 | G — Review | PR review and remediation |

## Legacy skills (do not invoke)

| Stub | Use instead |
|------|-------------|
| `gather-context` | [00-context](../.cursor/skills/00-context/SKILL.md) |
| `doc-planner` | [01-requirements](../.cursor/skills/01-requirements/SKILL.md) |
| `audit-docs` | [02-verify-plan](../.cursor/skills/02-verify-plan/SKILL.md) / [05-verify-tech](../.cursor/skills/05-verify-tech/SKILL.md) |
| `build-planner` | [04-tech-plan](../.cursor/skills/04-tech-plan/SKILL.md) |
| `build-executor` | [07-build](../.cursor/skills/07-build/SKILL.md) |
| `verify-build` | [08-verify-build](../.cursor/skills/08-verify-build/SKILL.md) |
| `deploy-verify` | [13-deploy-smoke](../.cursor/skills/13-deploy-smoke/SKILL.md) |

Archives: [.cursor/skills/_archive/](../.cursor/skills/_archive/README.md).
