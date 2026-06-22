# Skill routing

Quick reference for which `.cursor/skills/` stage to invoke. Full conventions:
[pipeline-preamble.md](../.cursor/skills/pipeline-preamble.md).

## Decision tree

```
Does the repo already have docs/feature-list.md + deployable code?
│
├─ NO  → pipeline (greenfield 00–13)
│
└─ YES → What kind of work?
         │
         ├─ Bug / regression / small surgical patch
         │    → 14-hotfix
         │
         ├─ Production health / ops investigation (no feature intent)
         │    → 15-service-health
         │
         ├─ New feature(s), scope change, API/arch change, large refactor,
         │  new dependency, multi-doc spec update, breaking change
         │    → 16-evolve  ← default for "add X" on existing app
         │
         ├─ Lessons learned / improve pipeline skills (no product change)
         │    → 17-retrospective
         │
         ├─ Review an open PR (post findings, no merge)
         │    → 18-pr-review
         │
         └─ Fix findings after PR review (no merge)
              → 19-address-pr-review
```

## By user phrase

| You say… | Skill |
|----------|-------|
| "Build this from scratch" / "run the pipeline" | [pipeline](../.cursor/skills/pipeline/SKILL.md) |
| "Add feature X" / "new capability" / "implement Fn" | [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "Large refactor" / "change the API" / "new architecture" | [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "Update scope" / "breaking change" / "migrate to …" | [16-evolve](../.cursor/skills/16-evolve/SKILL.md) |
| "Fix this bug" / "hotfix" / "regression in prod" | [14-hotfix](../.cursor/skills/14-hotfix/SKILL.md) |
| "Check production health" / "staging is broken" | [15-service-health](../.cursor/skills/15-service-health/SKILL.md) |
| "Retrospective" / "improve our process" | [17-retrospective](../.cursor/skills/17-retrospective/SKILL.md) |
| "Review this PR" | [18-pr-review](../.cursor/skills/18-pr-review/SKILL.md) |
| "Address review comments" / "fix PR feedback" | [19-address-pr-review](../.cursor/skills/19-address-pr-review/SKILL.md) |

## Change magnitude (existing app)

| Magnitude | Examples | Skill |
|-----------|----------|-------|
| **Surgical** | One bug, typo, config tweak, dependency patch | 14-hotfix |
| **Medium** | Single new Fn, one new endpoint + specs, scoped UI panel | 16-evolve |
| **Large** | Multi-service change, API redesign, monorepo migration, new deploy target | 16-evolve (full routing plan) |
| **General** | Scope/API/acceptance change without a clean Fn label | 16-evolve (`cycle_type: general`) |

When magnitude is unclear, start **16-evolve** Phase 0 intake — it classifies and routes.

## 16-evolve vs 14-hotfix

| Criterion | 14-hotfix | 16-evolve |
|-----------|-----------|-----------|
| New row in `feature-list.md` | No | Yes (typical) |
| Updates multiple spec docs | Rarely | Often |
| Needs execution-plan tasks | No | Yes |
| User-visible new capability | No | Yes |
| Architectural / breaking change | No | Yes |
| Mandatory phase checkpoints A–D | No | Yes |

## Active evolve cycle

Once **16-evolve** opens a cycle (`evolve/{id}-{slug}` branch), child stages **00–15** run in
**delta mode** with `feature_ids` and `evolve_cycle_id`. Invoking **07-build** or **01-requirements**
directly is allowed **only** when a cycle is active or user waives orchestration (logged in
`workflow-state.yaml`).

## Numbered stages (00–19)

| Range | Phase | Purpose |
|-------|-------|---------|
| 00–03 | A — Product planning | Specs and plan guardrails |
| 04–06 | B — Technical planning | Execution plan and dev tooling |
| 07–08 | C — Build | Implementation |
| 09–13 | D — Verify & deploy | QA, E2E, deploy |
| 14–15 | E — Maintenance | Hotfix, health |
| 16 | F — Evolve | **Features & large changes** |
| 17 | F — Learn | Retrospective |
| 18–19 | G — Review | PR review and remediation |
