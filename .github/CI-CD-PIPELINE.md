# Continuous integration and delivery (CI/CD)

This document describes how GitHub Actions checks run for the TAC-to-IWXXM
monorepo. The primary workflow file is `.github/workflows/ci-cd.yml`.

## What “green” means

Required checks must pass before you merge a feature or evolve pull request into
the `stage` Git branch, and again before you promote `stage` to `main`.

Typical required work includes:

- Format / lint / typecheck
- Unit tests with **100%** line coverage on covered packages (fail closed)
- Frontend Vitest coverage at the configured 100% thresholds
- End-to-end checks (smoke on many paths; **E2E Full (Playwright)** on promote)

Exact job names can change. Trust the Checks tab on the pull request and
`docs/deploy.md` for promote rules.

## Monorepo surfaces under test

| Surface | Location | Typical runner |
|---------|----------|----------------|
| HTTP API | `apps/backend` | pytest + coverage |
| Operator website | `apps/frontend` | Vitest + coverage |
| Ingest worker | `apps/worker` | pytest + coverage |
| Auth library | `packages/auth` | pytest + coverage |
| Conversion | `packages/tac2iwxxm` | pytest + coverage |
| TAC lint | `packages/tac-validate` | pytest + coverage |
| IWXXM validate | `packages/iwxxm-validate` | pytest + coverage |
| Dissemination | `packages/dissemination` | pytest + coverage scripts |
| Workflows | `packages/workflows` | pytest + coverage |
| Shared helpers | `packages/shared` | pytest + Vitest as applicable |
| End-to-end | `apps/e2e` | Playwright |

Legacy top-level paths such as `backend/`, `auth/`, and `GIFTs/` are not the
current layout. New work targets `apps/` and `packages/`.

## Branch flow

| Change type | Target branch |
|-------------|---------------|
| Feature / evolve pull request | `stage` (not `main` while `stage` exists) |
| Production promote | `stage` → `main` |
| Production deploy | Tag `vYYYY.MM.DD-deploy` on `main` after tip CI is green |

See `docs/deploy.md` for promote and release steps.

## Local parity before the first push

From the repository root:

```bash
make format-check lint typecheck test-unit
# or: make validate-fast / make ci
```

After you push:

```bash
gh run list --branch "$(git branch --show-current)" --workflow ci-cd.yml --limit 3
gh run watch <run-id>
```

## Coverage policy (current)

Covered Python packages and the frontend use **fail-under 100** (or equivalent
per-file gates). Do not lower those thresholds to make CI green. Fix the missing
tests or uncovered lines instead.

## Related docs

- [docs/deploy.md](../docs/deploy.md) — deploy, promote, and staging smoke
- [docs/ops/DEVELOPMENT.md](../docs/ops/DEVELOPMENT.md) — local setup
- Root [README.md](../README.md) — install and run
