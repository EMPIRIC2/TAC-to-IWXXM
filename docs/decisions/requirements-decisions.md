# Requirements Decisions Log

> Stage: 01-requirements | Last updated: 2026-08-11 (S064 / EV-055)

## EV-055 / S064 — Quality metrics normalize + 2025-2 validate (#982 / #980 / #979) (`D-S064-01-ac=1`)

| Topic | Decision | Notes | Status |
|-------|----------|-------|--------|
| EV-055 / Fn | Deepen F7.q + F2/F13 | F4 only if messaging; no new top-level Fn (`D-S064-engine=1`) | confirmed |
| EV-055 / normalize | Both sides; match_status = normalized equality | `D-S064-normalize=1` | confirmed |
| EV-055 / regen | Regenerate corpus_metrics | Stored match semantics match AC2 (`D-S064-regen=1`) | confirmed |
| EV-055 / Schematron | **Hard enable** for 2025-2 | Overrides soft prefer (`D-S064-sch-hard=1`) | confirmed |
| EV-055 / XSD import | **Hard fix** for 2025-2 | Overrides optional (`D-S064-xsd-hard=1`) | confirmed |
| EV-055 / algorithm | **W3C C14N** always | `D-S064-c14n=1` | confirmed |
| EV-055 / volatile | **C14N after volatile-attr strip** | `D-S064-c14n-volatile=1` / ADR-035 | confirmed |
| EV-055 / panes | Normalized default + override to raw | `D-S064-gateA-M2=override` | confirmed |
| EV-055 / helper | Shared generator + FE | `D-S064-gateA-M1=1` | confirmed |
| EV-055 / Gate A | **PASS** | `D-S064-gateA=1` → 04 | confirmed |
| EV-055 / journey | Deepen **UJ-056** only | No UJ-057 (`D-S064-uj=1`) | confirmed |
| EV-055 / AC | AC1–AC7 (amended Gate A) | See evolve-decisions §EV-055 | confirmed |
| EV-055 / docs | Delta manifest | feature-list + journeys + test-plan + api-contract + decisions | confirmed |
| EV-055 / UI preview | Declined | Docs/repo only (`D-S064-ui-preview=2`); re-offer at 11 | confirmed |
| EV-055 / route | Standard | PR → stage; skip 03/06 | confirmed |

[Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13] [Corpus: api]
[Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-055]

## EV-054 / S063 — Quality metrics tab (#836 / F7.q) (`D-S063-01-ac=1`)

| Topic | Decision | Notes | Status |
|-------|----------|-------|--------|
| EV-054 / Fn | Deepen F7 + **F7.q** | No F34 (`D-S063-fn=1`) | confirmed |
| EV-054 / shell | Separate primary app-shell tab | Peer to Convert / History — not FileConverter panel (`D-S063-shell-tab=1`) | confirmed |
| EV-054 / compute | Precomputed metrics JSON | Served via public `GET /api/v1/quality-metrics*` (`D-S063-compute=1` + Gate A=2) | amended |
| EV-054 / Gate A | PASS + metrics HTTP API | Re-open api-contract; re-enable 05 (`D-S063-gateA=2`) | confirmed |
| EV-054 / diff | Unified XML diff in v1 | Plus inspectable raw panes (`D-S063-diff=2`) | confirmed |
| EV-054 / journey | **UJ-056** | TC-EV054-001..007; H4–H5 required | confirmed |
| EV-054 / AC | AC1–AC7 | See evolve-decisions §EV-054 | confirmed |
| EV-054 / docs | Delta manifest | feature-list + journeys + test-plan + decisions; skip API/config unless 04 | confirmed |
| EV-054 / UI preview | Declined at open | `D-S063-ui-preview=2`; re-offer at 11 | confirmed |
| EV-054 / route | Standard | include 10/12/13; skip 03/05*/06 | confirmed |

[Corpus: product §F7] [Corpus: journeys] [Corpus: tests] [Corpus: adr/ADR-032]
[Corpus: decisions §EV-054]

## EV-053 / S062 — Vitest branches ≥95 FileConverter (#968) (`D-S062-01-ac=1`)

