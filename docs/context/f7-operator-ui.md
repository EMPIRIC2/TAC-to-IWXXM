# Context — F7 Multi-Product Operator UI

> **Mode**: scoped | **Slug**: f7-operator-ui | **Generated**: 2026-07-13
> **Feature / workflow**: F7 + #694/#702/#665/#666/#697 (#5 parent tracker) | **Status**: active
> **Session**: [S011-f7-operator-ui](../sessions/S011-f7-operator-ui/session-brief.md)

## Executive Summary

F6 already converts and validates all seven TAC products and F6.e ships product/profile
pickers on `FileConverter`. F7 is still **Planned** in the corpus: no workbench, no decode
panel, no multi-product sessions, and no span-level API. This session builds the operator UI
and related product-model change: **BYO-only** database/auth credentials (env including
Postgres/`DATABASE_URL`), remove the admin dashboard, add decode + span-aware lint/validate,
partial convert for highlighting, then the live workbench. Upstream packages exist; the gaps
are span offsets, decode/annotate HTTP, editor dependency (CodeMirror 6), and deliberate
corpus rewrite for admin retirement.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | Milestone order: **#697** (admin/BYO) → **#702** decode + spans foundation → **#665/#666** failed-TAC/partial → **#694** live workbench |
| R2 | Decision | **OVERRIDDEN by R2′ (2026-07-13)**. Original: separate F7 sessions; F5 table stays METAR/SPECI-only |
| R2′ | Decision | **Unified** `tac_work_sessions` for all 7 products; migrate `metar_work_sessions`; My METARs = METAR/SPECI filter; deprecate old table after cutover |
| R3 | Decision | Editor: **CodeMirror 6** (new dep — back-add to `docs/dependency-inventory.md` in 04/07) |
| R4 | Decision | API: new **`POST /api/v1/decode-tac`** (ordered segments with `start`/`end`) **and** optional `start`/`end` on lint/validate issues |
| R5 | Decision | Partial convert: soft-fail **preview** path returning best-effort IWXXM + failed-span markers (flag or dedicated endpoint — finalize in 04-tech-plan) |
| R6 | Decision | **BYO-only** credentials model: drop shared hosted multi-tenant admin assumption. Operators configure **their** Supabase **and** Postgres/`DATABASE_URL` (and related SQL URIs) via deploy/env — no in-app paste-keys UI, no central admin dashboard |

## Scope & Constraints

### In scope (S011)

| Slice | Issues | Notes |
|-------|--------|-------|
| BYO credentials + admin removal | #697 | Env-contract rewrite; delete AdminDashboard + `/admin/*`; remove approval/toggle-admin/cross-user browse |
| Decode panel (7 products) | #702 | Library + HTTP + collapsible Code\|Explanation UI; samples; residuals explicit |
| Span foundation | #694/#702/#698-related | Parser/lint offsets; shared editor span model |
| Failed-TAC + partial | #665/#666 | Distinct failure cue; best-effort XML + failed span markers |
| Live workbench | #694 | Debounced lint/validate/convert; highlight; hover; toggleable live IWXXM; pull-up console |
| Multi-product sessions | F7 / R2′ | Unified `tac_work_sessions`; migrate F5 rows; My METARs filter |
| Parent tracker | #5 | Keep open; close/link when slices land |

### Out of scope (v1)

- Teaching/CMS beyond short decode explanations
- Click-row-to-edit TAC mutation
- Full IWXXM field mapping inside decode table
- AMHS/SWIM/AFS; F8 push sinks
- Per-user “paste Supabase keys” UI (R6)
- Extending **F5** as a permanent parallel store after unified cutover (My METARs survives as filter)
- Separate F7-only sessions table alongside `metar_work_sessions` (rejected — R2′)

### Feature mapping

- **F7** — primary product home (operator entry + sessions)
- **F6** — engine deltas (spans, decode, soft preview)
- **F5** — unchanged METAR/SPECI semantics; admin browse path removed
- **M4** — auth shrinks with `/admin/*` removal

## Environment / Topology

| Concern | Today | After S011 (R6) |
|---------|-------|-----------------|
| DB / auth | Shared Supabase project + admin role | **Operator-owned** Supabase URL + keys + optional `DATABASE_URL` / Postgres URI via env |
| Admin UI | `AdminDashboard` + `/admin/*` | **Removed** |
| API origin | Render API + static frontend CORS | Unchanged topology; CORS still different-origin |
| Live editor calls | Convert click-only; no lint/validate clients | Debounced JWT-auth calls to lint/decode/validate/preview; AbortController cancel |

Browser integration risk: workbench latency on every keystroke → prefer **lint/decode first**, full validate/convert behind toggle/debounce (04-tech-plan).

## Existing Infrastructure

