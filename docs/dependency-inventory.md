# Dependency Inventory

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-08-17 (S069 / EV-059 — F34 Schemathesis + pytest-gremlins + Stryker)
> **Status**: **Accepted** for F30/F31; **EV-059 planned** quality-gate deps below (install in 07-build)

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
| slowapi | Public API rate limits (F21 / ADR-031) | MIT | PyPI (E17-15) |
| redis | Optional slowapi storage backend (Upstash Redis URL) — EV-052 / #900 | MIT | PyPI (`apps/backend`) |
| sentry-sdk[fastapi] | Error monitoring when `SENTRY_DSN` set — EV-052 / #900 | MIT / BSL (SDK) | PyPI (`apps/backend`; worker uses `sentry-sdk`) |
| fakeredis | Unit tests for shared rate-limit store — EV-052 | MIT | PyPI (dev; `apps/backend`) |
| alembic | Schema migrations against `DATABASE_URL` (F30); CI/deploy `upgrade head` | MIT | PyPI (`>=1.13,<2`) |
| sqlalchemy | DO Postgres access for sessions / F8 (shared) | MIT | PyPI (`>=2.0,<3`) |
| asyncpg / psycopg | Postgres drivers for `DATABASE_URL` | Apache-2.0 / LGPL | PyPI (existing + Alembic) |
| tac2iwxxm | Conversion (F6) | MIT | workspace path |
| tac-validate | TAC lint / rules | MIT | workspace path |
| iwxxm-validate | XSD + Schematron (F2) | MIT | workspace path |
| gifts | ~~Conversion~~ | — | **Removed at F6 cutover** (ADR-014) |
| dissemination | F16–F19 sinks | MIT | workspace path (ADR-030) |
| auth | Supabase Auth JWT verify + `/auth/*` (F31 restore) | MIT | workspace `packages/auth` (ADR-033) |

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
| httpx | WIS2 HTTP dataset client (`HttpxDatasetClient`) | BSD | PyPI (`>=0.28`) |
| aiomqtt | WIS2 MQTT client (`AiomqttClient`; 2.x / paho) | BSD-3-Clause | PyPI (`>=2.3.0,<3`) |
| tac2iwxxm | Shared AHL parse/format/`T1T2`/BBB/filename (EV-029 / E29-T2) | MIT | workspace path |

#### packages/dissemination — test / integration (E14-09)

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| testcontainers[mysql,postgres] | PG/MySQL Testcontainers for TC-F16-003 (T2.5) | MIT | PyPI (`>=4.8`); workspace `dev` + package optional `integration` |
| python:3.12.11-slim-bookworm + mosquitto (apt) | F17 wis2box Compose harness image (T3.3) — MQTT + HTTP dataset stand-in | PSF / EPL-2.0 (mosquitto) | Docker Hub / Debian; build context `packages/dissemination/docker/wis2box-harness` |

Package license: **MIT**. No FastAPI/Supabase imports. Backend already has `sqlalchemy` +
`asyncpg` + `psycopg`; package may declare overlapping pins via workspace.

### packages/tac2iwxxm

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| msgspec | Versioned IR / convert issue models (ADR-016) | Apache-2.0 | PyPI (`>=0.19`) |
| PyYAML | Decode glossary YAML overlays (F9 / ADR-032; E20-F5) | MIT | PyPI (`>=6.0`) |
| lxml | XML encode/validate support (optional / transitional) | BSD | PyPI |
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

### packages/auth — **Restored (F31 / ADR-033)**

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| PyJWT[crypto] | JWKS JWT verify (RS256/ES256); **no HS256 secret path** for product | MIT | PyPI (`>=2.8`) |
| httpx | Fetch Supabase Auth JWKS (`…/auth/v1/.well-known/jwks.json`) | BSD | PyPI (`>=0.28`) |
| fastapi | `/auth/*` router types (library mounted in backend) | MIT | PyPI |
| supabase (optional FE-adjacent) | Prefer FE `@supabase/supabase-js`; Python client **not required** for JWKS verify | Apache-2.0 | avoid for server verify |
| (workspace) | Auth library mounted in `apps/backend` | MIT | `packages/auth` |

Was **Deleted** under F21 / ADR-031 (E17-22=B). EV-031 restores Auth-only path (no product DB
via Supabase). **JWKS-only** (`D-S038-04-b1` Q2=2): do not use `SUPABASE_JWT_SECRET` /
`python-jose` HS256 as product verify. Strip admin routes on restore from `c9cebfa^`.

### apps/frontend

| Package | Purpose | License | Source |
|---------|---------|---------|--------|
| react | UI | MIT | npm |
| vite | Bundler | MIT | npm |
| **idb** | IndexedDB wrapper for guest work sessions (F7.h / F31) | ISC | npm (E17-12 / ADR-031) |
| fake-indexeddb | Vitest IndexedDB polyfill for TC-004 | Unlicense | npm (dev; T2.3) |
| **@supabase/supabase-js** | Optional client Auth bootstrap (F31 login) | Apache-2.0 | npm — restore in 04 |
| CodeMirror 6 | F7 workbench editor | MIT | npm — pinned S011 M2 T2.5: `codemirror@6.0.2`, `@codemirror/view@6.43.6`, `@codemirror/state@6.7.1`, `@codemirror/commands@6.10.4`, `@codemirror/language@6.12.4` (autocomplete deferred until needed) |
| @sentry/react | Browser error monitoring when DSN set — EV-052 / #900 | MIT | npm (`apps/frontend`) |
| openapi-typescript | OpenAPI → typed FE client — EV-052 / #900 (`D-S061-orval=1`; not full Orval) | MIT | npm (dev; `apps/frontend`) |