| Topic | Decision | Notes | Status |
|-------|----------|-------|--------|
| EV-053 / strategy | Re-include FileConverter | Fill branch+line tests until aggregate ≥95 (`D-S062-fc-strategy=1`) | confirmed |
| EV-053 / AC5 | FileConverter ≥95% branches | Stricter than aggregate-only (`D-S062-01-ac` Q3=2) | confirmed |
| EV-053 / docs | Delta manifest | feature-list + test-plan + decisions; inventory resolve in 07 | confirmed |
| EV-053 / UI | Preview | Declined (`D-S062-ui-preview=2`); CI/Vitest only | confirmed |
| EV-053 / route | Standard | skip 03/05/06/10/12/13 | confirmed |
| EV-053 / Fn | Deepen | F29 + M5 only; no new Fn | confirmed |

[Corpus: product §F29] [Corpus: product §M5] [Corpus: tests] [Corpus: adr/ADR-007]
[Corpus: decisions §EV-053]

## EV-052 / S061 — CI polish + quality PR stats + Sentry/Redis/Orval (`D-S061-01-ac=1`)

| Topic | Decision | Notes | Status |
|-------|----------|-------|--------|
| EV-052 / F29+F6 | Quality sticky PR comment #2 | match/soft-diff/fail/skip × product × profile; separate from EV-036 coverage | confirmed |
| EV-052 / tests | #950 ≥95% gates | Restore ADR-007 floors; fill tests; inventory required | confirmed |
| EV-052 / F30 | Sentry Developer free | API+FE+worker; DSN optional; no new K8s service | confirmed |
| EV-052 / F21 | Upstash Redis free | Shared slowapi store; no DOKS Redis Deployment (`D-S061-redis=1`) | confirmed |
| EV-052 / M5 | Orval or openapi-typescript | Pick in 04; typed FE client from OpenAPI | confirmed |
| EV-052 / UI | 01 preview | N/A (`D-S061-ui-preview=3`) | confirmed |
| EV-052 / route | Standard | skip 03/06/10/12/13 | confirmed |

## EV-050 / S059 — codes.wmo.int Validated (#959) (`D-S059-01-ac=4a` + profile amend)

| Prefix | Topic | Decision | Status |
|--------|-------|----------|--------|
| EV-050 / route | Standard | `00→16→01→02→04→05→07→08→09→11`; skip 03/06/10/12/13 (`D-S059-route=1`) | confirmed |
| EV-050 / families | Membership v1 | Weather + recent + cloud amount/type + SIGMET/AIRMET phenomena + nilReason where lint touches (`D-S059-families=1a`) | confirmed |
| EV-050 / fixtures | Expansion | Aggressive: RE*, AIRMET `_`, SpaceWxPhenomena, TCU this cycle (`D-S059-fixtures=2c`) | confirmed |
| EV-050 / #882 | Live refresh | Design-only compose note; no job this cycle (`D-S059-882=3a`) | confirmed |
| EV-050 / Fn | Deepen | F6/F12/F15/F20/F23/F24/F28 (no new Fn); UI N/A | amended |
| EV-050 / profiles | annex3 vs iwxxm_us | All F6 products; `iwxxm_us` N/A where unsupported; classify shared / intentional L5 / true error; fix true errors (`D-S059-profiles=1b`) | confirmed |
| EV-050 / UI | Preview | N/A — no browser UI | confirmed |
| EV-050 / Validated | #889 AC5 | Satisfied via offline harvest + membership CI (`D-S059-validated=1`); supersedes Lean `D-S055-validated=1` for Validated | confirmed |

[Corpus: product §F6/F12/F15/F20/F23/F24/F28] [Corpus: tests] [Corpus: tech-spec]
[Corpus: decisions]

## EV-048 / S057 — Strip internal doc refs (#951) (`D-S057-01-ac=1`)

| Prefix | Topic | Decision | Status |
|--------|-------|----------|--------|
| EV-048 / F7 | Operator UI copy | No Corpus/ADR/EV/S0/`docs/` cites in operator-visible strings | confirmed |
| EV-048 / F21 | Public OpenAPI + errors | Operator language only in descriptions/`detail` | confirmed |
| EV-048 / guard | Patterns | `\[Corpus:`, `docs/sessions/`, `docs/feature-list`, `ADR-\d+`, `EV-\d+`, `S0\d+` (`D-S057-guard-s0=1`) + `TC-*`, `E##-##`, `#NNN` (`D-S057-04-guard-ext=1`) | confirmed |
| EV-048 / UJ | UJ-055 | New journey; T0/T2; T3 if UI audit finds hits | confirmed |
| EV-048 / UI | 01 preview | Non-deployed local Vite (`D-S057-ui-preview=1`) | confirmed |
| EV-048 / route | Standard | 04/05/07–11 required; 12/13 waived | confirmed |

