# Architecture

> **Project**: TAC to IWXXM 
> **Repository**: https://github.com/EMPIRIC2/TAC-to-IWXXM 
> **Version**: monorepo + `tac2iwxxm` + operator UI (Quality metrics on stage) 
> **Last updated**: 2026-11-10

## Overview

This document describes system architecture, components, and hard constraints.
For runtime config and deploy hosts, use [technical-requirements.md](technical-requirements.md)
and its satellites. For the product capability list, use [product-requirements.md](product-requirements.md)
and [AGENTS.md](../AGENTS.md).

**What the product does**

TAC to IWXXM turns aviation Traditional Alphanumeric Code (TAC) messages into
World Meteorological Organization (WMO) IWXXM XML. Supported products include
AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA, and related forms.

| Concern | Package / location |
|---------|-------------------|
| Convert TAC → IWXXM | `packages/tac2iwxxm` |
| Lint TAC | `packages/tac-validate` |
| Validate IWXXM (XSD + Schematron) | `packages/iwxxm-validate` |
| Schema snapshots (read-only) | `vendor/schemas/` (WMO and optional NOAA IWXXM-US) |

**Repository shape**

The codebase is one Git monorepo:

- `apps/`: deployable services (API, frontend, worker, e2e)
- `packages/`: libraries
- `vendor/`: read-only upstream schema snapshots

**Runtime facts (platform independence / hybrid operator sessions)**

- Hosting is DigitalOcean Kubernetes Service (**DOKS**). Render is retired after soak.
- Product database is **DigitalOcean Postgres** via `DATABASE_URL`.
- **Supabase** verifies Auth JSON Web Tokens (JWTs) only. It is not the product database.
- Public convert, lint, validate, and disseminate routes need no JWT.
- Optional Supabase Auth gates long-term work sessions (`/api/v1/work-sessions*`).
- A near-realtime ingest worker writes to the same product Postgres.
- Dissemination uses one-shot Bring Your Own Credentials (**BYOC**): pasted secrets
 stay in memory only, with Server-Side Request Forgery (SSRF) controls and a required
 egress allowlist.
- The multi-product operator UI is the umbrella product track. **Quality metrics**
 (list + detail) is live on **staging**. Promote to production is deferred.

## System Architecture

### Runtime

```
Browser
 guest: IndexedDB (privacy-gated) + loss-of-progress notice
 login: Supabase Auth → JWT
 │ public /api/v1 convert/lint/validate/disseminate — no JWT
 │ /api/v1/work-sessions* — Bearer JWT (logged-in only)
 ▼
apps/frontend (static — DOKS/CDN or Vite dev)
 │ runtime /config.json → API base URL
 ▼
apps/backend (FastAPI — DOKS)
 ├── packages/auth — Supabase Auth JWT verify + /auth/*
 ├── public /api/v1/* (convert/validate/lint/decode/preview/dissemination) + abuse controls
 ├── /api/v1/work-sessions* → DigitalOcean Postgres (owner = Supabase user id)
 ├── packages/tac-validate | tac2iwxxm | iwxxm-validate | dissemination
 └── vendor/schemas/* (read-only)

apps/worker (DOKS — ingest worker)
 └── DATABASE_URL → DigitalOcean Postgres (store/quarantine; no Supabase DB)
```

`packages/gifts` remains absent. Supabase product PostgREST and the product database
are out of scope. Auth only. One-time migrate of legacy Supabase `tac_work_sessions`
(and related tables) into DigitalOcean Postgres. Alembic or the backend migration
path targets `DATABASE_URL`.

### Repository

```
TAC-to-IWXXM/
├── apps/
│ ├── backend/ # FastAPI — conversion, validation, auth routes
│ ├── frontend/ # React/Vite UI
│ ├── worker/ # ingest worker near-RT ingest poller (DOKS Deployment)
│ └── e2e/ # Playwright + cross-service integration
├── packages/
│ ├── auth/ # Supabase Auth JWT library (not a deployable)
│ ├── tac2iwxxm/ # General TAC→IWXXM (general TAC conversion); MIT; PyO3 required at cutover
│ ├── reference-lookup/ # Station and navaid coordinates for convert (general TAC conversion)
│ ├── tac-validate/ # TAC lint + business rules
│ ├── iwxxm-validate/ # XSD + Schematron (IWXXM validation); vendor consumers
│ ├── dissemination/ # dissemination drawer through AMHS SWIM AFS adapters sinks / writer-contract / SSRF 
│ ├── workflows/ # YAML execute(message, workflow) 
│ └── shared/ # API types, env helpers, constants
├── vendor/
│ ├── manifest.json # Pins upstream repo/tag/SHA or HTTP URL+hash per bundle
│ └── schemas/
│ ├── iwxxm/
│ ├── iwxxm-ca/ # Canada / ECCC national extensions (when pinned)
│ ├── iwxxm-codelists/
│ ├── iwxxm-modelling/
│ ├── iwxxm-translation/
│ └── iwxxm-us/ # NOAA/MDL national extensions (general TAC conversion)
├── workflows/ # Workflow YAML definitions
├── pyproject.toml # uv workspace root
├── pnpm-workspace.yaml
├── Makefile
└── docker-compose.yml # backend + frontend (+ worker optional locally)
```

### Component Overview

The table below maps each major component to its purpose, path, and main
dependencies. Later sections (**Component Details**) expand each row.

| Component | Purpose | Location | Dependencies |
|-----------|---------|----------|--------------|
| Backend API | Conversion, validation, auth; **Done** dissemination drawer through AMHS SWIM AFS adapters dissemination preflight/send (BYOC, memory-only); rule-catalog aggregator | `apps/backend/` | tac2iwxxm, tac-decoding, tac-validate, iwxxm-validate, dissemination, auth, shared, vendor |
| Frontend | Operator UI (workbench, decode, operator workbench sessions, five trust catalogs; dissemination drawer through AMHS SWIM AFS adapters drawer; **** Profile Builder authoring retired → dropdowns) | `apps/frontend/` | shared (types); CodeMirror 6 |
| E2E workspace | Cross-app tests | `apps/e2e/` | backend, frontend |
| Auth library | Supabase Auth JWT middleware (Auth-only) | `packages/auth/` | supabase-py / JWT verify |
| tac2iwxxm | TAC → IWXXM (7 products, bulletin split, profiles); decode re-export window | `packages/tac2iwxxm/` | tac-validate (optional), tac-decoding (re-export), reference-lookup, vendor; PyO3 required at cutover |
| reference-lookup | Station and navaid coordinates for convert (general TAC conversion) | `packages/reference-lookup/` | OurAirports public-domain files; checked-in table remains the fallback |
| tac-decoding | TAC → natural-language decode + glossary + Decoding catalog (live decode) | `packages/tac-decoding/` | , (no FastAPI/Supabase); MIT; PyPI `tac-decoding` |
| tac-validate | TAC lint / shared rule pack | `packages/tac-validate/` | , (no FastAPI/Supabase) |
| iwxxm-validate | XSD + Schematron (IWXXM validation engine) | `packages/iwxxm-validate/` | vendor schemas (read-only) |
| Dissemination | Sink adapters, writer-contract DDL, SSRF helpers (dissemination drawer through AMHS SWIM AFS adapters) | `packages/dissemination/` | SQLAlchemy async + dialect drivers; aiosmtplib |
| Shared | Cross-cutting utils/types | `packages/shared/` | — |
| Vendor schemas | Authoritative IWXXM SoT | `vendor/schemas/*` | wmo-im + iwxxm-us snapshots |
| Work history (work history/hybrid operator sessions) | Guest IndexedDB + logged-in DO Postgres sessions | FE IndexedDB + `tac_work_sessions` on DO | operator workbench / hybrid operator sessions; Auth JWT |
| Worker (ingest worker) | Near-RT ingest poller → store/quarantine | `apps/worker/` | `DATABASE_URL` → DO Postgres (platform independence) |
| Workflows | YAML executor `execute(message, workflow)` | `packages/workflows/` | tac2iwxxm, tac-validate, iwxxm-validate, pyyaml |
| Coverage gate harness | Unit coverage enforcement: pytest-cov + Vitest + per-file checker + scripts Python cov + bats-core | `scripts/ci/`, `tests/bats/`, CI matrix | / |

### Platform logical layers

Epic [](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) describes a **logical** layering model
(**Core → Profiles → Validation → Adapters → Dissemination**). Spike [](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/923)
and [](adr/-platform-logical-layers.md) **keep current package names** (Option C) and map
epic layers onto the monorepo below. Physical renames/splits (Option B) require a later evolve cycle
after contract spikes, close. **those spikes are now closed (–042, synthesis 2026-09-03).**

