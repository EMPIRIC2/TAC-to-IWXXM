# Dependency Inventory

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-07-21 (S019 / EV-014 — Planned `packages/dissemination` deps; ADR-030)

## Runtime Dependencies

### apps/backend

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| fastapi | HTTP API | MIT | PyPI |
| uvicorn | ASGI server | BSD | PyPI |
| pydantic | OpenAPI + low-churn schemas (ADR-026) | MIT | PyPI |
| msgspec | High-churn HTTP DTO decode/encode (ADR-026) | Apache-2.0 | PyPI |
| httpx | HTTP client | BSD | PyPI |
| httpx2 | Starlette TestClient (dev) | BSD | PyPI |
| python-multipart | File uploads | Apache-2.0 | PyPI |
| supabase | Auth (via packages/auth) | MIT | PyPI |
| tac2iwxxm | Conversion (F6) | MIT | workspace path |
| tac-validate | TAC lint / rules | MIT | workspace path |
| iwxxm-validate | XSD + Schematron (F2) | MIT | workspace path |
| gifts | ~~Conversion~~ | — | **Removed at F6 cutover** (ADR-014) |
| dissemination | F16–F19 sinks | MIT | workspace path (ADR-030) |

### packages/dissemination (S019 / EV-014 — M1)

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| sqlalchemy[asyncio] | Async engine / DDL / writer-contract | MIT | PyPI (`>=2.0`) |
| asyncpg | Postgres async driver | Apache-2.0 | PyPI (`>=0.29`) |
| aiomysql | MySQL/MariaDB async | MIT | PyPI (`>=0.2.0`) |
| aiosqlite | SQLite async | MIT | PyPI (`>=0.20.0`) |
| aioodbc | SQL Server async (ODBC) | MIT | PyPI (`>=0.5.0`; E14-06=A) |
| aiosmtplib | EDIS SMTP submit | MIT | PyPI (`>=3.0.0`) |
| msgspec | Preflight/send models + HTTP encode | Apache-2.0 | PyPI (`>=0.19`) |

Package license: **MIT**. No FastAPI/Supabase imports. Backend already has `sqlalchemy` +
`asyncpg` + `psycopg`; package may declare overlapping pins via workspace.

### packages/tac2iwxxm

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| lxml | XML encode/validate support | BSD | PyPI |
| IR library | Versioned IR models | Apache-2.0 | **msgspec** (ADR-016); reuse module-level `msgspec.json.Encoder` / `Decoder` on hot paths (`tac2iwxxm.codec`) |
| PyO3 / maturin / rustc | Native hotspots | Apache-2.0 / MIT (typical) | **Required before cutover** (ADR-017) |

Package license: **MIT**. No FastAPI/Supabase imports.

### packages/tac-validate

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| msgspec | Structured issue / fix models | Apache-2.0 | **Required** (ADR-016); reuse `tac_validate.codec` Encoder/Decoder |

Package license: **MIT**. Stdlib-first preferred; no FastAPI/Supabase. No Schematron.

### packages/iwxxm-validate

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| lxml | Transitional / parity reference (Python path) | BSD | PyPI |
| msgspec | Issue / report Struct models (ADR-016) | Apache-2.0 | PyPI |
| PyO3 / maturin / rustc | Rust XSD + Schematron core (F13 / #699) | Apache-2.0 / MIT | Required for published wheel |
| **xmloxide** 0.4.x | Native well-formed + XSD + ISO Schematron (D-S014-T33-crates) | MIT | crates.io (`default-features = false`) |
| Schema assets | Bundled pinned IWXXM XSD/SCH | WMO terms | Copied from `vendor/schemas/*` at build |

Package license: **MIT**. Vendor schemas read-only in monorepo; wheel may bundle pins.
Schematron: **native Rust via xmloxide** (F13 / E10-22); lxml isoschematron retained for parity until cutover.
Rejected for T3.3: `quick-xml`+`xsd-schema` (no Schematron), `libxml` (system deps / no xslt2 SCH).

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
| CodeMirror 6 | F7 workbench editor | MIT | npm — pinned S011 M2 T2.5: `codemirror@6.0.2`, `@codemirror/view@6.43.6`, `@codemirror/state@6.7.1`, `@codemirror/commands@6.10.4`, `@codemirror/language@6.12.4` (autocomplete deferred until needed) |

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
| cargo / maturin | **required before cutover** | PyO3 wheel build in CI/API image (ADR-017) |
| xsdata | **dev/codegen** (F11 / ADR-027) | XSD → Python models from pinned IWXXM schemas — `xsdata[cli]>=24.5` in workspace `dev` |
| xsdata-pydantic | **dev/codegen** (F11 / ADR-027) | pydantic v2 output plugin — `>=24.5` in workspace `dev`; also `metar-shared[xsd]` for importing committed models |
| maturin | **dev** (F13/F14) | PyO3 wheel build — `>=1.7` in workspace `dev`; also CI |

**Deployables**: API + static frontend + **F8 Background Worker** (`apps/worker`, ADR-018).
API image depends on tac2iwxxm + validate packages; worker image uses the same packages plus
poller/store writers. Rust toolchain in API (and worker if linked) image for PyO3.

## Vendored / External Data (not PyPI)

| Asset | Upstream | Location | Update mechanism |
|-------|----------|----------|------------------|
| iwxxm schemas | wmo-im/iwxxm | vendor/schemas/iwxxm | Scheduled Action + manifest.json |
| iwxxm-codelists | wmo-im/iwxxm-codelists | vendor/schemas/iwxxm-codelists | Scheduled Action |
| iwxxm-modelling | wmo-im/iwxxm-modelling | vendor/schemas/iwxxm-modelling | Scheduled Action |
| iwxxm-translation | wmo-im/iwxxm-translation | vendor/schemas/iwxxm-translation | Scheduled Action |
| iwxxm-us | NOAA/MDL HTTP `3.0` (`https://nws.weather.gov/schemas/iwxxm-us/3.0/`) | vendor/schemas/iwxxm-us | Manifest `source_url` + content hash (D-S008-05-batch1); sync PR |
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
- S008 05 (2026-07-12): iwxxm-us = NWS HTTP 3.0 + URL/hash; cargo/maturin required; F8 deployable
- S008 M1 (2026-07-12): msgspec added to tac2iwxxm + tac-validate with shared Encoder/Decoder modules; iwxxm-us vendored from NWS `3.0` tarball pin
  (D-S008-05-batch1)
- S014 / EV-010 (2026-07-18): backend msgspec high-churn (ADR-026); iwxxm-validate Rust+bundle;
  PyPI publish deps (maturin/OIDC); **xsdata + xsdata-pydantic** for XSD codegen (ADR-027);
  **xmloxide 0.4.x** native XSD+Schematron (D-S014-T33-crates / E10-46)
- S015 / EV-011 (2026-07-19): F15 issue registry — **no new runtime deps**; catalog HTTP + docs
  export from existing `tac-validate` / msgspec stack (E11-30)
- S019 / EV-014 (2026-07-21): Planned `packages/dissemination` — SQLAlchemy async + aiomysql /
  aiosqlite / **aioodbc** (E14-06=A) + aiosmtplib; msgspec HTTP (E14-07=A); pins in M1