## EV-047 / S056 — M0 husky + converter perf + operator docs (`D-S056-01-ac=1`)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-047 / M5 | Husky shape A | pre-commit lint/format; pre-push fast units; reverse EV-036 day-to-day weight | confirmed |
| EV-047 / F6 | Converter perf gate | convert-only p95; YAML baselines; >20% or ceiling; CI required; not husky | confirmed |
| EV-047 / F7 | Operator docs | `docs/guides/operator-one-pager.md` + `operator-handbook.md`; README + Help | confirmed |
| EV-047 / route | 10-e2e | Re-enabled for UJ-054 Help; 12/13 waived unless 11 requires deploy | confirmed |
| EV-047 / UI | 01 preview | Declined non-deployed UI (`D-S056-ui-preview=2`) | confirmed |

[Corpus: product §M5] [Corpus: product §F6] [Corpus: product §F7] [Corpus: tests]
[Corpus: journeys]

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

## EV-039 / F16 — Live local SQL ingest e2e + teardown (2026-08-06)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-039/F16-R1 | Scope | Deepen F16 only — no new Fn | confirmed |
| EV-039/F16-R2 | Engines | All four: Postgres + MySQL + SQL Server + SQLite | confirmed |
| EV-039/F16-R3 | Harness | Reuse `docker-compose.mock-byoc.yml` + Playwright live (no route mocks) | confirmed |
| EV-039/F16-R4 | Teardown | Integration + e2e + local Compose — audit and fix gaps | confirmed |
| EV-039/F16-R5 | UI preview | Declined this cycle | confirmed |
| EV-039/F16-R6 | Manifest | feature-list, journeys, test-plan, tech-spec; skip api-contract/spec/new ADR | confirmed |
| EV-039/F16-R7 | ACs | AC1–AC7 approved (`D-S047-ac`=1) | confirmed |
| EV-039/F16-R8 | CI | Live suite documented via make; may be opt-in if SQL Server heavy | confirmed |
| EV-039/F16-R9 | OOS | New vendors; live WIS2/EDIS/F19; prod SQL containers | confirmed |

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

## EV-016 / F7.g — Workbench golden examples (2026-07-22)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-016/F7-R1 | Scope | Frontend-only goldens per #780; deepen F7 | confirmed |
| EV-016/F7-R2 | Journey | UJ-032 + TC-F7-008 | confirmed |
| EV-016/F7-R3 | Status | F7 stays Planned; slice F7.g | confirmed |
| EV-016/F7-R4 | Optional | Happy-path IWXXM only; no soft-fail / file-queue v1 | confirmed |
| EV-016/F7-R5 | Thin fixtures | In-repo only; allow 1 + document gap; no invented TAC | confirmed |
| EV-016/F7-R6 | Docs | feature-list + user-journeys + test-plan + light spec | confirmed |
| EV-016/F7-R7 | Non-goals | No api-contract / config / deploy env changes | confirmed |

## EV-017 / F21+F22 — Public app + privacy (#783) (2026-07-27)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-017/F21-R1 | Auth | Public operator app; no login/JWT for convert/validate/lint/decode/preview/dissemination | confirmed |
| EV-017/F21-R2 | History | IndexedDB F5/F7; export/import; no cross-device sync v1 | confirmed |
| EV-017/F21-R3 | Legacy DB | No public API to old rows; ~30-day archive then delete | confirmed |
| EV-017/F21-R4 | Abuse | Baseline rate/size/timeouts this cycle; keep SSRF/allowlist | confirmed |
| EV-017/F21-R5 | Sequence | Local history before auth teardown | confirmed |
| EV-017/F21-R6 | F8 | Service-role remains private / out of public router | confirmed |
| EV-017/F22-R1 | Tracking | Solution A — no non-essential analytics/marketing | confirmed |
| EV-017/F22-R2 | UI | Footer Privacy settings + first-visit notice + GPC; no CMP | confirmed |
| EV-017/F22-R3 | Schema | Versioned PrivacyPreferences; necessary always on; others default false | confirmed |
| EV-017/M4-R1 | M4 | Deprecated for operator Auth; fate of packages/auth in ADR | confirmed |
| EV-017/UJ-R1 | Journeys | UJ-003 superseded; UJ-033 added; UJ-001/004/018 public+IndexedDB | confirmed |
| EV-017/API-R1 | Contract | `/auth/*` + work-sessions HTTP removed; convert public | confirmed |
| EV-017/manifest | Docs | feature-list, spec, journeys, test-plan, api-contract | confirmed |
| EV-017/UI-preview | Preview | Deferred to 11-verify-impl | confirmed |