| Logical layer | Purpose | Current home(s) | Contract (ADR) | Runtime gap |
|---------------|---------|-----------------|----------------|-------------|
| **Core** | Shared IR types, constants, vendor helpers | `packages/shared`; IR inside `packages/tac2iwxxm` | Option C | Document boundaries only |
| **Profiles** | Semantic + exchange profile contracts, content, and operator-managed profile assets | Code: `tac2iwxxm/profiles/*`, `tac_validate/profiles.py`, `dissemination/exchange_registry.py`; content: `config/profiles/` | | Cross-version conversion framing , operator sharing , and quality backlog closeout deepen on top of the existing resolver and UI; destination credentials remain outside stored profile objects |
| **Conversion** | TAC→IWXXM encode | `packages/tac2iwxxm` | | Exchange packaging vs dissemination |
| **Decoding** | TAC→NL segments/summary + Decoding catalog | `packages/tac-decoding` (was tac2iwxxm) | / | Catalog export for operator workbench five-tab shell |
| **Validation** | Staged TAC then IWXXM | `packages/tac-validate` + `packages/iwxxm-validate` | PipelineResult | Unified runtime; `ca_eccc` reference |
| **Adapters** | SQL/DB symmetric source/sink mapping | `packages/dissemination` (`db_preflight`, `writer_contract`, `sink`) | MappingConfig | Source poll; sink mapping runtime |
| **Gateways / AFS** | AFTN/AMHS/EDIS/WIS2box + plan/audit | `packages/dissemination` (`edis`, `wis2`, `transports`, `packaging`) | DisseminationGateway | ** Planned:** façade + `health` + plan runtime |
| **Dissemination** | Policy, plan, retry, delivery audit | Same + FE drawer + **ops surface** (`apps/frontend`) | DisseminationPlan | ** Planned:** audit on `DATABASE_URL` + ops UI |
| **Workflows** | `execute(message, workflow)` | `packages/workflows` + `workflows/*.yaml`; ingest worker via `execute` | | Implemented |
| **Auth** | JWT middleware | `packages/auth` | — | Out of MET platform layers |
| **Apps** | HTTP / UI / worker / e2e | `apps/backend`, `frontend`, `worker`, `e2e` | — | Thin callers , no package move |

**Residual YAML :** detector hatch behavior moves into declarative detector YAML where the DSL can express it; decode airport names use a file/env YAML ICAO→name table (`set_location_name_resolver` remains an optional override); emit stays Python builders selected by emit-map `plugin:`, with a golden that an overlay swap changes output. No Schematron-as-YAML, no HTTP YAML bodies, no operator UI. Public `convert` and `decode_tac` wire stay stable.

**Approved milestone sequence** (epic synthesis): Core → Profiles → Validation →
Adapters → Dissemination → Workflows → Platform UIs (–).

**References:** Context: platform-package-layout-923 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
Context: epic-922-synthesis (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 session `reports/923-platform-package-layout.md`; `reports/922-epic-synthesis.md`.

## Component Details

### apps/backend

- **Purpose**: Single HTTP API for health, conversion, validation, lint, decode, soft-preview,
 dissemination, **optional Auth** (`/auth/*` via `packages/auth`), and **JWT-gated**
 `/api/v1/work-sessions*` (hybrid operator sessions). Convert/lint/validate/disseminate remain **public** (no JWT)
 with abuse controls (public operator app Amended). **No** `/admin/*` (operator workbench).
- **Data**: Product DB = **DigitalOcean Postgres** (`DATABASE_URL`). Supabase used only to
 **verify** Auth JWTs. no product PostgREST writes.
- **Migrations**: Alembic (or backend migration path) against `DATABASE_URL`, not Supabase CLI
 as SoT .
- : Restore Auth library + session APIs. ingest worker/store co-located on same DO DB.
 one-time migrate legacy Supabase session rows into DO.
- **Source**: general TAC conversion / . . / . **/ platform independence/hybrid operator sessions**.

### packages/tac2iwxxm

- **semantic and exchange profiles delta **: Profile plugins evolve from flat `annex3` / `iwxxm_us` to
 **semantic** ids (`ICAO_2025`, `US_FAA_NWS`, …) with legacy aliases until cutover.
 **Exchange** profiles (`GLOBAL_AFS`, `APAC_ROBEX`, …) apply on packaging paths in
 `packages/dissemination`, not in the TAC lexer. See [](adr/-semantic-vs-exchange-profiles.md)
 and [domain/profiles/](domain/profiles).
- **Purpose**: General TAC→IWXXM library (general TAC conversion). Python public API → **bulletin split** (WMO AHL)
 → versioned IR → product plugins → profile plugins (`annex3` / `iwxxm_us` → **semantic and exchange profiles** semantic ids)
 → XML writer. library/CI metrics via companion validate packages.
- **Products (v1)**: AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA.
- **Inputs**: TAC string/files **or bulletins**; `product`; `profile`; `iwxxm_version`; schema paths under vendor.
- **Outputs**: IWXXM XML bytes/strings (per report). metrics reports in tests/CI only (not convert API fields).
- ** deltas**: Decode/annotate ordered segments (`start`/`end` + short explanation).
 soft-preview / partial convert hooks returning best-effort XML + failed spans. VAA/TCA spans
 may be best-effort with explicit residuals (G4).
- ** delta (live decode)**: `decode_tac` explanations become **value-aware** (parsed values:
 temps, wind direction/speed/gusts, visibility, pressure, times, change groups) for all
 seven products (sparse ones best-effort), and the result gains a deterministic
 plain-language `summary` paragraph ("Not decoded: …" clause when residuals exist.
 "partial decode" wording for sparse products). Offsets and existing fields unchanged
 (additive). .
- **delta (published converter packages)**: Published to PyPI as `tac2iwxxm` `0.1.0`. optional extra
 `[validate]` depends on `tac-validate` + `iwxxm-validate`. Public convert API documented for
 third-party install.
- **delta (TAF and SPECI quality bar)**: Deepen **TAF (general TAC conversion)** and **SPECI (general TAC conversion)** convert/golden
 fidelity: exceptional-rule tables from . guidance + 2025-2 corrections. expanded
 annex3 / `iwxxm_us` goldens; convert → `iwxxm-validate` round-trip. Roots `iwxxm:TAF` /
 `iwxxm:SPECI`.
- **delta (SIGMET quality bar)**: Deepen **SIGMET (general TAC conversion)**: general `iwxxm:SIGMET` plus
 content-selected **`iwxxm:VolcanicAshSIGMET`** (VA phenomenon / WV AHL. still
 `product=sigmet` on HTTP). Exceptional-rule tables from . guidance + 2025-2
 corrections. expanded goldens. convert → `iwxxm-validate` round-trip. TC SIGMET OOS .
- **delta (VAA quality bar/TCA quality bar)**: Deepen **VAA (general TAC conversion)** + **TCA (general TAC conversion)** WMO golden bar:
 `canonicalize_xml` under defaults. see product-requirements VAA quality bar/TCA quality bar (**Done**).
- **delta **: Cross-product encode correctness deepen: NSC vs layered
 cloud; Guidance nils (`common/nil` vs `iwxxm/nil`); `translationFailedTAC` quarantine;
 dual-register colour href policy (offline vendor RDF/CSV). iwxxm-translation Amd79-80-2023
 TAC → 2025-2 as **informative** (no 2023-1 XML byte-match). default omit `translationCentre*`
 (optional config/request gate for Translation Centre). FIR/“S OF” polygon helpers (
 coord). COLLECT/multi-version hooks under dissemination drawer through AMHS SWIM AFS adapters (not single-report SoT). Runtime pin
 **v2025-2**.
- **deepen**: Maps pack span IR → legacy convert slots and
 can emit IWXXM from that path for METAR/SPECI. Default may flip to pack-IR emit when
 vendor peers stay byte-identical. `products/metar_speci.py` stays until a later delete-gate
 evolve. Does not fold `tac-decoding` into this package.
- **deepen **: Extend pack fill + pack-IR emit to
 all core products. `pack_ir_map` must map spans→slots **without** importing deleted
 `products/*.py`. Selective delete-gate: all-or-nothing per shared parser file when
 in-bar peers are byte-identical. keep files that fail. Does not merge packages.
- **SoC**: **No** FastAPI or Supabase imports.
- **Conversion catalog**: Package-owned Conversion trust-catalog rows
 (aggregated as `GET /api/v1/rule-catalogs?family=conversion`) are one row per semantic
 profile with a 1–3 sentence operator `summary` and `issue_type=profile` (`policy`
 reserved). Descriptions prefer existing profile registry / prose ( clean).
- **Runtime**: Pure Python v0. optional **Rust/PyO3** hotspots after benchmarks (not Cython).
- **License**: MIT.
- **IR**: **msgspec.Struct** . HTTP high-churn paths also msgspec .
- **Source**: [AGENTS.md](../AGENTS.md) general TAC conversion/published converter packages/TAF and SPECI quality bar/SIGMET quality bar/VAA quality bar/TCA quality bar. . . .
 evolve-decisions . context/general-tac-iwxxm-converter.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 context/package-publish-validation.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 context/aerodrome-quality.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 context/sigmet-quality.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).

