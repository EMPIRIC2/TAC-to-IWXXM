# Monorepo Migration Checklist

Validates monorepo migration progress against `docs/migration-plan.md` and test-plan TC-M*
cases. Use during M1–M6 implementation, PR review, and phase gate checks.

## When to Use

- Starting or resuming big-bang migration work (ADR-003)
- Before opening the monorepo PR
- Verifying a migration milestone is complete
- Reviewing whether a change is structural (allowed) vs product rewrite (blocked)

## Spec Sources

- `docs/migration-plan.md` — steps, scope, rollback
- `docs/test-plan.md` — TC-M001 through TC-M005
- `docs/feature-list.md` — M1–M6 acceptance
- `docs/spec.md` §Monorepo Migration — submodule mapping

## Pre-Migration Gate

| Check | Source |
|-------|--------|
| Feature freeze communicated | migration-plan §Pre-Migration |
| Submodule SHAs recorded | migration-plan / vendor manifest baseline |
| Golden fixtures exported | TC-M003 / test-data |
| Render env vars documented | deploy.md, config-spec artifact |
| Branch `feat/monorepo-big-bang` | migration-plan §Pre-Migration |

## Step Validation (migration-plan §Migration Steps)

| Step | Verify |
|------|--------|
| 1 Vendor baseline | `vendor/schemas/*` + `vendor/manifest.json` populated |
| 2 Move packages | `packages/gifts`, `packages/auth`, `packages/shared` exist |
| 3 Move apps | `apps/backend`, `apps/frontend`, `apps/e2e` exist |
| 4 Wire workspaces | Root `pyproject.toml` uv workspace; `pnpm-workspace.yaml` |
| 5 Merge auth | Auth routes on backend; auth service removed from compose |
| 6 Update imports | No broken Python/TS path deps |
| 7 CI/CD | Workflows, Docker, render.yaml updated |
| 8 Docs | No `git submodule` instructions remain |
| 9 Remove submodules | `.gitmodules` absent (TC-M004) |

## Test Case Mapping

| TC | Pass criteria |
|----|---------------|
| TC-M001 | Clone + `make install && make test-unit` + health 200 |
| TC-M002 | Manifest matches checked-in vendor tree |
| TC-M003 | Golden conversion outputs unchanged (normalized XML) |
| TC-M004 | No submodule machinery in repo |
| TC-M005 | Auth on backend; two-service compose |

## Blocked During Migration (REQ-016)

- New conversion algorithms or validation rules
- UI feature additions beyond wiring fixes
- Direct edits to `vendor/schemas/*` content (manifest bumps via sync only)
- Automated GIFTs upstream sync (manual only — ADR-004)

## Output Format

```
Migration Checklist: [N]/[total] complete

Step status:
- [x] Step 1 — Vendor baseline
- [ ] Step 5 — Merge auth (blocker: ...)

Test cases:
- TC-M001: pending | pass | fail

Scope warnings:
- ...
```

Raise `[Scope Drift]` for changes that look like product features, not migration structure.
