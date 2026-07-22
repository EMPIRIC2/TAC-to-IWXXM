# Requirements Decisions Log

> Stage: 01-requirements | Last updated: 2026-07-12

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| REQ-001 | Monorepo direction | Single git; reduce submodule complexity; preserve upstream pull for iwxxm | confirmed |
| REQ-002 | iwxxm-* upstream | Vendored snapshots from wmo-im; no git submodules for schemas | confirmed |
| REQ-003 | GIFTs placement | `packages/gifts` — full source; manual merge from mgoberfield when chosen | confirmed |
| REQ-004 | Auth shape | `packages/auth` library merged into backend; single deployable API | confirmed |
| REQ-005 | Workspace tooling | Makefile + uv workspace + pnpm workspaces | confirmed |
| REQ-006 | Migration approach | Big-bang — one PR removes all submodules | confirmed |
| REQ-007 | Target layout | `apps/{backend,frontend,e2e}` + `packages/{auth,gifts,shared}` + `vendor/schemas/*` | confirmed |
| REQ-008 | Legacy repos | Archive after stable deploy; monorepo sole active dev target | confirmed |
| REQ-009 | Vendor sync trigger | Scheduled GitHub Action opens PR on wmo-im new tags | confirmed |
| REQ-010 | Deploy topology | Two Render services — API (backend+auth) + static frontend | confirmed |
| REQ-011 | Big-bang scope | Structure + auth merge + docs + test reorganization | confirmed |
| REQ-012 | Shared package | `packages/shared` — types + cross-app utils | confirmed |
| REQ-013 | E2E location | `apps/e2e/` dedicated workspace | confirmed |
| REQ-015 | Vendor pinning | `vendor/manifest.json` — repo + tag/SHA per bundle | confirmed |
| REQ-016 | Non-goals | No product feature rewrites during migration | confirmed |
| REQ-014 | GIFTs sync | **Deprecated (S008 / ADR-014)** — `packages/gifts` removed at F6 cutover; was manual merge from mgoberfield | deprecated |
| REQ-017 | Auth route prefix | `/auth/*` at API root after merge | confirmed |
| REQ-018 | Golden regression | TC-M003 normalized canonical XML diff | confirmed |
| REQ-019 | Legacy repo archive | After stable production deploy, not at merge | confirmed |
| REQ-020 | JS workspace | pnpm workspaces (frontend + packages/shared) | confirmed |