### packages/tac-decoding

- **Purpose**: Deterministic TAC → natural-language decode (`decode_tac`), extensible glossary,
 and **Decoding** trust-catalog export (live decode /). Publishable PyPI package
 (`tac-decoding`) so open-source consumers can extend decode without the full converter.
- **Location**: `packages/tac-decoding/`
- **Constraints**: No FastAPI/Supabase imports. Catalog rows are read-only trust metadata
 (: no internal doc refs in operator-facing strings).
- **catalog deepen**: Decoding catalog export may include additive
 `issue_type` ( vocabulary), optional `severity`, `source_*`, and optional
 `conform_note`. Null/omit when unknown; FE must not invent defaults. Prefer `content`
 for glossary tokens that explain TAC groups/codes. best-effort public sources only.
 Aggregated via `GET /api/v1/rule-catalogs?family=decoding` .
- **Migration**: Logic moves from `tac2iwxxm.decode` / `glossary`; `tac2iwxxm` re-exports for
 one release then deprecates those entry points. **** keeps the shims, the legacy
 parsers, and the multi-pin compares.
- : The same packs also project convert IR.
 `tac2iwxxm` depends on `tac-decoding` for that IR. Decode must not import `tac2iwxxm`
 (bulletin split is an injected port). Layouts are token-stream, label-fields, and
 COLLECT (contained TAC, or an XML field walk when no TAC is present). No IWXXM encoder
 in this package. Legacy parsers, validation, and pin compares stay (`2023-1`,
 `2025-2`, `3.0.0`, and whatever pin a profile already requires). Packs do not
 choose the pin. the caller passes version and profile.
- **deepen**: Builtin METAR/SPECI packs gain real rules.
 `project_ir` remains span/residual IR only. Slot mapping and IWXXM emit from pack IR
 live in `tac2iwxxm`. When METAR/SPECI vendor goldens stay byte-identical, convert may
 default to the pack-IR emit path for those products without deleting legacy parsers.
- ** **: Builtin packs for remaining core products gain real
 rules. Span IR only in this package. mapper independence + selective parser delete live
 in `tac2iwxxm`.

### packages/tac-validate

- **Purpose**: TAC linting and shared **business-rule pack** for all seven product TAC forms
 (parse gate + rules). **Not** Schematron.
- **Inputs**: TAC text or bulletin fragments. product hint when known.
- **Outputs**: Structured issue list (severity, code, message, location. optional integer
 `start`/`end` character offsets for editor highlight. ).
- ** delta (workbench preview)**: Severity enum `error | warning | info`; `ok` computed from `error` only.
 `MISSING_TERMINATOR` → `info` with actionable copy + paired `add_terminator` fix entry
 (`replacement` = text with `=` appended) powering the UI quick fix. .
- **delta (TAC validate package)**: Published to PyPI `tac-validate` `0.1.0`. encode mined
 `docs/domain/` rules: full depth METAR/SPECI/TAF. SIGMET/AIRMET/VAA/TCA templates + gates.
 cite-only for paywalled Annex text. CLI for CI.
- **delta (METAR and SPECI quality bar)**: **Issue registry** module is the single source of lint
 `code` + default `severity` + message template . Rules import registry entries.
 docs/generated catalog lists codes. METAR rule pack expanded (R1–R6 + opportunistic).
 CI rejects unknown codes. Public codes stable. severities may tighten in minor releases.
 Workbench METAR lint+convert smoke under METAR and SPECI quality bar (operator workbench status unchanged).
- **delta (TAF and SPECI quality bar)**: Same registry. add/extend **TAF** codes and deepen **SPECI**
 rules/fixtures to the full quality bar (not residual-only). Coverage-matrix TAF + SPECI
 rows. exceptional-rule accept/negative packs. Workbench `product=taf` / `product=speci` smoke
 under TAF and SPECI quality bar (operator workbench status unchanged). No new registry architecture ( reuse).
- **delta (SIGMET quality bar)**: Same registry. add/extend **SIGMET** (+ VA SIGMET) codes and
 fixtures to the full quality bar. Coverage-matrix themes G1–G3 / V1–V3 / C1.
 exceptional-rule accept/negative packs. Workbench `product=sigmet` (+ VA fixture) smoke
 under SIGMET quality bar (operator workbench status unchanged). No new registry architecture ( reuse).
- **delta **: Tighten NSC / related lint beyond research `NSC_PRESENT` if
 needed for P0 exclusivity with layered cloud. registry codes only (no new architecture).
- **SoC**: **No** FastAPI or Supabase imports.
- **Source**: product-requirements general TAC conversion/TAC validate package/METAR and SPECI quality bar/TAF and SPECI quality bar/SIGMET quality bar. / . / . / .
 / . / . / . / 
- : Detector packs (small DSL + `python:`
 hatch), TAC quality policy runtime, optional MatchPort for decode spans. Registry remains
 code SoT. Activate fail-closed. overlays file/env only.

### packages/iwxxm-validate

**Developer experience :** Public jobs must be reachable from plain
module and symbol names. See . Pilot: Canonical XML helpers
for Quality Metrics compare use a clear primary path (not jargon-only `c14n`),
with aliases during one CalVer window. DX tests: ``…``.

- **Purpose**: IWXXM validation engine: XSD + Schematron validation of IWXXM XML against vendored schemas.
- **Inputs**: IWXXM XML; `iwxxm_version`; optional `profile` (US catalogs when `iwxxm_us`).
- **Outputs**: Validation report (pass/fail + messages).
- **delta (IWXXM validate package)**: **Rust core** (well-formed + XSD + native Schematron/SVRL)
 via PyO3. Python SDK. pinned schemas **bundled** in the wheel. PyPI `iwxxm-validate` `0.1.0`.
 Parity suite vs historical lxml isoschematron. Optional **XSD-derived** typed models
 (codegen. validation performance). UML modelling is provenance only. TAC has no official model.
- **delta **: SCH/XSD **negative** fixtures for NSC+layers. dual-register
 colour / dual nil RDF policy tests under offline vendor SoT (v2025-2 pin).
- **SoC**: **No** FastAPI or Supabase imports. **read-only** consumption of `vendor/schemas/*`
 (and bundled copies in published wheels).
- **Source**: product-requirements IWXXM validation/IWXXM validate package. context/realtime-tac-ingest.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 context/package-publish-validation.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 evolve-decisions 
- : Assert inventory + IWXXM output policy
 runtime (enable/disable by assert id. Schematron bundle refs). XSD/well-formed always error.
 Vendor `.sch` remains SoT.

### packages/gifts

- **Status**: Deleted in the first PR that wires tac2iwxxm to `/api/v1/convert` .
- **Historical**: Fork of mgoberfield/GIFTs. REQ-014 / / GIFTs package deprecated.

### vendor/schemas

- **Purpose**: Read-only copies of upstream schema repositories at pinned tags.
- **Inputs**: `vendor/manifest.json` pins. sync script/Action fetches release artifacts
 (wmo-im iwxxm-* and IWXXM-US. URL/tag TBD in 04).
- **Outputs**: XSD, Schematron, codelist files consumed by `iwxxm-validate` and tac2iwxxm.
- **Constraints**: **No direct edits** in monorepo except manifest version bumps via sync PRs.
- **Source**: REQ-002, REQ-012. /014.

### packages/shared

- **Purpose**: Shared API types (OpenAPI-derived TS), env URL helpers, constants (CORS origins,
 version enums, general TAC conversion product/profile enums).
- **Config loader **: Loads `config/deploy/profiles/{local,prod}.json` by `METAR_CONFIG_ENV`. exposes merged
 config to Python and TypeScript. secrets resolved from env only.
- **Source**: REQ-010, .

### apps/frontend

- **Purpose**: Public converter UI (product/profile/version), CodeMirror 6 workbench, decode
 panel, Failed-TAC / soft-preview UX, **IndexedDB** work history My METARs + operator workbench multi-product sessions
 (operator workbench), and privacy preference center privacy notice/settings. **Done (dissemination drawer through AMHS SWIM AFS adapters)**: Dissemination drawer + APIs
 remain for harness. : Operator Dissemination sink chooser /
 Convert&Send / Upload to Database **restored** . drawer exchange overlay .
 **mass file ingest**: Auth-gated mass file/folder ingest (caps 200 / 5 MiB / 50 MiB. sniff/zip-bomb).
 **operator workbench deepen **: Queue + keyboard + batch convert/validate . **No**
 AdminDashboard, `/admin/*` (public operator app public convert. Auth optional for hybrid operator sessions/mass file ingest mass).
