# ADR-005: Runtime and Toolchain Pins

## Status: Accepted

## Context

The legacy repo uses inconsistent Python versions (3.9–3.12 across pyproject, CI, and Docker)
and Node versions (18–22). The monorepo migration requires a single canonical toolchain for uv
workspace, pnpm workspaces, CI, and Docker builds.

## Decision

Pin the following for all workspace members:

| Tool | Version / choice |
|------|------------------|
| Python | **3.12** (`requires-python = ">=3.12"` in root pyproject) |
| Node | **22** (`engines.node` in root package.json) |
| Python typechecker | **basedpyright** (strict on apps/backend + packages/*) |
| Python linter/formatter | **Ruff** (including packages/gifts — retire flake8/black/isort) |
| JS package manager | **pnpm** workspaces (replace npm lockfile in migration PR) |
| Coverage gate | **95%** on all packages and apps |

## Consequences

- GIFTs `requires-python >=3.9` compatibility statement narrows to 3.12+.
- Frontend Dockerfile must update from Node 20 to Node 22.
- CI jobs using Python 3.11 (gifts, integration) unify to 3.12.
- One-time effort to migrate gifts lint tooling and npm → pnpm.
- basedpyright may surface latent type issues — budget fix time in Phase 1.

## Alternatives Considered

- **Python 3.11 everywhere**: Rejected — backend CI/Docker already on 3.12.
- **Keep flake8 in gifts**: Rejected — inconsistent with backend/auth ruff setup.
- **Defer pnpm**: Rejected — REQ-005 requires pnpm workspaces in target layout.
- **Defer typechecker**: Rejected — user chose basedpyright for migration PR.
