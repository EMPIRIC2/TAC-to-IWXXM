# Execution plan — S052 / EV-043

[Corpus: product §F30] [Corpus: adr/ADR-034] [Corpus: deploy]

| ID | Type | Task | Spec Source | Depends On | Status |
|----|------|------|-------------|------------|--------|
| T1.1 | docs | F30 AC8–12 + test-plan TC-F30-008..012 + evolve-decisions + ADR-034 | feature-list; test-plan; #886 | — | completed |
| T1.2 | rule | Cursor rule promote-from-stage / dual env_role | ADR-034 | T1.1 | completed |
| T2.1 | iac | Kustomize overlays staging + prod | deploy/doks; ADR-034 | T1.1 | in_progress |
| T2.2 | ci | Dual Deploy jobs + Staging smoke + staging-gate | ci-cd.yml; TC-F30-010/012 | T2.1 | pending |
| T2.3 | ops | stage branch, ns/secrets, RBAC, DNS runbook, GH envs/rulesets | deploy.md; #886 | T2.1 | pending |
| T2.4 | docs | deploy.md + skills 12/13/15/16 + ci-after-push | ADR-034 | T2.2 | pending |
| T3.1 | verify | 08–13 staging smoke + prod path evidence | TC-F30-008..012 | T2.* | pending |

## Milestone

**M1** — Dual-env DOKS + CI/CD + protection docs/CLI