- **Quality metrics (staging)**: Primary shell tab `/quality` lists official WMO corpus
 stems. detail `/quality/:stem` with Official/Converted panes and GitHub-style collapsible
 unified diffs (C14N match. promote deferred).
- **operator workbench accumulate ZIP **: Workbench accumulates sequential successful IWXXM
 results. Download all → one ZIP with **IWXXM `.xml`** members plus matching **TAC source**
 members (`.txt` / `.tac` / `.metar`). IWXXM download names never keep TAC extensions.
 default stem ≈ first 8 sanitized TAC chars of first
 success + timestamp. clear/reset. soft cap **≤200**. Dissemination multi-select unchanged.
- **operator workbench validate-only **: Dedicated Validate mode: paste or single `.xml`
 upload via existing `POST /api/v1/validate` (reuse unless 04 finds a gap). IWXXM version handling
 version/profile parity. guest-usable. Orthogonal to Quality metrics.
- **operator workbench IWXXM product **: Product select includes **IWXXM**. Pass-through:
 lint well-formed XML + IWXXM validation XSD/Schematron. **no** TAC convert. Convert control disabled or
 no-ops with a clear operator message. operator workbench Validate-only **remains**. FileConverter /
 accumulate / Quality metrics honor `product=iwxxm`.
- ** AHL bulletin **: AHL heading is bulletin COM. contained reports lint with
 the selected TAC product. Do not score AHL tokens as METAR/TAF syntax.
- ** profile picker **: Labeled Profile (Annex 3 / IWXXM-US) at converter **top**.
 applied to convert/lint/validate. accessible name+label.
- **general TAC conversion delta**: Product select (7 TAC values + **IWXXM** pass-through + auto-detect), profile
 select (`annex3` | `iwxxm_us`), version control; values passed via `conversion_params` /
 multipart to `/api/v1/convert`.
- **operator workbench convert-params **: Hard Convert maps Bulletin ID, Issuing Center, On Error →
 `stop_on_error`, and Strict Validation → `validate_output`/`validation_level`. Soft-preview
 skips post-convert validation. Console Log Level filters workbench lines client-side.
 ** **: `log_level` also sets backend/package **logger verbosity**. **
 **: Bulletin ID and Issuing Center are labeled, editable, and sent on convert
 (empty → discover-from-AHL or defaults).
 Upload accept: `.txt`, `.metar`, `.tac`.
- **operator workbench delta (public operator app amend)**: Debounced **public** calls to lint/decode/validate/preview with
 AbortController. span highlight + hover. collapsible Code|Explanation decode panel. toggleable
 live IWXXM. pull-up console. **local** operator workbench session persist/resume (IndexedDB, not server).
- **operator workbench input modes **: TAC | AHL bulletin (`/convert-bulletin`) | IWXXM COLLECT
 (`/ingest-collect` 501 placeholder). Accept `.xml`/`.gz` (inflate). `log_level` +
 `include_nil_reasons` on Convert. Log Level filters Conversion log + console for lint/validate
 process messages. **Validation**: / TC-operator workbench-007 : auto-switch
 required. COLLECT 501 honest UX. operator workbench status unchanged.
- **operator workbench golden examples **: Static frontend catalog (copied package
 goldens) + Examples control in FileConverter. loads TAC / AHL / happy-path IWXXM into
 existing modes. sets product/inputMode. demo labeling. No new API routes. Soft-fail XML
 and file-upload queue deferred. / TC-operator workbench-008. operator workbench status unchanged.
- **operator workbench / work history **: Work history for all seven products in IndexedDB. My METARs =
 `product IN (metar, speci)` local filter; **no** `/api/v1/work-sessions`.
- **live decode/workbench preview delta **: Decode panel gains a top **"Plain language"** block rendering the
 backend `summary` live (existing debounce path). New **side-by-side IWXXM preview pane**
 (stacked < `lg`) anchors Soft-preview / Live IWXXM output: pretty-printed XML + status
 badge ("Soft preview , not for publish" plain-language copy vs "Passed") + failed-span
 count linked to editor highlights. Lint console renders `info` severity distinctly with a
 one-click **"Add `=`"** quick fix (also as editor affordance on the hint span). .
- **Source**: general TAC conversion-R5. product-requirements general TAC conversion/operator workbench/live decode/workbench preview/public operator app/privacy preference center. context/f7-operator-ui.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).

### live TAC map

- **Purpose**: Guest-visible Leaflet map of current aviation weather on Decode visuals. The API timer pulls Aviation Weather Center feeds, stores every fetched location, translates at most 40 reports per tick, and serves the cache. 
- **Home**: `apps/frontend` Decode visuals and `apps/backend` live-map router plus the existing database. The ingest worker worker stays at 0 replicas.
- **Read path**: `GET /api/v1/live-map` is public. It returns places already in the cache for the requested box and families. It does not call a feed.
- **Write path**: About every 5 minutes the API process stores every fetched location and text. It translates and lints at most 40 reports. A stored place is drawn before IWXXM exists. Three reports per place, newest first.
- **Map**: Leaflet with the current tiles. World zoom draws one marker per continent that has reports. The next zoom draws sub-region markers. A closer zoom draws each station and shape on its own product layer. Colors are fixed: METAR `#1d4ed8`, SPECI `#0369a1`, TAF `#0f766e`, AIRMET `#c2410c`, G-AIRMET `#a16207`, SIGMET `#b91c1c`, volcanic ash `#6d28d9`, tropical cyclone `#be185d`, volcano notice `#4338ca`. Fills and outlines differ. The newest report is solid. The two earlier reports are faded. Hover highlights the shape. Co-located airport reports are offset and each has a type chip. 
- **Hover**: The card shows the product, issue time, and station, or Area when there is no airport. Scrollable TAC sits to the right on a wide screen and below the metadata on a narrow screen. The card opens on the newest stored report. A control selects an earlier copy. Clicking the shape or the card loads that copy into the converter above the map. Stored IWXXM stays off the map list.
- **Filters**: Group headings stay. Each product is its own checkbox and layer, including `gairmet` under Hazards. Space weather is a list, never a pin. The list uses `#0e7490` when it has rows. This cycle does not add a space-weather feed. Country, region, issue time, and hazard phenomenon filter the loaded view in the browser. They are not `GET /api/v1/live-map` parameters. Country defaults to all countries and uses the existing airport country for ICAO stations. Area reports stay. Region defaults to all regions and uses the existing continent and sub-region names. Time defaults to all reports, with presets for the last hour, last 6 hours, and last 24 hours, judged from the newest report. Phenomenon checkboxes start off. IFR, Turbulence, Icing, and Thunderstorms apply only to AIRMET, G-AIRMET, and SIGMET. A hazard stays when its newest TAC matches any checked phenomenon. 
- **Must not change**: Convert and validate response bodies, guest access, station search, continent and sub-region zoom, the tile source, and the live-map query parameters.

### Runtime configuration

- **Purpose**: Non-secret per-environment settings (URLs, CORS, validation flags).
- **Files**: `config/deploy/profiles/local.json`, `config/deploy/profiles/staging.json`, `config/deploy/profiles/prod.json`, `config/deploy/profiles/e2e.json` (committed).
- **Frontend**: Static host serves `/config.json` (prod copy + publishable key injected at deploy).
- **BYO (R6)**: Operator deploy env supplies Supabase URL/keys (and optional app
 `DATABASE_URL` for legacy primary upload). **No** in-app paste of **Supabase auth** keys.
- **Dissemination BYOC **: Users may paste **one-shot destination** credentials
 (DB URI / WIS2 / EDIS SMTP / AMHS params) in the dissemination drawer. API memory-only.
 required `DISSEMINATION_EGRESS_ALLOWLIST` .
- **Source**: [env-variable.md](env-variable.md), session. / 

### User METAR work history

- **Purpose**: Durable converter work history for METAR/SPECI (and operator workbench all-product sessions).
- **Guest**: Browser IndexedDB. loss-of-progress notice. privacy preference center may gate non-necessary local store.
- **Logged-in**: `/api/v1/work-sessions*` → **DO Postgres** `tac_work_sessions` (owner =
 Supabase Auth user id). On login: **auto-upload** eligible local drafts (=2).
- **Legacy**: One-time migrate prior Supabase rows into DO this cycle. no ongoing Supabase DB reads.
- **Source**: work history. R2″. ** R2‴ / hybrid operator sessions**.