## EV-019 / F23 — SIGMET + VA SIGMET quality (2026-07-29)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-019/F23-R1 | Scope | Full #733 general + #739 VA quality bars; #738 TC OOS | confirmed |
| EV-019/F23-R2 | Fn | New F23 + deepen F6.d/F12; ADR-028 reuse | confirmed |
| EV-019/F23-R3 | Routing | Lean+build (01/02/04/07/08/10/13; skip 03/05/06/09/11/12) | confirmed |
| EV-019/F23-R4 | Depth | Guidance audit + fixtures + goldens + matrix themes | confirmed |
| EV-019/F23-R5 | OOS | Sibling product tickets; PyPI; F16–F19; F7 Planned | confirmed |
| EV-019/F23-R6 | Smoke | H1–H3 if API; H4–H5 workbench sigmet + VA when FE | confirmed |
| EV-019/F23-R7 | Journeys | UJ-034; TC-F23-001..006 | confirmed |
| EV-019/F23-R8 | API | Full endpoint review; no new routes; `product=sigmet` + content-selected VA root | confirmed |
| EV-019/E19-9 | Manifest | Mandatory + coverage matrix + API review + light plan-adherence | confirmed |
| EV-019/E19-10 | UI preview | Docs/repo only | confirmed |
| EV-019/E19-12 | Themes | G1–G3 / V1–V3 / C1 | confirmed |
| EV-019/E19-14 | FE catalog | No new filters; smoke only | **amended** by E19-17=B |
| EV-019/E19-15 | Milestone order | Research → G1–G2 → G3 → V1–V2 → V3 → C1 → smoke | confirmed |
| EV-019/E19-16 | Research M0 | Full mining → sigmet-research-catalog.md | confirmed |
| EV-019/E19-17 | FE catalog | Additive SIGMET/VA tag filters (amends E19-14) | confirmed |
| EV-019/E19-18 | Deps | AskQuestion per new dep (prefer none) | confirmed |
| EV-019/manifest | Docs | Spec, journeys, test-plan, coverage matrix, API contract | confirmed |

## EV-023 / #800 — APAC FAQ + codes encode/validate deepen (2026-07-30)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-023/E23-1 | Fn | Deepen F6+F2+F12(+F13); no new Fn | confirmed |
| EV-023/E23-2 | Scope | Full #800 backlog P0+P1+actionable P2; OOS per ticket Out-of-scope + #740/#741 | confirmed |
| EV-023/E23-3 | Routing | Lean+build 01/02/04/07/08/10; 13 when behavior ships; skip 03/05/06/09/12 | confirmed |
| EV-023/E23-4 | Deploy | 13-deploy-smoke when convert/validate ships | confirmed |
| EV-023/E23-ui | UI | N/A — no new UI; no new UJ | confirmed |
| EV-023/manifest | Docs | feature-list deepen + test-plan TC-EV023 + config-spec translationCentre + journeys note | confirmed |
| EV-023/journeys | Tests | TC-EV023-001..009; deepen UJ-001/005/006/016 | confirmed |
| EV-023/api | API | No new routes expected; optional convert flag for translationCentre (name in 04) | confirmed |

## EV-024 / #804+#807+#773 — IWXXM domain mine + WMO sample menu (2026-07-30)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-024/E24-1 | Session | Open S031 via 00-context; Lean+build | confirmed |
| EV-024/E24-2 | Issues | #804+#807+#773; exclude #806 | confirmed |
| EV-024/E24-3 | Depth | Full ticket AC (mine + matrices + wire + promote + child issues) | confirmed |
| EV-024/E24-4 | Routing | Lean+build; 13 when catalog/API ships | confirmed |
| EV-024/E24-ui | UI preview | UIb — docs/repo only; re-offer at 11 | confirmed |
| EV-024/manifest | Docs | M3 — lean delta + **new UJ-039**; skip Spec/Config/API/Deploy | confirmed |
| EV-024/E24-C | Catalog | Hybrid C1+C2+C3: discovery + validate/CI wire + **WMO examples in sample menu**; strict vs reference tiers; ADR-032 amend; encode gaps → children | confirmed |
| EV-024/journeys | UJ | **UJ-039** new; deepen UJ-036/UJ-032 | confirmed |
| EV-024/tests | TC | TC-EV024-001..008 | confirmed |
| EV-024/S02.M1 | Catalog field | `wmoReference?: boolean` in 04 (keep wmoPass/wmoSeed) | confirmed |
| EV-024/S02.M2 | Stem set | Product-in-scope + TAC peers; SWX/VONA/WAFS/QVACI deferred | confirmed |
| EV-024/S02.L1 | Vitest | Amend examplesCatalog tests for pass **or** reference in 07 | confirmed |
| EV-024/E24-02 | Gate A | PASS Batch F 1,1,1 → 04-tech-plan | confirmed |

