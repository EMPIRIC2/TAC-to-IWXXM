# Dependency Inventory

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-06-14

## Runtime Dependencies

### apps/backend

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| fastapi | HTTP API | MIT | PyPI |
| uvicorn | ASGI server | BSD | PyPI |
| pydantic | Schemas | MIT | PyPI |
| httpx | HTTP client | BSD | PyPI |
| httpx2 | Starlette TestClient (dev) | BSD | PyPI |
| python-multipart | File uploads | Apache-2.0 | PyPI |
| supabase | Auth (via packages/auth) | MIT | PyPI |
| gifts | Conversion | See packages/gifts | workspace path |

### packages/gifts

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| (GIFTs deps) | METAR parsing, XML | Per GIFTs pyproject | In-repo; upstream mgoberfield/GIFTs |

### packages/auth

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| fastapi | Router mounting | MIT | PyPI |
| supabase | JWT validation | MIT | PyPI |

### apps/frontend

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| react | UI | MIT | npm |
| vite | Bundler | MIT | npm |
| @supabase/supabase-js | Client auth | MIT | npm |

## Workspace Tooling

| Tool | Version policy | Purpose |
|------|----------------|---------|
| Python | **3.12** (pinned) | Runtime for all uv workspace members (ADR-005) |
| Node | **22** (pinned) | Frontend/e2e workspace (ADR-005) |
| uv | pin in pyproject | Python workspace, lockfile |
| pnpm | pin in package.json engines | JS workspace (monorepo) |
| basedpyright | strict | Python typechecking (ADR-005) |
| ruff | all Python packages | Lint + format including packages/gifts (ADR-005) |
| prettier | workspace TS | Format apps/* and packages/* TypeScript |
| eslint | workspace TS | Lint apps/frontend, apps/e2e, packages/shared |
| make | system | Orchestration |
| pre-commit | dev group (pyproject) | Git hooks — gitleaks + `make ci` gate |
| docker / compose | system | Local multi-service |
| Coverage | 95% all members | pytest + Vitest gates (ADR-007) |

## Vendored / External Data (not PyPI)

| Asset | Upstream | Location | Update mechanism |
|-------|----------|----------|------------------|
| iwxxm schemas | wmo-im/iwxxm | vendor/schemas/iwxxm | Scheduled Action + manifest.json |
| iwxxm-codelists | wmo-im/iwxxm-codelists | vendor/schemas/iwxxm-codelists | Scheduled Action |
| iwxxm-modelling | wmo-im/iwxxm-modelling | vendor/schemas/iwxxm-modelling | Scheduled Action |
| iwxxm-translation | wmo-im/iwxxm-translation | vendor/schemas/iwxxm-translation | Scheduled Action |
| GIFTs source | mgoberfield/GIFTs | packages/gifts | Manual merge when chosen (REQ-014) |

## Removed Dependencies (post-migration)

| Removed | Replaced by |
|---------|-------------|
| git submodules (×6) | vendor/ + in-repo packages |
| Separate auth Docker image | packages/auth in backend image |

## License Notes

- wmo-im schema repos: WMO terms — read-only vendor copies.
- GIFTs: verify LICENSE in packages/gifts before release.
- Run audit-licenses skill before adding new PyPI/npm deps.

## Decision Log

New dependencies require `[Decision]` + back-add to this file per plan-adherence rules.
