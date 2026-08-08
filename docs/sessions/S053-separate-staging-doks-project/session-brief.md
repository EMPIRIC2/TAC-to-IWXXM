---
session_id: S053-separate-staging-doks-project
type: feature
status: in_progress
branch: evolve/EV-044-separate-staging-doks
started_at: 2026-08-08
intent: "Separate staging DOKS (+ DO project Staging TAC-to-IWXXM) from prod cluster; amend ADR-034 shared-cluster decision"
orchestrator: 16-evolve
evolve_cycle_id: EV-044
prior_session: S052-doks-staging-prod-branch-deploys
feature_ids:
  - F30
preset: Standard
ui_preview: N/A — no product UI feature this cycle
---

# Session S053 — Separate staging DOKS under DO Project

## Goal

Make staging a first-class DigitalOcean footprint under **Staging TAC-to-IWXXM** (own DOKS
cluster + managed Postgres) while prod stays on **TAC-to-IWXXM**, without breaking
`stage`→staging / `main`→prod promote CD from EV-043.

[Corpus: product §F30] [Corpus: deploy] [Corpus: tech-spec] [Corpus: tests]
[Corpus: adr/ADR-034] [Corpus: adr/ADR-033]

## In scope

- Provision cheapest viable **staging DOKS** (`metar-iwxxm-staging`, 1× `s-2vcpu-4gb`, `nyc1`);
  assign to DO Project **Staging TAC-to-IWXXM**
- Provision cheapest **staging Postgres** (`metar-iwxxm-staging`, `db-s-1vcpu-1gb`); assign to
  **Staging TAC-to-IWXXM**
- Keep prod cluster/DB on DO Project **TAC-to-IWXXM**
- Wire CD `stage` → staging cluster kubeconfig / GH Env; `main` → prod (promote rules unchanged)
- DNS: `api|app.staging.tac-to-iwxxm.com` → **new** staging LB IP (Porkbun)
- Amend ADR-034 (second cluster now accepted); update deploy/runbooks/skills `env_role`
- Tear down shared-cluster ns `metar-iwxxm-staging` after new stack smokes green

## Out of scope

- Product UI features; App Platform; changing promote-from-stage PR policy; Render reopen;
  enlarging prod node pool beyond what cutover needs

## Locked decisions (2026-08-08)

| ID | Decision |
|----|----------|
| D-S053-open | Approve S053 / EV-044 Standard routing (`1:1`) |
| D-S053-db | New cheapest managed PG under Staging project (`2:1`) |
| D-S053-size | Staging DOKS 1× `s-2vcpu-4gb` match prod cheapest (`3:1`) |
| D-S053-teardown | Tear down shared-cluster staging ns after cutover (`4:1`) |
| D-S053-scope | Separate staging DOKS + project visibility (`prior 1:2 / 2:2`) |

## Routing

**Standard**: `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
Skip `06` (no new language/runtime dependency inventory change).