## EV-027 / #815 — Official WMO decode residual matrix (2026-07-31)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-027/E27-1 | Session | Open S034 / EV-027; #815 inventory + residual matrix + CI | confirmed |
| EV-027/E27-2 | Routing | Lean+build; 13 when ships; skip 03/05/06/09/11/12 | confirmed |
| EV-027/E27-3 | UI preview | Defer until after build (`D-S034-open` Q3=2) | confirmed |
| EV-027/E27-4 | Triage | Fix decode when cheap; else allowlist + child issue (no silent leftovers) | confirmed |
| EV-027/E27-M | Docs | **Lean** — feature-list + user-journeys (UJ-042) + test-plan (TC-EV027-001..005) + requirements/evolve decisions; skip Spec/Config/API/Deploy | confirmed |
| EV-027/E27-UJ | Journey | **New UJ-042**; deepen UJ-039 / UJ-020 | confirmed |
| EV-027/E27-TC | TC ids | **New TC-EV027-001..005** | confirmed |
| EV-027/E27-E1 | Close 01 | Mark 01 completed → start 02-verify-plan | confirmed |
| EV-027/S02.M1 | Allowlist SoT | Package test artifact; FIXTURE_GAPS = catalog/load gaps only | confirmed |
| EV-027/S02.M2 | Gate C bar | All seven target empty residuals; allowlist only with standing-doc intent (F9 G4 / ADR-025) + child issue | confirmed |
| EV-027/S02.L1 | Inventory SoT | Pytest-discovered vendor/mirrored TAC peers | confirmed |
| EV-027/E27-02 | Gate A | PASS Batch F 1,2,1 → 04-tech-plan | confirmed |
| EV-027/E27-T1..T5 | Batch T | Order/grain/deps/Gate C/draft = **2,1,2,1,1** | confirmed |
| EV-027/E27-04 | Gate B | Approve M0–M3 (catalog-first) → 07-build @ T0.1 | confirmed |

## EV-026 / #809 — VA multi-location ADR-032 equality / wmoPass (2026-07-31)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-026/E26-1 | Session | Open S033 / EV-026; #809 equality only | confirmed |
| EV-026/E26-2 | Depth | ADR-032 equality → catalog `wmoPass` → close #809 | confirmed |
| EV-026/E26-3 | Routing | Lean+build; 13 when ships; skip 03/05/06/09/11/12 | confirmed |
| EV-026/E26-4 | Out | No US REMARKS reopen; no #738 | confirmed |
| EV-026/E26-ui | UI | N/A — catalog/Vitest only | confirmed |
| EV-026/E26-M | Docs | **Lean** — feature-list + user-journeys (UJ-041) + test-plan (008/009 strict) + requirements/evolve decisions; skip Spec/Config/API/Deploy | confirmed |
| EV-026/E26-TC | TC ids | **Reuse** TC-EV025-008..009 with EV-026 strict/`wmoPass` semantics | confirmed |
| EV-026/E26-E1 | Close 01 | Mark 01 completed → start 02-verify-plan | confirmed |
| EV-026/E26-T1..T5 | Batch T | Order/grain/deps/Gate C/draft = **1,1,2,1,1** | confirmed |
| EV-026/E26-04 | Gate B | Approve M0–M3 (12 tasks) → 07-build @ T0.1 | confirmed |

