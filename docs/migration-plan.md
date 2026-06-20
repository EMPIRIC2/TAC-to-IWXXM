# Migration Plan — Submodule to Monorepo

> **Project**: METAR to IWXXM Converter
> **Repository**: https://github.com/joseph-c-mcguire/metar-to-IWXXM
> **Last updated**: 2026-06-14

## Summary

| Field | Value |
|-------|-------|
| **From** | Root repo + 6 git submodules + separate auth/ backend/ directories |
| **To** | Single git: `apps/` + `packages/` + `vendor/` |
| **Estimated effort** | 2–5 dev-days (structure, CI, docs, tests) |
| **Risk level** | Medium (big-bang; actively updating repo) |
| **Rollback possible** | Partial — revert merge commit; re-init submodules from archived repos |

## Motivation

- Eliminate `git clone --recurse-submodules` and submodule SHA drift.
- Separate authoritative iwxxm schema sources (read-only vendor) from editable app code.
- Collapse auth microservice into backend for simpler deploy (two Render services).
- Single PR workflow for cross-cutting changes (frontend + backend + GIFTs).

## Scope

**In scope**:

- Remove `.gitmodules`; vendor wmo-im snapshots with `vendor/manifest.json`
- Move `backend/` → `apps/backend/`, `frontend/` → `apps/frontend/`
- Move `GIFTs/` → `packages/gifts/`, `auth/` → `packages/auth/`
- Create `packages/shared/`, `apps/e2e/` (relocate root `tests/*.e2e.spec.ts`)
- Merge auth routes into backend; update docker-compose, render.yaml, Makefile
- Update CI workflows; add scheduled upstream sync Actions
- Update README, DEVELOPMENT.md, all submodule references

**Out of scope**:

- Product feature rewrites (non-goal REQ-016)
- Changes to wmo-im schema content
- New conversion algorithms

## Pre-Migration Checklist

- [ ] Feature freeze window communicated (big-bang)
- [ ] Record current submodule SHAs in this doc / manifest baseline
- [ ] Export golden conversion outputs for TC-M003
- [ ] Confirm Render env vars documented for two-service layout
- [ ] Branch: `feat/monorepo-big-bang` from latest `main`

## Migration Steps

| # | Step | Action | Rollback |
|---|------|--------|----------|
| 1 | Vendor baseline | Run vendor sync script; populate `vendor/schemas/*` + manifest.json from current submodule SHAs | Delete vendor/ |
| 2 | Move packages | Copy GIFTs → packages/gifts; auth → packages/auth; extract shared utils | Restore from git |
| 3 | Move apps | backend → apps/backend; frontend → apps/frontend; root e2e → apps/e2e | Restore paths |
| 4 | Wire workspaces | Root pyproject.toml uv workspace; pnpm-workspace.yaml; path deps | Revert pyproject |
| 5 | Merge auth | Mount auth routers in backend; remove auth service from compose | Restore auth/ service |
| 6 | Update imports | Fix Python/TS paths to packages/* and vendor/* | git revert |
| 7 | CI/CD | Update workflows, Docker contexts, render.yaml | Revert workflows |
| 8 | Remove submodules | `git submodule deinit -f --all`; delete .gitmodules; remove .git/modules refs | Re-add submodules from archive |
| 9 | Docs + tests | Update all docs; reorganize tests per test-plan | Revert docs |
| 10 | Validate gate | TC-M001–M005 + full E2E | — |

### Step 1 Detail: Vendor Baseline

```bash
# To be implemented in scripts/vendor/sync-iwxxm.sh
./scripts/vendor/sync-iwxxm.sh --from-manifest vendor/manifest.json
```

Expected: four schema trees under `vendor/schemas/` matching wmo-im tags.

### Step 5 Detail: Auth Merge

- Import `packages.auth` middleware in `apps/backend` FastAPI app.
- Mount former auth routes at `/auth/*` on backend port.
- Frontend: single `VITE_API_BASE_URL` (auth + API same host).
- Remove `auth` service from docker-compose.yml.

## Post-Migration Validation

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | No submodules | `test - ! -f .gitmodules` | absent |
| 2 | Clone smoke | TC-M001 | pass |
| 3 | Manifest integrity | TC-M002 | pass |
| 4 | Conversion golden | TC-M003 | pass |
| 5 | E2E suite | `make tests:e2e` | pass |
| 6 | Render preflight | render.yaml validate + deploy dry-run | pass |

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Big-bang merge conflicts | High | High | Feature freeze; single owner branch |
| 2 | Broken path imports | Medium | High | CI matrix + TC-M001 |
| 3 | GIFTs manual merge conflicts | Medium | Medium | Manual merges only; resolve when pulling mgoberfield |
| 4 | Render deploy misconfig | Medium | High | UJ-OPS-001 smoke; two-service checklist |
| 5 | Lost submodule history | Low | Low | Archived repos remain on GitHub |

## Rollback Plan

1. Revert merge commit on `main`.
2. Restore `.gitmodules` from previous commit.
3. `git submodule update --init --recursive`
4. Redeploy previous Render images.

**Point of no return**: Archiving legacy repos after stable production deploy (REQ-019).

## Communication Plan

| When | Who | What |
|------|-----|------|
| Before merge | Contributors | Feature freeze + branch name |
| PR open | Reviewers | Big-bang checklist in PR body |
| After merge | All | New clone instructions (no submodules) |
| After stable production deploy | GitHub | Archive legacy repos (REQ-019 — out of migration PR scope) |

## References

- docs/spec.md §Monorepo Migration
- docs/requirements-decisions.md
- ADR-001, ADR-002, ADR-003
