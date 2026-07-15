# Execution Plan — S011 F7 Operator UI (EV-008)

> **Project**: METAR to IWXXM Converter  
> **Generated**: 2026-07-13  
> **Skill**: 04-tech-plan (delta)  
> **Session**: S011-f7-operator-ui  
> **Evolve cycle**: EV-008  
> **Branch**: `evolve/S011-f7-operator-ui`  
> **Mode**: delta (does not reset S008 plans)  
> **Specs consumed**: feature-list.md §F7, spec.md §F5/F7, user-journeys.md UJ-004/013/015–019,
> test-plan.md TC-F7-*, api-contract.md, config-spec.md, env-contract.md, dependency-inventory.md,
> ADR-020/021/022, context/f7-operator-ui.md, 02-verify-plan-audit.md

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase D — T6.4 in_progress (12 done / 13 pending); preparing PR-EV-008 |
| **Active milestone** | M6 — Verify & deploy |
| **Active task** | T6.4 in_progress (12 approved; 13 blocked on merge) |
| **Tasks completed** | M1–M5 + T6.1 + T6.2 + T6.3 |
| **Last updated** | 2026-07-14 |

## Tech Stack Summary (S011 delta)

| Category | Choice | Source |
|----------|--------|--------|
| Template | `static+api+worker` (unchanged) | ADR-018 |
| Language | Python 3.12 + uv; Node 22 + pnpm | ADR-005 |
| Editor | **CodeMirror 6** — `@codemirror/view`, `state`, `commands`, `language` + basic setup | R3; 04 Batch 1 A |
| Decode API | `POST /api/v1/decode-tac`; `product` **required** | api-contract; M2=A |
| Soft-preview | `preview=true` on `POST /api/v1/convert` | ADR-022 |
| Spans | Optional `start`/`end` on lint/validate issues | api-contract |
| Sessions | Unified `tac_work_sessions`; **expand-cutover** migrate (no long dual-write) | ADR-020; 04 A |
| Session API | Keep `/api/v1/work-sessions*` + top-level `product` | api-contract |
| WIP rule | **One WIP per user total** | 02 M1=A |
| Admin / BYO | Remove `/admin/*`; BYO env; `E2E_USER_*` harness | ADR-021 |
| Debounce | **300ms** lint/decode; AbortController | 04 A |
| Live IWXXM | **Off by default** (toggle) | 04 A |
| CORS / H0c | **Reuse** existing unit + `verify_connectivity.sh` | 04 A |
| Deploy | Existing Render API + static (+ worker untouched) | deploy.md |

## Feature ↔ Milestone Mapping

| Feature / issue | Milestone | Deliverable |
|-----------------|-----------|-------------|
| #697 BYO + admin | M1 | Admin gone; E2E_USER_*; docs already mostly done |
| #702 decode + spans | M2 | decode-tac + CodeMirror + decode panel |
| #665/#666 Failed + preview | M3 | Cue + preview path |
| #694 workbench | M4 | Live debounce/spans/console |
| F7 / R2′ sessions | M5 | Unified table + migrate + My METARs filter |
| Verify & deploy | M6 | 08–13; TC-F7-001–006; issue closeout |

## Data Dependencies

| Asset | Type | Staging Status | Needed By |
|-------|------|----------------|-----------|
| Supabase Postgres | DB | present (BYO) | M5 migration |
| Existing `metar_work_sessions` rows | data | present | M5 cutover copy |
| Golden TAC fixtures (7 products) | test-data | present / extend | M2–M4 |
| Vendor schemas | schemas | present | unchanged |
| CodeMirror 6 npm packages | dep | **to install** | M2 |

## Implementation Phases

### Phase 1: Admin removal + BYO harness (M1)

**Objective**: Product admin surface gone; live harness uses `E2E_USER_*`.  
**Entry gate**: This plan approved.  
**Exit gate**: TC-F7-006 green at T2; no AdminDashboard routes.

#### M1: F7.a — Admin / BYO harness (#697)

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T1.1 | Test: `/admin` and legacy admin deep links → not-found (TC-F7-006) | Test | completed | UJ-019 | — |
| T1.2 | Remove frontend AdminDashboard / `/admin` routes and nav links | Impl | completed | ADR-021 | T1.1 |
| T1.3 | Remove or hard-disable `packages/auth` admin API routers (`/admin/*`) | Impl | completed | api-contract | T1.1 |
| T1.4 | Retarget tests: drop admin suite; rename `ADMIN_*` → `E2E_USER_*` in harness/Makefile/docs still listing admin | Impl | completed | config-spec | T1.2, T1.3 |
| T1.5 | Update `.env.example` + env-check for `E2E_USER_*`; warn on `ADMIN_*` | Impl | completed | env-contract | T1.4 |
| T1.6 | PR-M1: admin removal | PR | pending | — | T1.2–T1.5 |