## Workspace Tooling

| Tool | Version policy | Purpose |
|------|----------------|---------|
| Python | **3.12** (pinned) | Runtime for all uv workspace members (ADR-005) |
| Node | **22** (pinned) | Frontend/e2e workspace (ADR-005) |
| uv | pin in pyproject | Python workspace, lockfile |
| pnpm | **9.15.4** via `packageManager` + corepack | JS workspace (monorepo); not Homebrew |
| macOS Homebrew | root [`Brewfile`](../Brewfile) | System toolchain: `python@3.12`, `node@22`, `uv`, `rust`, Docker Desktop, `libpq`, `unixodbc`, `gh` |
| basedpyright | strict | Python typechecking including tac2iwxxm, tac-validate, iwxxm-validate (ADR-005) |
| ruff | all Python packages | Lint + format including new validate packages (ADR-005) |
| prettier | workspace TS | Format apps/* and packages/* TypeScript |
| eslint | workspace TS | Lint apps/frontend, apps/e2e, packages/shared |
| make | system | Orchestration |
| pre-commit | dev group (pyproject) | Fast commit gates (invoked from husky) |
| husky | root `package.json` devDependency (^9.1.7) | Git hooksPath — pre-commit (fast+medium) + pre-push (`make ci` units+Compose; EV-036) |
| actionlint | pre-commit hook | GitHub Actions workflow lint (EV-002) |
| yamllint | pre-commit hook | `.github/` YAML lint (EV-002) |
| supabase/setup-cli | GitHub Action | Supabase CLI in `supabase-sync.yml` — **pin `2.111.0`** (not `latest`; CLI 2.112.0 breaks `link` on api-keys `inserted_at`, supabase/cli#6115 / BUG-2026-08-07) |
| docker / compose | system | Local multi-service |
| Coverage | 95% all members | pytest + Vitest gates (ADR-007); includes tac2iwxxm, tac-validate, iwxxm-validate |
| schemathesis | **dev** (F34 / EV-059 / #727) | OpenAPI property-based suite vs `apps/backend` ASGI — **MIT**; pinned `==4.24.3` (workspace `dev`) |
| pytest-gremlins | **dev** (F34 / EV-059 / #874) | Python mutation testing (pytest plugin) — **MIT**; pinned `==1.9.0` (workspace `dev`); nightly/manual |
| @stryker-mutator/core (+ vitest-runner / typescript-checker) | **dev** (F34 / EV-059 / #874) | TypeScript mutation testing — **Apache-2.0**; pinned `10.0.0` in `apps/frontend` + `packages/shared`; nightly/manual |
| cargo / maturin | **required before cutover** | PyO3 wheel build in CI/API image (ADR-017) |
| xsdata | **dev/codegen** (F11 / ADR-027) | XSD → Python models from pinned IWXXM schemas — `xsdata[cli]>=24.5` in workspace `dev` |
| xsdata-pydantic | **dev/codegen** (F11 / ADR-027) | pydantic v2 output plugin — `>=24.5` in workspace `dev`; also `metar-shared[xsd]` for importing committed models |
| maturin | **dev** (F13/F14) | PyO3 wheel build — `>=1.7` in workspace `dev`; also CI |

**Deployables**: API + static frontend + **F8 worker** on **DOKS** (ADR-033; Render transitional).
API image depends on tac2iwxxm + validate + **auth** packages; worker image uses packages plus
poller/store writers via `DATABASE_URL`. Rust toolchain in API (and worker if linked) image for PyO3.

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

- S069 / EV-059 (2026-08-17): **schemathesis==4.24.3** (MIT) pinned in workspace `dev`;
  **pytest-gremlins==1.9.0** (MIT) + **@stryker-mutator/{core,vitest-runner,typescript-checker}@10.0.0**
  (Apache-2.0) pinned for #874 — F34 quality gates (`D-S069-tool`); mutation not a every-PR
  required gate; workflow `.github/workflows/mutation.yml` (schedule + workflow_dispatch)
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
- S019 / EV-014 T2.5 (2026-07-21): **testcontainers[mysql,postgres]≥4.8** — multi-DB writer-contract
  integration (TC-F16-003 / E14-09); SQLite in-process; PG/MySQL skip without Docker
- S019 / EV-014 T2.6 (2026-07-21): SQL Server via **aioodbc** + Testcontainers; integration
  tests **skip when no ODBC driver** (E14-06)
- S019 / EV-014 T2.7 (2026-07-21): ODBC driver install/verify notes in `docs/deploy.md` +
  `packages/dissemination/README.md` (E14-06); stock API image still omits `msodbcsql18`
- S019 / EV-014 T3.3 (2026-07-21): wis2box Compose harness — **lightweight MQTT+HTTP image**
  (`python:3.12.11-slim-bookworm` + Debian `mosquitto`); reject full WMO wis2box release stack
  for CI cost (E14-04 / Q17); not a Render service
- S019 / EV-014 T3.4 (2026-07-21): **httpx** + **aiomqtt≥2.3,<3** — concrete WIS2 transports
  for TC-F17-001 harness publish (D-S019-EV014-T34-transports); reject aiomqtt 3.x alpha
- S026 / EV-020 (2026-07-29): **PyYAML≥6.0** on `tac2iwxxm` for decode glossary YAML overlays
  (F9 / ADR-032; E20-F5)
- S036 / EV-029 (2026-08-02): **tac2iwxxm** workspace dep on `dissemination` for shared AHL
  helpers (E29-T2; `format_wmo_ahl` thin wrapper)
