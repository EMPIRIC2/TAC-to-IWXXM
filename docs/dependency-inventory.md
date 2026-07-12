# Dependency Inventory

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-07-12 (S008 realtime/package amend)

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
| tac2iwxxm | Conversion (F6) | MIT | workspace path |
| tac-validate | TAC lint / rules | MIT | workspace path |
| iwxxm-validate | XSD + Schematron (F2) | MIT | workspace path |
| gifts | ~~Conversion~~ | — | **Removed at F6 cutover** (ADR-014) |

### packages/tac2iwxxm

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| lxml | XML encode/validate support | BSD | PyPI |
| IR library | Versioned IR models | Apache-2.0 | **msgspec** (ADR-016) |
| PyO3 / maturin / rustc | Native hotspots | Apache-2.0 / MIT (typical) | **Required before cutover** (ADR-017) |

Package license: **MIT**. No FastAPI/Supabase imports.

### packages/tac-validate

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| msgspec | Structured issue / fix models | Apache-2.0 | **Required** (ADR-016); pydantic only at HTTP |

Package license: **MIT**. Stdlib-first preferred; no FastAPI/Supabase. No Schematron.

### packages/iwxxm-validate

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| lxml | XSD + Schematron execution | BSD | PyPI |

Package license: **MIT**. Vendor schemas read-only. No FastAPI/Supabase.

### packages/gifts — Removed at F6 cutover

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| (historical GIFTs deps) | METAR parsing, XML | Per former pyproject | Removed per ADR-014; REQ-014 deprecated |

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
| basedpyright | strict | Python typechecking including tac2iwxxm, tac-validate, iwxxm-validate (ADR-005) |
| ruff | all Python packages | Lint + format including new validate packages (ADR-005) |
| prettier | workspace TS | Format apps/* and packages/* TypeScript |
| eslint | workspace TS | Lint apps/frontend, apps/e2e, packages/shared |
| make | system | Orchestration |
| pre-commit | dev group (pyproject) | Git hooks — fast gates |
| actionlint | pre-commit hook | GitHub Actions workflow lint (EV-002) |
| yamllint | pre-commit hook | `.github/` YAML lint (EV-002) |
| supabase/setup-cli | GitHub Action | Supabase CLI in `supabase-sync.yml` |
| docker / compose | system | Local multi-service |
| Coverage | 95% all members | pytest + Vitest gates (ADR-007); includes tac2iwxxm, tac-validate, iwxxm-validate |
| cargo / maturin | optional | Only when Rust/PyO3 extra enabled (04-tech-plan) |

**Deployables**: No new Render service **this cycle**. API image depends on tac2iwxxm + validate
packages; F8 worker (if later) is under F8 + ADR. Rust toolchain in image only if native extra enabled (04).

## Vendored / External Data (not PyPI)

| Asset | Upstream | Location | Update mechanism |
|-------|----------|----------|------------------|
| iwxxm schemas | wmo-im/iwxxm | vendor/schemas/iwxxm | Scheduled Action + manifest.json |
| iwxxm-codelists | wmo-im/iwxxm-codelists | vendor/schemas/iwxxm-codelists | Scheduled Action |
| iwxxm-modelling | wmo-im/iwxxm-modelling | vendor/schemas/iwxxm-modelling | Scheduled Action |
| iwxxm-translation | wmo-im/iwxxm-translation | vendor/schemas/iwxxm-translation | Scheduled Action |
| iwxxm-us | NOAA/MDL (URL/tag in 04) | vendor/schemas/iwxxm-us | Manifest pin + sync PR (F6) |
| GIFTs source | mgoberfield/GIFTs | ~~packages/gifts~~ | **Removed** at F6 cutover (ADR-014) |

## Removed Dependencies (post-migration / F6)

| Removed | Replaced by |
|---------|-------------|
| git submodules (×6) | vendor/ + in-repo packages |
| Separate auth Docker image | packages/auth in backend image |
| packages/gifts (F6 cutover) | packages/tac2iwxxm |
| (inline backend Schematron) | packages/iwxxm-validate |
| (ad-hoc TAC checks) | packages/tac-validate |

## License Notes

- wmo-im schema repos: WMO terms — read-only vendor copies.
- iwxxm-us: cite NOAA/MDL upstream notices in vendor README at pin time.
- `packages/tac2iwxxm`, `packages/tac-validate`, `packages/iwxxm-validate`: **MIT**.
- GIFTs: package removed — no longer ship its LICENSE in-tree.
- Run audit-licenses skill before adding new PyPI/npm deps (including PyO3 extras; tac-validate
  pydantic/msgspec choice in 04).

## Decision Log

New dependencies require `[Decision]` + back-add to this file per plan-adherence rules.

### Session changelog

- S008 (2026-07-12): tac2iwxxm MIT; gifts removed; iwxxm-us; optional PyO3; IR lib TBD in 04
- S008 amend (2026-07-12): tac-validate + iwxxm-validate MIT; lxml for Schematron; tac-validate
  may use pydantic/msgspec (04)
- S008 04 (2026-07-12): msgspec required; PyO3 cutover gate; F8 worker deps (ADR-016–018)