**PR**: PR-M1 → `evolve/S011-f7-operator-ui` (or main per git strategy)

---

### Phase 2: Spans + decode + editor shell (M2)

**Objective**: Offset-aware lint/decode; CodeMirror shell; decode panel UI.  
**Exit gate**: TC-F7-002 green (API + panel smoke).

#### M2: F7.b — Decode + spans (#702)

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T2.1 | Test: lint/validate issue models accept optional `start`/`end` | Test | completed | api-contract | M1 |
| T2.2 | Impl: tac-validate / tac2iwxxm emit offsets where available (METAR/SPECI/TAF first; VAA/TCA best-effort+residuals G4) | Impl | completed | feature-list G4 | T2.1 |
| T2.3 | Test: `POST /api/v1/decode-tac` contract (product required; segments + residuals) | Test | completed | TC-F7-002 | M1 |
| T2.4 | Impl: decode library API + backend thin wrapper `/decode-tac` | Impl | completed | api-contract | T2.3, T2.2 |
| T2.5 | Add CodeMirror 6 packages to frontend; inventory pins | Impl | completed | dependency-inventory | M1 |
| T2.6 | Test: decode panel Code\|Explanation + residual display | Test | completed | UJ-015 | T2.4, T2.5 |
| T2.7 | Impl: replace textarea shell with CodeMirror; decode panel collapsible | Impl | completed | UJ-013/015 | T2.6 |
| T2.8 | PR-M2: decode + CodeMirror | PR | completed | — | T2.2–T2.7 |

---

### Phase 3: Failed-TAC + soft-preview (M3)

**Objective**: Distinct failure cue; `preview=true` convert path.  
**Exit gate**: TC-F7-003 green.

#### M3: F7.c — Failed-TAC + preview (#665/#666)

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T3.1 | Test: convert with `preview=true` → 200 + `failed_spans` + best-effort XML | Test | completed | ADR-022 | M2 |
| T3.2 | Impl: tac2iwxxm soft-preview hooks + backend `preview` form flag | Impl | completed | api-contract | T3.1 |
| T3.3 | Test: Failed-TAC visual cue in editor/results | Test | completed | UJ-016 | T3.2 |
| T3.4 | Impl: Failed-TAC cue + wire preview control in UI | Impl | completed | #665/#666 | T3.3 |
| T3.5 | PR-M3: preview + Failed-TAC | PR | completed | — | T3.2–T3.4 |

---

### Phase 4: Live workbench (M4)

**Objective**: Debounced live assist without melting the API.  
**Exit gate**: TC-F7-004 green.

#### M4: F7.d — Live workbench (#694)

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T4.1 | Test: debounce 300ms + AbortController cancels in-flight | Test | completed | UJ-017 | M3 |
| T4.2 | Impl: live lint/decode clients; span highlight + hover | Impl | completed | #694 | T4.1, T2.7 |
| T4.3 | Impl: pull-up console; live IWXXM toggle (**default off**) | Impl | completed | 04 A | T4.2 |
| T4.4 | Test: Playwright workbench smoke (TC-F7-001/004) | Test | completed | test-plan | T4.3 |
| T4.5 | Confirm H0c/H4–H5 still green (reuse existing CORS/connectivity) | Test | completed | connectivity-gates | T4.4 |
| T4.6 | PR-M4: live workbench | PR | completed | — | T4.2–T4.5 |

---

### Phase 5: Unified sessions (M5)

**Objective**: Expand-cutover to `tac_work_sessions`; My METARs filter.  
**Exit gate**: TC-F7-005 + TC-004′ green.

#### M5: F7.e — Unified sessions (R2′ / ADR-020)

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T5.1 | Test: session schema + `product` + one-WIP-total rule | Test | completed | 02 M1 | M4 |
| T5.2 | Migration: create `tac_work_sessions`; copy from `metar_work_sessions`; cutover backend; DROP old | Impl | completed | ADR-020; expand-cutover | T5.1 |
| T5.3 | Impl: work-sessions API `product` field + list filter | Impl | completed | api-contract | T5.2 |
| T5.4 | Impl: My METARs = `product IN (metar,speci)`; workbench history all products | Impl | completed | UJ-004/018 | T5.3 |
| T5.5 | Test: migrate smoke + non-METAR Draft resume (TC-F7-005) | Test | completed | UJ-018 | T5.4 |
| T5.6 | PR-M5: unified sessions | PR | completed | — | T5.2–T5.5 |

---

### Phase 6: Verify & deploy (M6)

**Objective**: Quality gates and production smoke.  
**Exit gate**: Routing 08–13 complete or waived per user; child issues closed; #5 stays open.

