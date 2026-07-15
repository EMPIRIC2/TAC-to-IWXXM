---
session_id: S012-empty-bearer-lint-tac
type: hotfix
status: completed
branch: fix/S012-empty-bearer-lint-tac
started_at: 2026-07-15
completed_at: 2026-07-15
pr_url: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/721
merge_sha: 6412b21
intent: "Production frontend sends Authorization: Bearer with empty token to POST /api/v1/lint-tac and /decode-tac → Missing authorization credentials; also lint-tac UI shows only '[lint-tac] N issue(s)' without descriptive issue details"
orchestrator: 14-hotfix
evolve_cycle_id: null
context_briefs: []
standing_docs_touched: []
---

# Session S012 — Empty Bearer lint-tac / decode-tac + lint UX

> **Completed 2026-07-15** — BUG-2026-07-15 resolved; PR [#721](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/721)
> merged (`6412b21`); production verified; Cursor rule
> `frontend-auth-token-hydrate.mdc` approved.

## Intent

Production frontend sends `Authorization: Bearer` with an empty token to
`POST /api/v1/lint-tac` and `POST /api/v1/decode-tac`, which fails with
**Missing authorization credentials**. Separately, the lint-tac UI only shows a
summary like `[lint-tac] N issue(s)` without descriptive issue details.

## Scope

**In scope**

- Fix empty Bearer / missing credentials handling for lint-tac and decode-tac
  (frontend auth header assembly and/or API auth middleware as root cause dictates)
- Surface descriptive lint issue details in the operator UI (not only count summary)
- Bug report + repro regression test per 14-hotfix

**Out of scope**

- F7 evolve cycle resume (S011 / EV-008 / PR #716) — parked until this hotfix closes
- 15-service-health (user approved 14-only routing)
- Unrelated convert / work-history features

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Parked session: [S011-f7-operator-ui](../S011-f7-operator-ui/session-brief.md) (PR [#716](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716))
- Corpus: `[Corpus: api]` lint-tac / decode-tac; `[Corpus: product]` F7 operator UI
- Orchestrator: 14-hotfix