### Multi-product operator UI / sessions

- **Purpose**: Operator UI for seven general TAC conversion products + hybrid sessions (**operator workbench**hybrid operator sessions).
- **Slices**: operator workbench–operator workbench as before. **operator workbench** restores JWT session APIs to DO Postgres for logged-in users.
- **operator workbench **: ConversionProfile editor: rule-pack CRUD, inspector,
 signed operator overlays on product Postgres (`DATABASE_URL`) with JWT ownership. .
 Complements light picker . does not merge destinations/credentials into profiles.
- **delta on operator workbench**: keep the workbench Profile affordance compact while making
 Conversion Profiles the glanceable summary surface: summary composition first, compare on that
 surface only, guests see pack/overlay count placeholders until signed in, all registered
 semantic profiles get profile-aware examples, starter packs/overlays seed only when untouched,
 and profile changes refresh the summary/catalog without resetting unrelated in-progress state
 unless a profile-dependent control becomes invalid. 
- **delta on operator workbench**: parameterizable conversion templates as the default
 Conversion rule object. slot-builder + TAC→IWXXM bridge UI (phase-1). first-party view/fork.
 custom JWT owner CRUD. fail-closed unknown ids. amend. Dissemination rules
 remain Disseminate / Convert & Send only. 
- **delta on operator workbench**: YAML-backed Five Libraries +
 Draft/Activate + validate-yaml + optional Convert `*.meta.json` sidecar ( EVPYL).
 Phase A shell on `stage` via PR . 
- **delta on operator workbench**: IDE workbench (catalog | editor |
 optional previews). **remove Conversion DnD**. renamable preset slots. full editable TAC/IWXXM
 validation (regex, levels, shared numeric ops). Decoding maps/units/structured types.
 Dissemination create/edit without new protocols or secrets. Overview compare + per-profile
 product/file-type/IWXXM version enablement. YAML SoT retained ( EVWB). Journeys
 -*. tests -*. 
- **API**: Public convert companions unchanged. session CRUD requires Auth JWT. operator workbench pack/overlay
 mutate routes require JWT (see [api-contract.md](api-contract.md) §). conversion
 template routes require JWT for custom mutate (see §). library-assets YAML mutate +
 validate-yaml require JWT (see § / §).
- **Source**: . operator workbench. **operator workbench**. ** operator workbench**. .
 ****. ****.
 Context: conversion-profile-editor-933 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 Context: [profile-builder-workbench-edit](context/profile-builder-workbench-edit.md) (scoped. not a design document set design gate).

### Public convert + optional Auth

- **Purpose**: Keep convert/validate/lint/decode/preview/dissemination public. optional Supabase
 Auth only for long-term server sessions (hybrid operator sessions). Abuse controls remain.
- **Source**: . **public operator app Amended**hybrid operator sessions. [AGENTS.md](../AGENTS.md).

### privacy preference center

- **Purpose**: Solution A + GPC. disclose IndexedDB. deepen to gate guest local history and
 disclose Auth cookies when login is used.
- **Source**: . hybrid operator sessions deepen.

### Near-realtime ingest

- **Purpose**: Continuous ingest → pipeline → store. quarantine on fail. scale via worker replicas.
- **Deploy**: DOKS Background/Deployment worker (`apps/worker/`). **DO Postgres** via
 `DATABASE_URL` (co-located with work sessions). No Supabase service-role DB writers.
- **Non-goals (ingest worker worker path)**: public machine-ingest auth UX. **automatic** push of ingest
 results (operator dissemination sinks are **dissemination drawer through AMHS SWIM AFS adapters**, not ingest worker auto-push).
- **Source**: . **platform independence**. [AGENTS.md](../AGENTS.md) ingest worker.
- : Cut over to `packages/workflows.execute` + `workflows/f8-metar-ingest-default.yaml`
 . See Context: workflows-runtime-1132 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).

### packages/workflows

- **Purpose**: Thin MET-lib workflow executor: load git `workflows/*.yaml`, run fixed stage
 registry (`validate-tac` → `convert-iwxxm` → `validate-xsd` / `validate-schematron` for MVP),
 return `WorkflowResult`. Apps remain thin callers.
- **SoC**: **No** FastAPI, Supabase, or SQLAlchemy. store/quarantine via injected ports.
- **Status**: **Implemented** . contract Accepted in .
- **Source**: [](adr/-workflow-definitions.md).
 Context: workflows-runtime-1132 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).

### platform independence

- **Purpose**: Supabase Auth-only. DO Postgres product DB. DOKS production cutover. amend .
- **Source**: [AGENTS.md](../AGENTS.md) platform independence. .

### hybrid operator sessions

- **Purpose**: Guest local + notice. logged-in DO sessions. auto-upload. privacy preference center interaction.
- **Source**: [AGENTS.md](../AGENTS.md) hybrid operator sessions.

### dissemination drawer through AMHS SWIM AFS adapters deepen

- **Purpose**: Runtime **DisseminationGateway** façade (`validate` / `send` / `health`) over
 existing sinks. **DisseminationPlan** execute + delivery audit on product Postgres. operator
 **Dissemination ops** surface (plan/audit/SQL mapping/gateway health) alongside the destinations
 drawer. JWT for ops/plan/audit/mapping/health. public preflight/send unchanged (public operator app).
- **Non-goals**: . live AFTN/failover features. secrets in audit UI. new packages.
- **Source**: [AGENTS.md](../AGENTS.md) §dissemination drawer through AMHS SWIM AFS adapters deepen .
 Context: dissemination-ops-936 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate). / .
 [evolve-decisions.md](decisions/evolve-decisions.md) §. .

### dissemination drawer through AMHS SWIM AFS adapters

- **Purpose**: Unified dissemination **drawer** for sending converted (or drag-dropped) IWXXM/TAC
 to operator-chosen destinations with schema/connectivity preflight.
- **dissemination drawer**: Multi-DB upload (Postgres, MySQL/MariaDB, SQL Server, SQLite) via one-shot URI.
 DDL/create-if-missing vs versioned writer contract. SSRF + allowlist.
- **dissemination drawer deepen **: **Export selection** multi-select for current-session
 outputs + dropped files. select-all/clear. empty selection disables Preflight/Send. client
 **N sequential** `/preflight`+`/send` with per-file aggregated results. selection count
 **≤20**. Finished IndexedDB history and batched multi-payload API **out of scope** v1.
 WIS2 dissemination through AMHS SWIM AFS adapters reuse the same selection UI contract.
- **dissemination drawer deepen **: Live local multi-DB SQL ingest via Playwright against
 `docker-compose.yml` profile `mock-byoc` (Postgres / MySQL / SQL Server + disposable SQLite). separate
 from mocked H6′. mandatory teardown across integration / e2e / local Compose. No new
 components. test/harness deepen of existing drawer + `packages/dissemination`.
 
- **WIS2 dissemination**: WIS2 publish. staging wis2box harness for test. live BYOC waived at close (Q15).
- **EDIS dissemination**: EDIS-compliant submit to RTH Washington. BYOC SMTP/gateway in drawer. live waived (Q15).
- **AMHS SWIM AFS adapters**: AMHS / SWIM / AFS adapters in the same drawer (staging stubs. live optional).
- **Auth / work history**: Public dissemination (public operator app. no operator JWT). Local session may record
 `kv_upload_key` on Finished in IndexedDB only. never store destination secrets.
- **Status**: **Done** ( closed 2026-07-21. PR ). Multi-select deepen .
 live local SQL e2e deepen / : Operator UI destinations
 **restored** (URI-BYOC + WIS2 dissemination through AMHS SWIM AFS adapters sinks). drawer exchange overlay. APIs +
 `packages/dissemination` unchanged. connection-first preflight retained.
- **ADRs**: amend (destination paste). (SSRF / allowlist). 
 (`packages/dissemination` + sink/API/wis2box/EDIS).
- **Source**: [AGENTS.md](../AGENTS.md) dissemination drawer through AMHS SWIM AFS adapters. / #2 / #6. evolve-decisions .
 **. evolve-decisions **. **evolve-decisions **. **/ **.
 **/ **.

### Secure mass file/folder ingest

- **Purpose**: Authenticated mass multi-file + folder/zip TAC ingest with progress, per-file
 errors, content sniff + zip-bomb guards. feeds convert/validate queue (no operator
 dissemination destinations this cycle).
- **Caps**: ≤200 files. ≤5 MiB each. ≤50 MiB total unzipped. May require raising
 `MAX_REQUEST_BODY_BYTES` or a dedicated mass-ingest limit (Gate A decision).
- **Status**: **Planned**. [AGENTS.md](../AGENTS.md) §mass file ingest. . TC-mass file ingest-*.
- **Source**: . evolve-decisions . mass ingest section.