## EV-025 / #810+#811+#812+#809 — iwxxm-us REMARKS encode + VA multi-location (2026-07-31)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-025/E25-1 | Session | Open S032; #810+#811+#812 one cycle | confirmed |
| EV-025/E25-2 | Depth | Full ticket AC (lint + encode + goldens + validate smoke) | confirmed |
| EV-025/E25-3 | Routing | Lean+build; 13 when behavior ships; skip 03/05/06/09/11/12 | confirmed |
| EV-025/E25-4b | Scope | Dual lane: US pack + #809 VA multi-location | confirmed |
| EV-025/E25-4c | US breadth | All remaining dig ❌ US types | confirmed |
| EV-025/E25-ui | UI | N/A — no UI this session | confirmed |
| EV-025/manifest | Docs | **M2** lean + journeys: feature-list + test-plan + **UJ-040/041** + deepen UJ-010/026/034/039; skip Spec/Config/API/Deploy | confirmed |
| EV-025/journeys | UJ | **UJ-040** US REMARKS pack; **UJ-041** #809 promote; deepen 010/026/034/039 | confirmed |
| EV-025/tests | TC | TC-EV025-001..010 | confirmed |
| EV-025/api | API | No new routes; thin convert/validate smoke if needed | confirmed |
| EV-025/S02.M1 | #809 golden | Soft-compare first; `wmoPass` only when ADR-032 equality holds | confirmed |
| EV-025/S02.M2 | Dig residuals | Aim close all ❌ in-cycle; soft Gate C deferral **superseded by E25-T5=3** | amended |
| EV-025/S02.L1 | SCH smoke | TC-EV025-010 may document SCH deferrals without blocking Lane A goldens | confirmed |
| EV-025/E25-02 | Gate A | PASS Batch F 1,1,1 → 04-tech-plan | confirmed |
| EV-025/E25-T1 | Milestone order | M0→#810→#811→#812→adjacent→#809→validate→Gate C | confirmed |
| EV-025/E25-T2 | Goldens | Per dig type/row encode (+lint) | confirmed |
| EV-025/E25-T3 | Deps | AskQuestion per new dep | confirmed |
| EV-025/E25-T4 | Lanes | Finish Lane A then Lane B | confirmed |
| EV-025/E25-T5 | Gate C residuals | Encode residual **blocks** Gate C (supersedes S02.M2 soft deferral) | confirmed |
| EV-025/E25-T6 | Draft plan | Draft from T1–T5; Gate B pending | confirmed |
| EV-025/E25-04 | Gate B | Approve M0–M7 → 07-build @ T0.1 | confirmed |

## EV-045 / #725 — Rust crate CI (2026-08-08)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-045/scope | Fn | Deepen **F13** + **F14** (no new Fn; M5 optional later) | confirmed |
| EV-045/ui | UI | N/A — no browser UI / no H4–H5 | confirmed |
| EV-045/workflow | CI shape | Extend `ci-cd.yml` (matrix over both crates); separate `rust-ci.yml` only if latency forces | confirmed |
| EV-045/clippy | Lint policy | `cargo clippy -- -D warnings` hard-fail; allowlist only if build proves need | confirmed |
| EV-045/make | Local | `make rust-check` mirrors CI | confirmed |
| EV-045/docs | Standing | feature-list, test-plan TC-EV045-*, UJ-DEV-006, tech-spec pointer | confirmed |
| EV-045/01-ac | Gate | D-S054-01-ac=1 — ACs + defaults confirmed → 02 | confirmed |

## EV-031 / #842+#830+#712 — Platform independence (2026-08-03)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| EV-031/E31-M | Document Manifest | Full 1–10; Feature List first | confirmed |
| EV-031/F30 | Feature List F30 | Accept; owns #830+#712; public convert APIs | confirmed |
| EV-031/F31 | Feature List F31 | Accept; hybrid sessions; F21 Amended | confirmed |
| EV-031/guest-merge | Guest→login | **Auto-upload** all eligible local drafts (no prompt) | confirmed |
| EV-031/auth | Auth model | Supabase Auth for long-term storage only | confirmed |
| EV-031/data | Data plane | DigitalOcean Postgres for product DB + F8 | confirmed |
| EV-031/host | Hosting | DOKS production cutover; Render retire after soak | confirmed |
| EV-031/spec-topo | Spec topology | packages/auth + work-sessions* restored | confirmed |
| EV-031/spec-data | Data/cutover | Single DO DB; Alembic; one-time migrate Supabase→DO | confirmed |
| EV-031/uj | User Journeys | UJ-045..048; persistent guest banner | confirmed |
| EV-031/tp | Test Plan | TC-F30/F31/EV031; H4–H5 required; lean remaining docs | confirmed |
| EV-031/docs-lean | Standing deltas | test-plan, config, env-contract, api, deploy, deps, ADR-033, migration note | drafted |
| EV-031/02-batch-c | Stale F21 + Gate A | Fix C1–C5; ADR-033 Proposed; Gate A PASS → 04 | confirmed |