## Live E2E delta (2026-06-22)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| LIVE-001 | Scope | All tiers — H3 + H4–H5 + H6 full Playwright UJ-001–003 | confirmed |
| LIVE-002 | CI policy | Manual/local only — Makefile targets; no GitHub Actions live job | confirmed |
| LIVE-003 | Credentials | Local `.env` — `ADMIN_EMAIL` / `ADMIN_PASSWORD`; JWT at runtime via login | confirmed |
| LIVE-004 | Playwright scope | Full UJ-001–003 against Render (`DISABLE_AUTH=false`) | confirmed |
| LIVE-005 | Env naming | Canonical `LIVE_*` prefix; migrate away from `STAGING_*` / `E2E_*` | confirmed |
| LIVE-006 | URLs | API: `https://metar-to-iwxxm-api.onrender.com`; Frontend: `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | confirmed |
| LIVE-007 | Makefile | Individual targets + `test-live` umbrella | confirmed |
| LIVE-008 | Cold-start | Retry with backoff — 3 attempts, 30s wait | confirmed |
| LIVE-009 | Rate limits | Exponential backoff on HTTP 429 | confirmed |
| LIVE-010 | H3 coverage | Full suite — health, convert, validate, auth `/me` | confirmed |
| LIVE-011 | Stale tests | Fix/migrate `tests/test_playwright_e2e.py` to merged API | confirmed |
| LIVE-012 | Acceptance | Manual signoff before release — not a PR merge gate | confirmed |
| LIVE-013 | Prerequisite | E2E-001 schema path fix must land before live validate passes | confirmed |

## S003 — Supabase keys, config split, env sync (2026-06-23)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| S003-R1 | Key naming | `SUPABASE_PUBLISHABLE_KEY` + `SUPABASE_SECRET_KEY` canonical; deprecate `ANON_KEY` / `SERVICE_ROLE_KEY` with shim | confirmed |
| S003-R2 | Frontend config | Runtime `/config.json` fetch at bootstrap; `config/prod.json` + publishable key inject at deploy | confirmed |
| S003-R3 | METAR project | `ktvxijislbtgqapllmuk`; migrations 003–004 **not yet applied** in production | confirmed |
| S003-R4 | Local ports | Standardize **18000** (frontend) / **18001** (API) everywhere | confirmed |
| S003-R5 | Secret key scope | `SUPABASE_SECRET_KEY` only for Auth Admin API (`create_admin_user.py`); admin routes use user JWT + RLS | confirmed |
| S003-R6 | Env sync | `env-contract.md` + `env-sync-runbook.md` + `make env-check`; align Render, Supabase, local, GitHub | confirmed |
| S003-R7 | Advisor scope | METAR tables only; CogniChem org projects out of scope | confirmed |
| S003-R8 | Auth dashboard | Enable leaked-password protection (HaveIBeenPwned) on METAR project | confirmed |
| S003-R9 | Config envs | `prod` + `local` only; `stage`/`dev` deferred | confirmed |

## F5 — User METAR work history (2026-06-23)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| F5-R1 | Status lifecycle | Draft → WIP → Finished; separate **Failed** for convert/partial errors | confirmed |
| F5-R2 | Failed recovery | Failed stays until user edits input and re-converts | confirmed |
| F5-R3 | Multi-session | Multiple Draft/Failed OK; max one WIP; new Draft allowed while WIP open | confirmed |
| F5-R4 | Login resume | Resume most recent non-Finished, non-deleted session on login | confirmed |
| F5-R5 | Auth | Persistence requires login (RLS per user); guests may convert without save | confirmed |
| F5-R6 | Auto-save | ~3s debounce after typing stops | confirmed |
| F5-R7 | File payload | Inline JSONB (name + TAC content) | confirmed |
| F5-R8 | Retention | Draft auto-purge 30 days via Supabase pg_cron | confirmed |
| F5-R9 | UI | Converter sidebar + My METARs page; filters: status + date | confirmed |
| F5-R10 | API | Backend REST only (no direct browser Postgres) | confirmed |
| F5-R11 | Delete | Soft-delete; user trash 30-day restore then hard-delete | confirmed |
| F5-R12 | Finished rule | Finished only after successful DB send; convert-only stays WIP | confirmed |
| F5-R13 | KV link | Store `kv_upload_key` on Finished session | confirmed |
| F5-R14 | Admin | Existing admin role — read-only browse all users' sessions | confirmed |
| F5-R15 | Title | Auto ICAO + timestamp; user can rename | confirmed |
| F5-R16 | Delivery | Merged S004/EV-004 with #555 UX + S003 Supabase (was S005 after S004) | confirmed 2026-06-23 |
| F5-R18 | Results sync | Re-convert replaces UI results and overwrites active session row | confirmed 2026-06-23 |
| F5-R19 | Sidebar count | 5 most recent sessions on converter | confirmed 2026-06-23 |
| F5-R20 | S003 dependency | Supabase key/config fixes included in same cycle as F5 | confirmed 2026-06-23 |
| F5-R17 | Failed slot | Failed counts like Draft for multi-session limits | confirmed |
| F5-R21 | History model | **Current state only** — one row per session (no append-only audit trail in v1) | confirmed 2026-06-23 interview |
| F5-R22 | Guest users | Can convert in-browser without login; **no persistence** until logged in | confirmed 2026-06-23 interview |
| F5-R23 | Send failure | Stay **WIP** — user can retry send; do not move to Failed | confirmed 2026-06-23 interview |
| F5-R24 | Finished reopen | **Read-only** view of TAC, IWXXM, errors, KV reference — no edit in v1 | confirmed 2026-06-23 interview |
| F5-R25 | Multi-device | Last write wins on auto-save (no conflict UI in v1) | confirmed 2026-06-23 interview |
| F5-R26 | New session | Explicit **New METAR** button creates a new Draft; prior sessions remain saved | confirmed 2026-06-23 interview |
| F5-R27 | Sidebar switch | Load selected session into converter; existing WIP row unchanged in DB | confirmed 2026-06-23 interview |
| F5-R28 | Login resume | Auto-resume most recent non-Finished, non-deleted session (reconfirmed) | confirmed 2026-06-23 interview |
| F5-R29 | Error log | In-app collapsible panel (#555) **and** persist `errors`/`issues` on session row | confirmed 2026-06-23 interview |
| F5-R30 | Retention | Draft auto-purge 30d; soft-delete trash 30d restore (reconfirmed) | confirmed 2026-06-23 interview |
| F5-R31 | Admin UI | Separate **admin page** for read-only browse of all users' sessions | confirmed 2026-06-23 interview |
| F5-R32 | Storage limits | No explicit cap in v1 — reasonable METAR batch sizes assumed | confirmed 2026-06-23 interview |
| F5-R33 | Guest login | Auto-create new **Draft** from in-browser converter state on login | confirmed 2026-06-23 audit (02-verify-plan) |
| F5-R34 | WIP edit | **WIP** stays WIP when user edits input before re-convert (IWXXM may be stale) | confirmed 2026-06-23 audit (02-verify-plan) |
| F5-R35 | Finished UI | Finished read-only — Convert/Convert&Send disabled; **New METAR** required | confirmed 2026-06-23 audit (02-verify-plan) |
| F5-R36 | Wording | F5 purpose uses "work history / session state" — not "audit trail" | confirmed 2026-06-23 audit (02-verify-plan) |

## F1 — #555 converter UX (2026-06-23 interview)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| F1-R555-1 | Results panel | **Replace** result cards on each **successful** convert only; failed runs keep prior results | confirmed 2026-06-23 interview |
| F1-R555-2 | Error log | Collapsible in-app panel from API `errors`/`issues`; also persisted on F5 session row | confirmed 2026-06-23 interview |

1. ~~Exact auth route prefix after merge~~ — resolved: `/auth/*` (REQ-017)
2. ~~pnpm vs npm~~ — resolved: pnpm (REQ-020)
3. ~~Golden file strategy for TC-M003~~ — resolved: normalized XML (REQ-018)

## S008 / F6 — General TAC→IWXXM (2026-07-12)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| F6-R1 | Feature id | **F6** — General TAC→IWXXM (`tac2iwxxm`); one Fn with product subsections | confirmed |
| F6-R2 | Products v1 | AIRMET, METAR, SIGMET, SPECI, TAF, **VAA**, **TCA** (7) | confirmed |
| F6-R3 | Profiles | Default `annex3`; opt-in `iwxxm_us` | confirmed |
| F6-R4 | API | Extend `POST /api/v1/convert` with `product` + `profile` | confirmed |
| F6-R5 | UI | Product + profile (+ version) pickers in v1; H4–H5 required | confirmed |
| F6-R6 | License | **MIT** for `packages/tac2iwxxm` | confirmed |
| F6-R7 | Native | Pure Python v0; optional **Rust/PyO3** (not Cython) — ADR-014 | confirmed |
| F6-R8 | Cutover | Hard cutover: first tac2iwxxm wire-up PR **deletes `packages/gifts`** | confirmed |
| F6-R9 | F1 | Status **Superseded by F6** | confirmed |
| F6-R10 | REQ-014 | **Deprecated** (ADR-004 deprecated; M3 deprecated) | confirmed |
| F6-R11 | Metrics | Library/CI only — no convert-response metrics fields in v1 | confirmed |
| F6-R12 | F5 | Do not extend to non-METAR products in F6 v1 | confirmed |
| F6-R13 | Phases | F6.a–F6.f (METAR/SPECI → US → TAF → SIGMET/AIRMET → API/UI → VAA/TCA) | confirmed |
| F6-R14 | Params | UI may auto-detect; **API requires `product`** (F6-R25); profile default annex3 | confirmed |
| F6-R15 | UJ structure | Extend UJ-001; add UJ-005/006/007 + error UJ-008–010; UJ-DEV-003→003b | confirmed |
| F6-R16 | T3 coverage | All 7 products annex3 via UI+API; US profile METAR/SPECI/TAF where applicable | confirmed |
| F6-R17 | Product conflict | Explicit UI product wins; warn if ≠ auto-detect | confirmed |
| F6-R18 | Batch files | Per-file product auto-detect; aggregate errors | confirmed |
| F6-R19 | Test scope | F6 in scope; metrics lib/CI only; H6=UJ-001–007 | confirmed |
| F6-R20 | Metrics CI | M-parse/xsd/sch required; archive gifts goldens post-delete | confirmed |
| F6-R21 | Cutover gate | TC-F6-020/021 METAR/SPECI + UJ-001 before gifts-delete merge | confirmed |
| F6-R22 | CI matrix | gifts → tac2iwxxm same cutover PR; Rust bench deferred to 04 | confirmed |
| F6-R23 | Deps | tac2iwxxm MIT + lxml; IR TBD 04; optional PyO3; iwxxm-us vendor; gifts section marked removed | confirmed |
| F6-R24 | API health | `tac2iwxxm_available`; remove `gifts_available` | confirmed |
| F6-R25 | API convert | `product` **required**; `profile` optional default annex3; multipart only | confirmed |
| F6-R26 | F5 params | Store product/profile in conversion_params; UI copies to multipart on submit | confirmed |
| F6-R27 | API errors | codes unknown_product / invalid_profile / missing_iwxxm_us / parse_failed; 400/422/5xx | confirmed |
| F6-R28 | Config | No new config/env keys; no cutover flag; US via request profile | confirmed |

## S008 realtime / package amend (2026-07-12)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| RT-R1 | Session | Amend S008 (reopen 00+01); realtime = ingest pipeline | confirmed |
| RT-R2 | Schematron | IWXXM only; TAC via separate lint package | confirmed |
| RT-R3 | Packages | `packages/iwxxm-validate` + `packages/tac-validate` | confirmed |
| RT-R4 | F2 | Evolves to thin wrapper over `iwxxm-validate` | confirmed |
| RT-R5 | F6 | Bulletin split acceptance; phase **F6.bulletin** with/before F6.a | confirmed |
| RT-R6 | F7 | Planned multi-product operator entry; F5 unchanged; no build this cycle | confirmed |
| RT-R7 | F8 | Planned near-RT ingest; store+push; quarantine; worker later; no build this cycle | confirmed |
| RT-R8 | This cycle | Package APIs + **API thin wrappers** for validate packages | confirmed |
| RT-R9 | Non-goals | Auth/sinks/AMHS postponed; F6 “no Render deployable” left unchanged (worker under F8) | confirmed |
| RT-R10 | Manifest | Feature List, Spec, Journeys, Test Plan, Deps, API light, ADRs; skip Config+Deploy | confirmed |
| RT-R11 | Spec | Unified pipeline; dashed F8 worker; SoC on both validate packages | confirmed |
| RT-R12 | Journeys | UJ-011/012 T2; UJ-013/014 Planned stubs; UJ-DEV-004; update UJ-002/005–007 | confirmed |
| RT-R13 | Test plan | TC-F6-030–033; M-sch via iwxxm-validate; **H7** live bulletin gate | confirmed |
| RT-R14 | Deps | Both packages MIT; tac-validate may use pydantic/msgspec in 04; iwxxm-validate uses lxml | confirmed |
| RT-R15 | API | validate wraps iwxxm-validate; `POST /lint-tac`; `POST /convert-bulletin`; convert single-report | confirmed |
| RT-R16 | ADR-015 | Validate packages + bulletin API + deferred F7/F8 + H7 | accepted |

## EV-009 / F9+F10 — Live decode translations + preview UX (2026-07-16)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-009/F9-R1 | Summary style | One flowing paragraph from decoded values (deterministic; no LLM) | confirmed |
| EV-009/F9-R2 | Residuals | Summary appends "Not decoded: …" naming residual spans | confirmed |
| EV-009/F9-R3 | Sparse products | Best-effort summary + "partial decode" wording (no threshold cutoff) | confirmed |
| EV-009/F9-R4 | Products | Value-aware decode for all 7 (METAR/SPECI/TAF rich; others best-effort) | confirmed |
| EV-009/F9-R5 | Engine | Backend `decode_tac` builds `summary`; additive decode-tac field | ADR-025 |
| EV-009/F10-R1 | Pane content | Pretty-printed IWXXM + status badge + failed-span count linked to editor | confirmed |
| EV-009/F10-R2 | Responsive | Side-by-side ≥ lg; stacked below editor < lg | confirmed |
| EV-009/F10-R3 | Quick fix | "Add '='" on console line + editor affordance on hint span | ADR-025 |
| EV-009/F10-R4 | Severity | `info` severity added; MISSING_TERMINATOR error→info; `ok` keyed to error only | ADR-025 |
| EV-009/F10-R5 | Soft-fail copy | LAYER12_SOFT_FAIL presented as plain-language status, code secondary | ADR-025 |

## EV-010 / F11–F14 — Package publish + validation stack (2026-07-18)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-010/F11-R1 | HTTP msgspec | Response encode + optional post-Form Structs; multipart Form intake unchanged; auth/sessions pydantic | ADR-026 |
| EV-010/F11-R2 | OpenAPI | Keep pydantic for OpenAPI aliases/export; no dual runtime validation | ADR-026 |
| EV-010/F11-R3 | Codegen | Production types from published XSD; UML provenance; TAC out of scope | confirmed |
| EV-010/F11-R4 | Perf gates | Soft benches in build; hard-fail at publish (lib path + HTTP msgspec) | confirmed |
| EV-010/F11-R5 | Must-ship | Keep 11B; 04 milestones; AskQuestion only if blocked (02 S1.M1=A) | confirmed |
| EV-010/F12-R1 | Domain depth | All 7 products; METAR/SPECI/TAF full; others template+gates; cite-only paywall | confirmed |
| EV-010/F12-R2 | PyPI | `tac-validate` `0.1.0`; tag `tac-validate-v0.1.0` | confirmed |
| EV-010/F13-R1 | Rust Schematron | Native Rust Schematron/SVRL; parity vs lxml; schemas bundled in wheel | confirmed |
| EV-010/F13-R2 | PyPI | `iwxxm-validate` `0.1.0`; tag `iwxxm-validate-v0.1.0` | confirmed |
| EV-010/F14-R1 | Extras | `tac2iwxxm[validate]` → tac-validate + iwxxm-validate | confirmed |
| EV-010/F14-R2 | Publish CI | OIDC trusted publishing per package version tag | confirmed |
| EV-010/R-deploy | Render | Full 12–13 redeploy (msgspec HTTP); PyPI publish in same cycle | confirmed |
| EV-010/R-config | Config/deploy docs | Minimal PyPI OIDC notes in config-spec + deploy (02 S8.M1=A) | confirmed |

## EV-014 / F16–F19 — Dissemination epic (2026-07-21)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-014/F16-R1 | Creds | One-shot destination URI/params; API memory-only; no saved profiles | confirmed |
| EV-014/F16-R2 | Auth | Supabase Auth stays deploy BYO; no paste of Supabase auth keys | ADR-021 amend |
| EV-014/F16-R3 | UI | Dissemination drawer; URI-only DB fields; preflight; block Send until green | confirmed |
| EV-014/F16-R4 | Schema | DDL / create-if-missing vs versioned writer contract | confirmed |
| EV-014/F16-R5 | Entry | Convert-then-send **and** drag-drop IWXXM/TAC | confirmed |
| EV-014/F16-R6 | Engines | Postgres, MySQL/MariaDB, SQL Server, SQLite | confirmed |
| EV-014/F16-R7 | SSRF | Full baseline + required `DISSEMINATION_EGRESS_ALLOWLIST` | ADR-029 |
| EV-014/F16-R8 | F5 | Keep history in Supabase; never store destination secrets | confirmed |
| EV-014/F17-R1 | WIS2 test | Staging wis2box on Render/Docker | confirmed |
| EV-014/F17-R2 | WIS2 live | User BYOC node/creds; required before cycle close | confirmed |
| EV-014/F18-R1 | EDIS | Real RTH Washington; BYOC SMTP/gateway in drawer | confirmed |
| EV-014/F19-R1 | Adapters | AMHS / SWIM / AFS in same drawer (non-goals overturn) | confirmed |
| EV-014/R-close | Gate | Staging OK to merge; live BYOC Postgres+WIS2+EDIS before close | confirmed |
| EV-014/R-route | Routing | Full 00→16→01…13 | confirmed |
| EV-014/S-M2 | Close | F19 staging required; F19 live optional + waive (Q28=A) | confirmed |
| EV-014/S-M4 | ADR | ADR-029 Accepted (02-verify-plan) | confirmed |

## EV-015 / F20 — TAF + SPECI quality (2026-07-22)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-015/F20-R1 | Scope | Full #735 TAF + full #734 SPECI quality bars | confirmed |
| EV-015/F20-R2 | Fn | New F20 + deepen F6.b/F6.c + F12; ADR-028 reuse | confirmed |
| EV-015/F20-R3 | Routing | Lean+build (01/02/04/07–11/13; skip 03/05/06/12) | confirmed |
| EV-015/F20-R4 | Depth | Guidance audit + fixtures + goldens + matrix themes | confirmed |
| EV-015/F20-R5 | OOS | Sibling product tickets; PyPI; F16–F19; F7 Planned | confirmed |
| EV-015/F20-R6 | Smoke | H1–H3 if API; H4–H5 workbench taf/speci when FE | confirmed |
| EV-015/F20-R7 | Journeys | UJ-031; TC-F20-001..006 | confirmed |
| EV-015/F20-R8 | API | Full endpoint review; no new routes; wire unchanged | confirmed |
| EV-015/E15-12 | Milestones | TAF lint → TAF goldens → SPECI → C1 → smoke | confirmed |
| EV-015/E15-13 | Research | Full mining pass + session research catalog | confirmed |
| EV-015/E15-14 | FE | Extend catalog panel TAF tag filters/copy | confirmed |
| EV-015/E15-15 | Deps | AskQuestion per new dep (prefer none) | confirmed |
| EV-015/E15-16 | CI | Existing pytest + ci.yml only | confirmed |
| EV-015/E15-17 | Mining | Full dig TAF+SPECI only | confirmed |
| EV-015/E15-18 | Deploy | API+FE; H1–H3 + H4–H5 required | confirmed |
| EV-015/E15-19 | Plan | Approve M0–M5 execution plan | confirmed |
| EV-015/manifest | Docs | Spec, journeys, test-plan, coverage matrix, API contract | confirmed |