### TAF and SPECI quality bar

- **Purpose**: METAR and SPECI quality bar sequel: raise **TAF** and **SPECI** lint / convert /
 IWXXM-validate quality to the METAR/SPECI bar. Reuse registry. deepen general TAC conversion/general TAC conversion and TAC validate package.
- **Encode authority**: WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections (no `runwayState`).
 FM 205 / Manual on Codes I.3. pinned XSD + Schematron.
- **TAF exceptional rules** (fixtures or explicit deferrals): NIL, CNL, AMD, COR, CAVOK, NSC,
 NSW, VV///, FM/TL/AT, TX/TN on base forecast, change groups FM/BECMG/TEMPO/PROB.
- **SPECI**: Full AC parallel to TAF. shared METAR/SPECI pack + mis-classification guards
 (Auto-detect / product hint never silent-swap SPECI↔METAR).
- **Status**: **Done** .
- **Non-goals**: Sibling product-quality tickets. PyPI bumps. dissemination drawer through AMHS SWIM AFS adapters changes. new ADR unless
 registry architecture changes.
- **Source**: [AGENTS.md](../AGENTS.md) TAF and SPECI quality bar. . context/aerodrome-quality.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).
 evolve-decisions . .

### SIGMET family quality bar

- **Purpose**: METAR and SPECI quality bar/TAF and SPECI quality bar sequel: raise **General SIGMET** and **VA SIGMET** 
 lint / convert / IWXXM-validate quality. Reuse registry. deepen general TAC conversion and TAC validate package.
- **Encode authority**: WMO `TAC-to-XML-Guidance.txt` + 2025-2 corrections. FM 205 /
 Manual on Codes I.3. pinned XSD + Schematron. EUR Doc 014 (public TAC shape) cite-only.
- **General SIGMET exceptional rules** (fixtures or explicit deferrals): CNL, single-point →
 `gml:CircleByCenterPoint` radius zero, single altitude (same lower/upper), STNR, polygon/line
 with declared CRS. sequence / validity / FIR/CTA / phenomenon / movement / intensity.
- **VA SIGMET**: Apply general mapping then volcano identity + ash geometry / forecast.
 `NO VA EXP` → `nothingOfOperationalSignificance`. CNL FIR-moved-ash. root
 `iwxxm:VolcanicAshSIGMET` (not `iwxxm:SIGMET`, not VAA).
- **API**: `product=sigmet` unchanged. root selection is package-side from TAC content
 (=A). No new routes.
- **Status**: **Done** (PR ).
- **Journeys / tests**: . quality bar-001..006. matrix themes G1–G3 / V1–V3 / C1.
- **Non-goals**: TC SIGMET. AIRMET / VAA / TCA / SWX / VONA. PyPI bumps. dissemination drawer through AMHS SWIM AFS adapters.
 new `product` enum . FE: **additive catalog filters for SIGMET/VA tags** in scope
 (=B amends ). new ADR unless registry architecture changes.
- **Source**: [AGENTS.md](../AGENTS.md) SIGMET quality bar. .
 context/sigmet-quality.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate). evolve-decisions . .

### AIRMET quality bar

- **Purpose**: AIRMET quality peer to SIGMET quality bar. WMO `airmet-A6-1a-TS` golden under **defaults**.
- **Status**: **Done** (PR ).
- **Journeys / tests**: . quality bar-001..005.
- **Policy**: (default `canonicalize_xml` equality).
- **Source**: product-requirements AIRMET quality bar. evolve-decisions . /032.

### WMO official example parity + UI gate

- **Purpose**: METAR/SPECI/TAF vendor golden equality under defaults. Examples catalog marks
 **strict** WMO-passers (plus SIGMET/AIRMET keepers when green). ** amend**: official
 WMO **reference** samples may also load .
- **Status**: **Done** (PR ). catalog deepen **Done** (PR ).
- **Journeys / tests**: . ****. example parity-001..004. . deepen / TC-operator workbench-008.
- **Policy**: (amended ).
- **Source**: product-requirements WMO example parity. evolve-decisions / 

### VAA quality bar

- **Purpose**: VAA (`iwxxm:VolcanicAshAdvisory`) quality peer to SIGMET quality bar/AIRMET quality bar. WMO
 `va-advisory-A7-2` TAC→IWXXM **`canonicalize_xml`-equal** under default convert settings
 . Registry-backed lint . Themes **VAA quality bar V1–V3 / C1**. Do not confuse with
 VA SIGMET (`iwxxm:VolcanicAshSIGMET`).
- **Status**: **Done** (PR ).
- **API**: `product=vaa` already in enum. no new routes.
- **Journeys / tests**: . quality bar-001..006. deepen / TC-operator workbench-008.
- **Fixtures**: Mine TAC themes from `iwxxm-translation` Amd79-80-2023. no Amd79 XML
 byte-match under 2025-2 (E21-D4).
- **Non-goals**: VA SIGMET . TCA is TCA quality bar. SWX . VONA . translation-failed as
 happy-path golden. PyPI bumps.
- **Source**: product-requirements VAA quality bar. evolve-decisions . /032.
 sessions/-quality/reports/wmo-vaa-tca-examples-inventory.md.

### TCA quality bar

- **Purpose**: TCA (`iwxxm:TropicalCycloneAdvisory`) quality peer. WMO
 `tc-advisory-A2-2` golden under defaults. Themes **TCA quality bar T1–T3 / C1**. Do not confuse with
 TC SIGMET (`iwxxm:TropicalCycloneSIGMET`. quality path absorbed in **/ **).
- **Status**: **Done** (PR ). **Deepen**: / (B4).
- **API**: `product=tca` already in enum. no new routes.
- **Journeys / tests**: . quality bar-001..006. deepen / TC-operator workbench-008.
- **Fixtures**: Same translation-package mine policy as VAA quality bar (E21-D4).
- **Non-goals** (original TCA quality bar): VAA is VAA quality bar. VONA. translation-failed happy-path. PyPI.
 TC SIGMET + SWXA moved to / SWXA quality bar.
- **Source**: product-requirements TCA quality bar. evolve-decisions . /032.
 sessions/-quality/reports/wmo-vaa-tca-examples-inventory.md.

### SWXA quality bar

- **Purpose**: / Space Weather Advisory (`iwxxm:SpaceWeatherAdvisory`) quality peer
 to METAR and SPECI quality bar through TCA quality bar. Completes the eight-family TAC→IWXXM converter set. TAC AHL `FN` → IWXXM `LN`.
 Registry-backed lint . golden policy .
- **Status**: **Done** (PR ).
- **API**: Additive **`product=swxa`** on convert / convert-bulletin / lint-tac / decode-tac
 (api-contract). No new routes or deployable. No `swx` alias.
- **Components**: `packages/tac-validate`, `tac2iwxxm`, `iwxxm-validate`. domain docs. fixtures.
- **Journeys / tests**: ****. quality bar-001..006. cycle -*.
- **Non-goals**: VONA . SIGWX / QVACI. dissemination sink UI. GIFTs-as-normative.
- **Source**: product-requirements SWXA quality bar. evolve-decisions .
 Context: eight-family-ahl-rules-823 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate).

### Eight-family AHL / lint / convert / validate

- **Purpose**: Mine-then-implement gap sweep across eight TAC families × lint / convert /
 IWXXM-validate, with bulletin/AHL/COM first, then product-by-product. Shared AHL/`T1T2`/
 filename model for conversion + dissemination drawer through AMHS SWIM AFS adapters consumers. Absorb / / (**SWXA quality bar**).
- **Status**: **Done** (PR ). Residuals → / .
- **Components**: domain mining + canonicals. `tac-validate` / `tac2iwxxm` / `iwxxm-validate`.
 thin `packages/dissemination` AHL helpers. fixtures/CI. FE only if Examples unlock.
- **Journeys / tests**: ****. . quality bar-001..006. deepen prior product TCs.
- **Non-goals**: SIGWX / VONA / QVACI as TAC inputs. WIS2 mining. sink UI. vendor hand-edits.
- **Source**: product-requirements deepen + SWXA quality bar. evolve-decisions . .

### Parameterized rule quality matrices

- **Purpose**: maintainable 5×4 (happy/sad/edge-pass/edge-fail) parameterized matrices
 covering lint · convert · IWXXM-validate rules with inventory gate and design-before-bulk.
- **Status**: **Done** (PR ).
- **API**: No new public routes for v1 (CI/pytest harness). No new deployable.
- **Components**: test runners under `packages/*` and/or `tests/`. issue-registry / Schematron /
 encode rule indexes. CI smoke + optional full matrix job.
