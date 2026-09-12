# 01-requirements delta — EV-028 / S035

**Date**: 2026-08-01  
**Mode**: delta / general (no new Fn)  
**UI preview**: N/A

## Locked intake

D-S035-open (1b/2a/3b/4b) + D-S035-routing (5a Lean+build, 6b all three → `0.1.1`).

## Artifacts updated

| Path | Change |
|------|--------|
| `docs/decisions/evolve-decisions.md` | Cycle EV-028 scope + acceptance |
| `docs/deploy.md` | EMPIRIC2 Trusted Publisher table; landing-page rule; `0.1.1+` tags |
| `docs/config-spec.md` | Publisher fields + tag pattern |
| `docs/test-plan.md` | TC-F14-001 amend; TC-EV028-001..003 |
| `docs/feature-list.md` | F12–F14 status/acceptance for EMPIRIC2 OIDC + consumer landings |

## Build-stage deliverables (not in 01)

- Codecov purge in CI/README/secret
- Package README + `description` rewrites (three public + dissemination)
- Version bumps to `0.1.1` + tags

## Open for AskQuestion

1. Document Manifest lean set (as written in evolve-decisions)
2. Close 01 → 02-verify-plan
