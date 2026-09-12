# 03-plan-tooling — S015 / EV-011

**Date**: 2026-07-19  
**Decision**: E11-18 — approve #1+#2 + issue-registry afterFileEdit hook

## Created / updated

| Item | Path |
|------|------|
| Plan adherence sync | `.cursor/rules/core/plan-adherence.mdc` — F15; F11–F14 Implemented; F7 Planned |
| Registry rule | `.cursor/rules/optional/tac-validate-issue-registry.mdc` |
| Advisory hook | `.cursor/hooks/issue_registry_guard.py` |
| Hook registration | `.cursor/hooks.json` afterFileEdit |
| Feature map | `.cursor/hooks/feature_drift.py` — F15 on `packages/tac-validate` |

## Skipped

- New skills / agents (covered by existing plan-adherence + pypi-package-publish + new rule)

## Smoke

`issue_registry_guard.py` warns on `rules.py` severity literals; silent on `models.py` and non-tac-validate paths.