- **Journeys / tests**: ****. TC-parameterized rule matrices-001..007. cycle -*.
- **Non-goals**: 100% Annex-3 coverage in first PR. live network/Supabase coupling.
- **Source**: product-requirements parameterized rule matrices. evolve-decisions .
 Context: quality-residuals-831 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate). .

### Quality residuals / /

- **Purpose**: Close residuals in order: parameterized rule matrices rule matrices → TC SIGMET deepen
 → VAA/TCA decode deepen .
- **Status**: **Done** (PR ). Residual → [](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) (A6-2-TC equality).
- **Components**: parameterized rule matrices harness. `tac-validate` TC pack. catalog/menu tier for A6-2-TC. decode
 engine for VAA/TCA labels. matrix/allowlist updates.
- **Journeys / tests**: ****. -*. TC-parameterized rule matrices-*. deepen quality bar/live decode/VAA quality bar/TCA quality bar. H4–H5 iff FE.
- **Non-goals**: Supabase strip. WIS2 mining. SIGWX/VONA/QVACI (VONA → / VONA quality bar).
- **Source**: product-requirements parameterized rule matrices + deepen. evolve-decisions . .

### VONA quality bar

- **Purpose**: Volcano Observatory Notice for Aviation
 (`iwxxm:VolcanoObservatoryNoticeForAviation`) quality peer to METAR and SPECI quality bar through SWXA quality bar. Guidance file silent.
 XSD + SCH + `vona-A7-1` + PANS-MET. Full operator workbench product surface this cycle .
- **Status**: **Planned** (epic ).
- **API**: Additive **`product=vona`** on convert / convert-bulletin / lint-tac / decode-tac
 (api-contract). No new routes or deployable. Keep-whole multiline TAC.
- **Components**: `packages/tac-validate`, `tac2iwxxm`, `iwxxm-validate`. FE product picker +
 Examples catalog. domain docs. fixtures.
- **Journeys / tests**: ****. quality bar-001..006. cycle -*.
- **Non-goals**: Metrics UI . SIGWX / QVACI. vendor hand-edits.
- **Source**: product-requirements VONA quality bar. evolve-decisions .
 Context: iwxxm-corpus-quality-846 (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate). .

### Official IWXXM corpus quality / WMO source parity

- **Purpose**: Under epic , in order: A6-2-TC → `wmoPass`. / **VONA quality bar** VONA bar +
 full operator workbench surface. release-line adoptability (docs/checklists, no re-pin). corpus /
 WMO-source parity children (iwxxm, iwxxm-translation, iwxxm-codelists, codes.wmo.int,
 iwxxm-modelling).
- **Status**: **In progress** .
- **Components**: encode/lint/validate packages. FE picker/catalog. domain version-policy docs.
 fixture/CI gates. no new deployable.
- **Journeys / tests**: ****. -*. quality bar-*. deepen /039/042/043/044. H4–H5
 when FE ships.
- **Non-goals**: metrics UI. workbench epic (except VONA surface required here).
 re-pin new IWXXM line inside . vendor hand-edits.
- **Source**: product-requirements VONA quality bar + deepen. evolve-decisions . .

### APAC FAQ + codes encode/validate deepen

- **Purpose**: Cross-cutting encode/lint/SCH deltas from APAC FAQs, codes.wmo.int, and
 iwxxm-translation mining: **deepen general TAC conversion/IWXXM validation/TAC validate package/IWXXM validate package** (no new Fn). Full P0+P1+actionable P2.
- **Status**: **Done** (PR).
- **Journeys / tests**: No new UJ. . deepen /005/006/016.
- **API**: No new routes expected. optional convert flag for `translationCentre*` (name in 04).
- **Non-goals**: . PDF remine. FAQ/2019 as equal-weight SoT. `.local/` binaries.
- **Source**: product-requirements general TAC conversion/IWXXM validation/TAC validate package/IWXXM validate package deepen. evolve-decisions . .

### IWXXM domain mine + WMO sample menu

- **Purpose**: Discovery-first domain mine of WMO `IWXXM/` tree , wmo-im org/siblings
 , and IWXXM-US/MDL . wire validate/CI. load official WMO examples from the
 workbench **Examples / sample menu** (****). Deepen general TAC conversion/IWXXM validation/IWXXM version handling/TAC validate package/IWXXM validate package/WMO example parity (+ general TAC conversion).
 no new Fn. Exclude (WIS2).
- **Status**: **Done** (PR). Children, filed for engine work.
- **Components**: `docs/domain/mining/*` + rules/canonicals; `apps/frontend` examples catalog;
 validate/convert fixture surfaces. no new deployable.
- **Journeys / tests**: ****. deepen /. . H4–H5 when FE ships.
- **Catalog policy**: amend: strict `wmoPass` vs WMO reference (loadable). no
 translation-failed happy-path. no US-in-WMO catalog mix.
- **Non-goals**: . big-bang encode engines. hand-edit `vendor/schemas/*`. USWX. PDF/clone commits.
- **Source**: product-requirements deepen. evolve-decisions . amend.
- **Follow-on**: / implements, (+ full dig ❌ US types).

### iwxxm-us REMARKS encode + VA multi-location

- **Purpose**: Dual-lane engine cycle: (A) encode/lint/golden/validate all dig ❌ iwxxm-us
 METAR/SPECI REMARKS types ( + adjacent checklist). (B) 
 `sigmet-multi-location-VA` annex3 golden soft→strict / catalog promote under .
 Deepen general TAC conversion / TAC validate package / IWXXM validation / IWXXM validate package / SIGMET quality bar. no new Fn.
- **Status**: **In progress** .
- **Components**: `packages/tac2iwxxm`, `packages/tac-validate`, `packages/iwxxm-validate`,
 annex3/`iwxxm_us` fixtures. catalog tier for . no new deployable / no new UI surface.
- **Journeys / tests**: ****, ****. deepen /026/034/039. .
 13 when API convert/validate ships.
- **Non-goals**: USWX. vendor hand-edits. US in WMO menu. . . roadmap SWX/VONA/WAFS.
- **Source**: product-requirements deepen. evolve-decisions . dig checklist children.

### Live decode translations + preview clarity

- **Purpose**: live decode: value-aware decode explanations + deterministic plain-language `summary`
 (packages/tac2iwxxm + decode panel). workbench preview: side-by-side IWXXM preview pane, plain-language
 soft-fail copy, `MISSING_TERMINATOR` info-level + "Add `=`" quick fix
 (apps/frontend + packages/tac-validate).
- **Status**: **Done** . ** deepen (live decode)**: extensible glossary registry + optional
 OpenAIP/airport data services names (TC-live decode-003/004. deepen).
- **Component deltas**: see §packages/tac2iwxxm delta, §packages/tac-validate delta,
 §apps/frontend live decode/workbench preview delta.
- **Non-goals**: LLM-generated text. Layer 1–2 / Schematron semantic changes.
- **Source**: [AGENTS.md](../AGENTS.md) live decode/workbench preview. . .
 [evolve-decisions §](decisions/evolve-decisions.md) / §

## Data Flow

### Unified convert/validate pipeline

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| 0. Unit | TAC or WMO AHL bulletin | Detect / accept | Ingest unit |
| 1. Split | Bulletin | `tac2iwxxm` bulletin splitter | One TAC report each |
| 2. TAC lint | TAC report | `tac-validate` (+ optional spans) | Issues or pass |
| 2b. Decode | TAC report | `tac2iwxxm` decode segments | Ordered Code\|Explanation |
| 3. Convert | TAC + product + profile + version | `tac2iwxxm` (hard or soft-preview) | IWXXM XML (+ failed markers) |
| 4. IWXXM validate | IWXXM XML (+ profile) | `iwxxm-validate` (XSD + Schematron) | Pass or fail report (+ optional spans) |
| 5a. API path | Results | Backend JSON | UI / client |
| 5b. ingest worker | Pass | Store (no push sinks in v1) | Published artifact |
| 5c. ingest worker fail | Fail | Quarantine (no publish) | Error record |

### UI / session overlay

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| U1. Edit | TAC text/files + product/profile/version | CodeMirror workbench | Live editor state |
| U1b. Live assist | Editor text (debounced) | Public POST lint / decode (preview) | Spans + decode rows + Failed-TAC cue |
| U2. Auth | Optional login (hybrid operator sessions) | Supabase Auth → JWT via `/auth/*`; convert stays public | JWT only for session APIs |
| U3–U4 | Convert / validate | Unified pipeline stages 0–4 | IWXXM + validation |
| U5. Display | JSON response | Frontend render | Copy/download + Source TAC + console |
| U6. Persist (guest) | Any of 7 products + results | **IndexedDB** upsert (operator workbench / hybrid operator sessions) + loss-of-progress notice | Draft/WIP/Finished/Failed |
| U6c. Persist (logged-in) | Eligible drafts + server CRUD | JWT → `work-sessions*` on DO Postgres (platform independence/hybrid operator sessions) | Long-term history |
| U6b. My METARs | Filter view | `product IN (metar, speci)` (local or server) | work history UX preserved |
| U7. Send link | Dissemination success | Store `kv_upload_key` locally (guest) or on server session | Finished status |

