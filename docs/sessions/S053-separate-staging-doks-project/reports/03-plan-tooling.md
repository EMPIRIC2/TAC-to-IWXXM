# 03-plan-tooling — S053 / EV-044 (delta)

**Status**: complete  
**Date**: 2026-08-08

## Changes

| Tooling | Action |
|---------|--------|
| `.cursor/rules/optional/doks-promote-from-stage.mdc` | Updated for dual DO Project / dual cluster + env-scoped kubeconfig (Phase A) |
| plan-adherence / template | No new rule — F30 deepen stays within existing components |
| New hook | Not required — no new browser surface |

## Guardrails enforced

1. Do not put staging workloads back on the prod cluster after cutover.
2. Staging secrets / `DATABASE_URL` must target dedicated staging Postgres.
3. CD must use env-scoped kubeconfigs (`staging` ≠ `production`).
4. Promote path remains `stage`→`main` only + staging-gate.

[Corpus: adr/ADR-034] [Corpus: product §F30] [Corpus: deploy]
