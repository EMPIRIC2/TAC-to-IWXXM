# 03-plan-tooling — S060 / EV-051

**Date:** 2026-08-09  
**Corpus:** [Corpus: adr/ADR-034] [Corpus: deploy]

## Updated

| Artifact | Change |
|----------|--------|
| `.cursor/rules/optional/doks-promote-from-stage.mdc` | Tag-driven prod; no auto Deploy on `main` |
| `.cursor/rules/optional/ci-after-push.mdc` | Event matrix for stage / main / deploy tag |
| `.cursor/rules/core/atomic-commits.mdc` | Promote = tag rolls prod |

## Exit

→ 07-build / 08-verify-build.