## Monorepo Migration

See [migration-plan.md](ops/migration-plan.md) for step-by-step big-bang procedure.

### Submodule → monorepo mapping

| Current submodule / prior target | Target | Strategy |
|----------------------------------|--------|----------|
| `schemas/iwxxm` | `vendor/schemas/iwxxm` | Snapshot from wmo-im/iwxxm |
| `schemas/iwxxm-codelists` | `vendor/schemas/iwxxm-codelists` | Snapshot |
| `schemas/iwxxm-modelling` | `vendor/schemas/iwxxm-modelling` | Snapshot |
| `data/iwxxm-translation` | `vendor/schemas/iwxxm-translation` | Snapshot |
| — | `vendor/schemas/iwxxm-us` | HTTP snapshot of `nws.weather.gov/schemas/iwxxm-us/3.0` + manifest URL/hash () |
| `GIFTs` / `packages/gifts` | **removed** | Delete on first tac2iwxxm wire-up PR |
| — | `packages/tac2iwxxm` | New MIT package (general TAC conversion) |
| — | `packages/tac-validate` | New package ( amend) |
| — | `packages/iwxxm-validate` | New package , IWXXM validation engine extract ( amend) |
| `frontend` | `apps/frontend` | Full source in monorepo |
| `auth/` (root, not submodule) | `packages/auth` | Library; routes in backend |
| `backend/` | `apps/backend` | Move + wire workspace deps |

### Legacy repositories

Separate GitHub repos (Metartoiwxxmfrontend, GIFTs fork, iwxxm forks) will be **archived read-only** after stable production deploy (REQ-019). Monorepo is the sole active development target. External GIFTs upstream is no longer an in-repo sync target (REQ-014 deprecated).

## Constraints & Assumptions

### Hard Constraints

- iwxxm / iwxxm-* (and iwxxm-us) content is authoritative from upstream. read-only in vendor/.
- Single git clone must be sufficient for local dev (`git clone`, no `--recurse-submodules`).
- Render / DOKS: deploy **three** workloads: API + static frontend + ingest worker worker (
 **platform independence** moves primary hosting to DOKS. Render retired after soak).
- No FastAPI/Supabase **product-DB** imports inside `packages/tac2iwxxm`, `packages/tac-validate`,
 or `packages/iwxxm-validate`. Auth/JWT verify may live only in `packages/auth` + backend.
- After general TAC conversion cutover PR: no `packages/gifts` in the tree. API must not import gifts.
- Schematron applies to **IWXXM only**. TAC quality uses `tac-validate`.
- operator workbench is **in scope**. ingest worker worker remains in tree . **platform independence/hybrid operator sessions** amend data/auth/host.
- PyO3 native extension + benches hard-pass before general TAC conversion cutover .
- Product Postgres is **DigitalOcean**. Supabase is **Auth-only** (no product PostgREST).

### Assumptions

- wmo-im continues publishing tagged releases on GitHub.
- NOAA/MDL continues to publish IWXXM-US schemas suitable for vendor pinning.
- Convert/lint/validate/disseminate stay public. JWT only for work-session APIs (public operator app Amended).
- ingest worker worker uses `DATABASE_URL` (DO), not Supabase service-role DB writers (platform independence).
- `DISABLE_AUTH` dual path remains **retired**. no local/CI JWT bypass that weakens abuse controls.

## Security & Privacy

- **Public convert API** (public operator app Amended): no JWT on convert/lint/validate/disseminate. abuse controls.
- **Optional Auth** (hybrid operator sessions): Supabase Auth JWT for `/auth/*` + `/api/v1/work-sessions*`. disclose
 Auth cookies in privacy preference center. guest IndexedDB gated by privacy prefs where classified non-necessary.
- **Admin API / `is_admin` product surface removed** (operator workbench).
- CORS from `config.*.api.corsOrigins` on backend.
- Secrets: Supabase Auth keys. DO `DATABASE_URL` + DOKS secrets. dissemination allowlist.
 ingest worker poller URL. **No** Supabase service-role for product data plane.
- Dissemination destination credentials remain **memory-only** (029).
- Legacy Supabase product rows: **one-time migrate** into DO Postgres this cycle. then no runtime
 Supabase DB dependency.

## Performance Characteristics

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Single METAR/SPECI Annex-3 conversion | < 2s | Typical (unchanged) |
| Unified pipeline (lint + convert + Schematron) | TBD | Target &lt;5–15s informs ingest worker; measure in 04 |
| Batch file upload (10 files) | < 10s | Depends on size |
| SIGMET / AIRMET / VAA / TCA / US-profile | TBD | May exceed METAR until measured (04) |
| Vendor sync PR | Minutes | CI job; not user-facing |
| Live lint/decode (debounced) | &lt; 500ms typical target | Abort in-flight; measure in 04 |
| Soft-preview convert | TBD | May exceed hard convert; UI must cancel |
| Library lint→convert→XSD+SCH | Beat current lxml baseline | Soft benches in build; hard-fail at PyPI publish (validation performance/IWXXM validate package) |
| High-churn HTTP DTO (msgspec) | ≤ prior pydantic map path | Hard-fail at publish/cutover |

## Known Limitations

- Big-bang migration required coordinated downtime or feature freeze during merge PR (historical).
- **Hard cutover**: first tac2iwxxm wire-up PR deletes gifts. production METAR path depends on
 tac2iwxxm immediately (gate with M-parity / goldens).
- US AIRMET/SIGMET fixture depth may lag METAR/TAF.
- PyO3 is **required before cutover** . pure Python may exist during GIFTs package–auth in API only.
- Accuracy metrics are library/CI only, not exposed on convert API responses in v1.
- Scheduled vendor PRs require review before production pins update.
- work history not extended as a permanent parallel store. **IndexedDB** unified sessions (R2″ / operator workbench).
 My METARs remains METAR/SPECI filter. Historical server `tac_work_sessions` (R2′) retired from
 public API.
- VAA/TCA decode may be residual-heavy in v1 (G4).
- Public machine-ingest auth, push sinks, AMHS/SWIM: out of scope (see product-requirements Non-Goals).

## Documentation layout

Standing specs in `docs/` are **project-wide** sources of truth. Bounded work runs in
**pipeline sessions** with ephemeral artifacts under `docs/sessions/SNNN-slug/`.

| Corpus | Location | Examples |
|--------|----------|----------|
| **Project (standing)** | `docs/` root | `spec.md`, `product-requirements.md`, `test-plan.md`, `deploy.md`, `api-contract.md` |
| **Session (ephemeral)** | `docs/sessions/{id}/` | `session-brief.md`, `routing-plan.md`, `reports/qa-report.md`, `reports/e2e-report.md` |
| **Scoped context** | `docs/context/{slug}.md` | Feature/workflow discovery briefs (linked from session brief) |

**Entry:** [skill-routing.md](skill-routing.md): start with **** (recommended) to
open a session, approve a routing plan, then run pipeline stages per plan.

**State:** repo-root `workflow-state.yaml` §`active_session` and §`sessions[]`.

Full convention: [.cursor/skills/sessions-reference.md](../.cursor/skills/sessions-reference.md).

Standing doc updates during a session use **delta commits** on the session branch with a
§Session changelog footer (session id + date).

## References

- docs/guides/ARCHITECTURE.md (pre-migration product architecture)
- [ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md](ARCHIVE/pre-monorepo-deploy/AUTH_MIDDLEWARE_ARCHITECTURE.md) (superseded by auth in API. see )
- docs/decisions/requirements-decisions.md
- , 

### Session changelog

- (2026-07-12): general TAC conversion tac2iwxxm architecture. gifts removal. IWXXM-US. UI product/profile. 
- amend (2026-07-12): `tac-validate` + `iwxxm-validate`. unified pipeline. operator workbench/ingest worker Planned.
 dashed ingest worker worker. context/realtime-tac-ingest.md (archived. see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`. not a design document set design gate)
- 05 (2026-07-12): ingest worker worker in-tree. PyO3 cutover gate. iwxxm-us HTTP 3.0 pin. three Render
 services 
- / (2026-07-13): operator workbench operator UI architecture. BYO + admin removal. decode/spans/
 soft-preview. CodeMirror workbench. **R2′** unified `tac_work_sessions` + work history migrate.
 ingest worker status sync
