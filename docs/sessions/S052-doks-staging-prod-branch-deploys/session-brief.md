---
session_id: S052-doks-staging-prod-branch-deploys
type: feature
status: in_progress
branch: evolve/EV-043-doks-staging-prod
started_at: 2026-08-08
intent: "DOKS staging + prod, protect stage/main, dual CI/CD; promote via PR stage→main after staging green (#886)"
orchestrator: 16-evolve
evolve_cycle_id: EV-043
prior_session: S051-output-filename-download-stale
github_issues:
  - 886
feature_ids:
  - F30
preset: Standard
ui_preview: N/A — no product UI feature this cycle
---

# Session S052 — DOKS staging + prod branch deploys

## Goal

Ship dual DOKS environments with protected branches: merge to `stage` auto-deploys
staging; promote via PR into `main` auto-deploys prod only after staging is proven green.

[Corpus: product §F30] [Corpus: deploy] [Corpus: tech-spec] [Corpus: tests]
[Corpus: adr/ADR-033] · [#886](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/886)

## In scope

- DOKS staging namespace + DNS (`api|app.staging.tac-to-iwxxm.com`)
- Protect `stage` / `main` (PR required); GH Environments `staging` / `production`
- CI/CD: `stage`→staging, `main`→prod
- `staging-gate` on PRs to `main` (head must be `stage` + Staging smoke green)
- Docs / ADR amend / skill updates for dual `env_role`

## Out of scope

- App Platform; second DOKS cluster; multi-reviewer prod approvals; product UI features; Render reopen

## Routing

**Standard**: `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
Skip `06` (no new runtime deps).