| Path | What exists | Gap for S011 |
|------|-------------|--------------|
| `apps/frontend/.../FileConverter.tsx` | 7-product + profile pickers; Textarea; Convert | METAR-centric copy; no live/decode/workbench |
| `apps/frontend/.../tacProduct.ts` | `TAC_PRODUCTS`, auto-detect | Reuse |
| `apps/frontend/.../api.ts` | Convert client only | Need lint/decode/validate/preview clients |
| `apps/frontend/.../admin/` | Full admin dashboard | Delete (#697) |
| `apps/frontend/.../useWorkSessionSync.ts` | 3s debounce autosave (F5) | Pattern reuse; F7 sessions separate |
| `apps/backend/.../api.py` | `/convert`, `/validate`, `/lint-tac`, `/convert-bulletin` | No `/decode-tac`; convert hard-fails; no spans |
| `apps/backend/.../schemas/*.py` | Issues with optional string `location` | Add optional int `start`/`end` |
| `packages/tac-validate` | 7-product lint; field-hint locations | Offset-aware findings |
| `packages/tac2iwxxm` | 7-product convert + IR; `scan_metar_tokens` | Decode segments; soft/partial path |
| `packages/auth/.../admin_api.py` | `/admin/*` | Remove or permanently gate off |
| Editor deps | None (Textarea) | Add **CodeMirror 6** (R3) |

## Cross-Reference Matrix

| Topic | Corpus today | Issues / S011 | Alignment |
|-------|--------------|---------------|-----------|
| F7 status | Planned; I/O TBD | Build this cycle | Evolve 01 delta → Implemented |
| F5 sessions | METAR/SPECI only (pre-S011) | R2′: unify into `tac_work_sessions`; My METARs = filter | **Amended** |
| Validate shape | Pass/fail + string `location` | Spans for #694 | **Schema delta** + ADR/api-contract |
| Admin / shared DB | Documented F5 admin + shared project | R6 BYO-only | **Deliberate product contradiction** — rewrite in 01 |
| Decode | Not in corpus | #702 | New F7/F6 companion capability |
| Partial convert | Bulletin partial only | #666 soft preview | Extend single-report path |
| #5 | Long-term UI | Parent tracker | Keep open (Phase 0 A) |

## Implementation Backlog

Suggested build milestones (R1):

1. **M1 — BYO + admin removal (#697)**  
   Env contract (`SUPABASE_*`, `DATABASE_URL` / Postgres URI); delete admin UI/routes; rewrite docs; retarget auth/RLS tests; drop approval/toggle-admin flows.

2. **M2 — Spans + decode (#702 foundation)**  
   IR/parser offsets; `POST /api/v1/decode-tac`; lint/validate issue `start`/`end`; CodeMirror 6 editor shell; decode panel UI for all 7 products (best-effort + residuals).

3. **M3 — Failed-TAC + partial (#665/#666)**  
   Soft preview/convert response with best-effort XML + failed markers; distinct Failed-TAC visual in results/editor.

4. **M4 — Live workbench (#694)**  
   Debounced lint/validate; inline highlight + hover; toggleable live IWXXM; pull-up console; request cancellation.

5. **M5 — Unified sessions (F7 / R2′)**  
   `tac_work_sessions` schema + migrate `metar_work_sessions`; retarget APIs; My METARs filter;
   workbench multi-product history; H4–H5 journeys.

6. **M6 — Verify & deploy**  
   08–13 per routing plan; close/link issues; leave #5 open with summary comment.

## Data & Credentials

- Credentials from **operator deploy env only** (R6): at minimum Supabase URL + publishable/secret keys as today’s wiring requires, plus **Postgres / `DATABASE_URL` (or equivalent SQL URI)** when direct DB access is needed.
- Never commit `.env` secrets; document in `docs/env-contract.md` during 01/04.
- Local/dev may still use `DISABLE_AUTH` patterns already in corpus — confirm in 01 whether BYO-only changes that.

## Unresolved Gaps (defer to 01 / 04)

| Gap | Owner stage |
|-----|-------------|
| Exact F7/unified sessions migration (dual-write window, WIP uniqueness across products) | 04 |
| Preview = query flag on `/convert` vs new `/preview` route | 04 |
| How far offsets are available for VAA/TCA v1 vs residuals-only | 01 + feasibility in 04 |
| CodeMirror package pins + license inventory entry | 04 / dependency decision |
| Whether self-signup vs invite-only is operator’s Supabase policy only (recommended: yes) | 01 |
| Migration path for existing shared-project users/data | 01 (explicit) |

## Sources

- [GitHub #694](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/694), [#702](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/702), [#5](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/5), [#665](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/665), [#666](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/666), [#697](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/697)
- [Docs: feature-list.md](../feature-list.md) §F7; [api-contract.md](../api-contract.md); [env-contract.md](../env-contract.md)
- [Context: realtime-tac-ingest.md](realtime-tac-ingest.md) F7 stub; [general-tac-iwxxm-converter.md](general-tac-iwxxm-converter.md); [metar-work-history.md](metar-work-history.md); [supabase-keys-config.md](supabase-keys-config.md)
- [Repo: apps/frontend FileConverter / admin / tacProduct / api.ts]
- [Repo: apps/backend api.py + schemas; packages/tac-validate; packages/tac2iwxxm; packages/auth admin_api.py]
- S011 Phase 0 approvals 2026-07-13; Phase 3 resolutions R1–R6 2026-07-13