#### M6: F7.f — Verify & deploy

| ID | Task | Type | Status | Spec | Depends |
|----|------|------|--------|------|---------|
| T6.1 | 08-verify-build full suite on evolve tip | Verify | completed | 08 skill | M5 |
| T6.2 | 09-qa + 10-e2e (TC-F7-001–006 focus) | Verify | completed | test-plan | T6.1 |
| T6.3 | 11-verify-impl per F7 acceptance 1–8 | Verify | completed | feature-list | T6.2 |
| T6.4 | 12-verify-deploy + 13-deploy-smoke (API then frontend) | Deploy | in_progress (12 done / 13 pending) | deploy.md | T6.3 |
| T6.5 | Close/link #697/#702/#665/#666/#694; comment on #5 | Ops | pending | Phase 0 | T6.4 |
| T6.6 | Evolve summary + CHANGELOG | Docs | pending | 16-evolve | T6.5 |

## Git Strategy

| Change | Branch | Base |
|--------|--------|------|
| Session | `evolve/S011-f7-operator-ui` | `main` |
| Minor PRs | Optional `feat/S011-M{N}-*` → evolve branch | per milestone |
| Major | Evolve PR → `main` after M6 / phase D | — |

**Commit format**: `[T{n}.{m}] type: description` or `[S011] docs: …` for plan docs.

### PR Plan

| PR | Type | Scope | Status |
|----|------|-------|--------|
| PR-M1 | Minor | Admin removal | pending |
| PR-M2 | Minor | Decode + CodeMirror | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716 |
| PR-M3 | Minor | Preview + Failed-TAC | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/717 |
| PR-M4 | Minor | Live workbench | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/718 |
| PR-M5 | Minor | Unified sessions | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/720 |
| PR-EV-008 | Major | Evolve → main | open — https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716 (no merge yet) |

## Phase Gate Check (B→C)

Before 07-build:

- [ ] This execution plan user-approved
- [ ] 05-verify-tech PASS (or in-progress)
- [ ] 06 skipped per routing
- [ ] CodeMirror license/pin recorded in dependency-inventory at install
- [ ] ADR-020/021/022 accepted (done)

## Connectivity tasks (reuse)

| Task | Status |
|------|--------|
| `test_cors_policy.py` (H0c) | **PASS** 2026-07-14 (T4.5) — 6 passed |
| `scripts/deploy/verify_connectivity.sh` (H4–H5) | exists — re-run M6 (T6.4) |
| New CORS config | **not required** (04 A) |

## Risks

| Risk | Mitigation |
|------|------------|
| Live workbench request storms | 300ms debounce + Abort; live IWXXM off by default |
| VAA/TCA weak offsets | Residuals explicit (G4); don't block M2 |
| Session migration data loss | Expand-cutover with copy verification tests before DROP |
| Admin removal breaks ops habit | BYO docs + TC-F7-006; no paste-keys |

## Session changelog

- 2026-07-13: Initial plan — 04 Batch 1 A (expand-cutover; CM6 packages; 300ms; live IWXXM off; keep work-sessions paths; reuse CORS)
- 2026-07-14: M4 complete (T4.1–T4.6); PR-M4 #718 open; next M5 T5.1
- 2026-07-14: M5 started — T5.1 in_progress (unified tac_work_sessions)
- 2026-07-14: M5 impl done (T5.1–T5.5); remote migration `20260714000010` applied (13 rows cutover); next T5.6 PR-M5
- 2026-07-14: PR-M5 #720 open; next M6
- 2026-07-14: Committed M1 leftover (bdcb9b8) + S010 mining docs (b5b79d7); M6 T6.1 in_progress
- 2026-07-14: T6.1 PASS (verification-report.md); compose integration SKIPPED (host ports/disk); next T6.2
- 2026-07-14: C→D passed (D-S011-EV008-c-to-d-pass); T6.2 09-qa+10-e2e in_progress
- 2026-07-14: T6.2 pass_with_advisories (qa-report + e2e-report); T0 TC-F7 green; Playwright/compose SKIPPED (ports/disk); QA-001 type narrow fix uncommitted; next T6.3
- 2026-07-14: T6.3 11-verify-impl in_progress (user option 1 — start without committing first)
- 2026-07-14: D-S011-EV008-f7-approve — F7 approved_with_waivers (criteria 1–6 T0; H4–H5 → T6.4/CI; AdminDashboard advisory); T6.3 completed; T6.4 12-verify-deploy in_progress
- 2026-07-14: D-S011-EV008-deploy-check-A — deploy checklist approved; committing QA-001+reports; preparing PR-EV-008; T6.4 remains in_progress (12 done / 13 pending); no merge/deploy until explicit approval
