# 03-plan-tooling — S019 / EV-014

**Date**: 2026-07-21  
**Decision**: Q30=A — approve all delta guardrails  
**Status**: completed

## Created / updated

| Item | Path |
|------|------|
| Plan adherence sync | `.cursor/rules/core/plan-adherence.mdc` — F16–F19; Dissemination §; H4–H5/H6′ |
| SSRF / BYOC rule | `.cursor/rules/optional/dissemination-egress-ssrf.mdc` (ADR-029) |
| Feature map | `.cursor/hooks/feature_drift.py` — F16–F19 path prefixes; F1–F19 copy |
| Scope check labels | `.cursor/hooks/scope_check.py` — backend/frontend/worker/e2e F16–F19 notes |

## Skipped

- New skills / agents (existing plan-adherence + scope-reviewer + workflow-state-manager)
- New package/component paths (deferred to 04-tech-plan)
- Regenerating core rules unrelated to dissemination

## Smoke

```text
echo '{"filePath":".../apps/backend/src/routers/dissemination/preflight.py"}' \
  | python3 .cursor/hooks/feature_drift.py
→ F16–F19 — Dissemination preflight/send (ADR-029)

echo '{"filePath":".../apps/frontend/src/App.tsx"}' \
  | python3 .cursor/hooks/feature_drift.py
→ F1–F19 — Frontend UI (dissemination drawer = F16–F19)
```

## Phase A

01-requirements ✓ · 02-verify-plan ✓ · 03-plan-tooling ✓ → ready for Phase B (04-tech-plan).
