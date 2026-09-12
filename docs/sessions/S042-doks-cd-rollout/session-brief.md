---
session_id: S042-doks-cd-rollout
type: feature
status: in_progress
branch: evolve/EV-034-doks-cd-rollout
started_at: 2026-08-05
intent: "Automate DOKS image rollout in CD pipeline after main merge/GHCR push"
orchestrator: 16-evolve
evolve_cycle_id: EV-034
prior_session: S041-worker-poller-hardening
context_briefs: []
standing_docs_touched: []
feature_ids: []
deepen_feature_ids:
  - F30
feature_note: "Infra/CD — close ci-cd.yml kubectl Notes gap; baseline tag 20260805003332-5245f8d"
route_status: approved_E34-1-5
---

# Session S042 — doks-cd-rollout

## Intent

Automate DOKS image rollout in the CD pipeline after `main` merge / GHCR push.
Close the gap where `ci-cd.yml` only **Notes** kubectl `set-image` / rollout commands
instead of executing them. Triggered after #845/#866 and the manual one-shot rollout of
`20260805003332-5245f8d`.

## Prior sessions

| Item | Disposition |
|------|-------------|
| S041 / EV-033 | **Completed** (lean-close `D-S041-1+3`) |
| S040 / EV-032 | **Suspended** — `resume_after` S042; do **not** auto-resume now |
| DOKS baseline | Live tag `20260805003332-5245f8d` (api/frontend/worker in `metar-iwxxm`) |

## Scope (Phase 0 — locked `E34-1..5` = A,A,A,B,A)

### In

- After GHCR push on `main`, pin `metar-api` / `metar-frontend` / `metar-worker` to
  immutable `TIMESTAMP-SHA` via `scripts/deploy/doks_rollout_images.sh`
- Actions secret `KUBE_CONFIG` (base64 kubeconfig) — fail-closed if missing
- Render hooks optional / non-blocking
- Docs + TC-F30-007 + Standard verify path

### Out

- Auto-resuming S040; new product Fn; Alembic redesign

## Routing (approved)

**Standard:** `00→16→01→02→04→07→08→09→11→12→13` (skip 03/05/06/10)

## Branch

`evolve/EV-034-doks-cd-rollout` (created)

## Links

- Standing: [tech-spec.md](../../tech-spec.md), [deploy.md](../../deploy.md), [CORPUS.md](../../CORPUS.md)
- Prior: [S041 session-brief](../S041-worker-poller-hardening/session-brief.md), [S041 evolve-summary](../S041-worker-poller-hardening/reports/evolve-summary.md)
