# EV-034 / S042 — Execution plan (delta)

**Cycle:** EV-034 · **Session:** S042-doks-cd-rollout  
**Deepen:** F30 · **Spec:** evolve-decisions §EV-034; `docs/deploy.md` CD section; TC-F30-007

## Tasks

| ID | Type | Description | Spec Source | Depends | Status |
|----|------|-------------|-------------|---------|--------|
| T1.1 | docs | Lock Phase 0 + F30/deploy/test-plan delta | E34-*; feature-list F30; deploy.md; TC-F30-007 | — | completed |
| T1.2 | impl | `scripts/deploy/doks_rollout_images.sh` | E34-1/2; TC-F30-007 | T1.1 | completed |
| T1.3 | impl | Wire Deploy job: kubectl + `KUBE_CONFIG`; DOKS rollout; Render optional/no-fail | E34-3/4; ci-cd.yml | T1.2 | completed |
| T1.4 | test | Light guard: script exists + workflow references rollout + no hard Render enforce | TC-F30-007 | T1.3 | completed |
| T1.5 | docs | `deploy/doks/README.md` CD pointer | deploy.md | T1.3 | completed |

## Git Strategy

- Branch: `evolve/EV-034-doks-cd-rollout`
- PR title: `[EV-034] Automate DOKS image rollout in CD`
- Checklist: lint · typecheck · tests · no secrets · TC-F30-007 mapping · `KUBE_CONFIG` documented (not committed)
