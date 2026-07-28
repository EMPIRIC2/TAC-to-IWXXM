# Execution plan — S023 / EV-017 (F21 public app + F22 privacy / #783)

> **Status**: **approved** (D-S023-04-plan-approve-A) — 07-build in progress  
> **Branch**: `evolve/EV-017-public-app-privacy`  
> **Evolve cycle**: EV-017  
> **Features**: **F21**, **F22**; deepen **F5** / **F7.h**; delete **packages/auth** (M4)  
> **Mode**: delta  
> **Spec sources**: feature-list F21/F22/F5/F7.h; spec; UJ-001/004/013/015/018/033;
> TC-004 / TC-F21-auth-gone / TC-F22-001..003; api-contract; ADR-031; E17-12..25

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M2 — IndexedDB local sessions (F7.h / F5) |
| **Active task** | T2.3 — Add idb; implement local session store |
| **Tasks** | 6 / ~28 completed |
| **Last updated** | 2026-07-28 |

## Tech Stack Summary (S023 delta)

| Area | Choice | Source |
|------|--------|--------|
| Template | `static+api+worker` unchanged | ADR-018 |
| Local sessions | IndexedDB via **`idb`**; reuse `workSessionPayload` | E17-12/13 |
| Guest migrate | One-time `sessionStorage` → IndexedDB | E17-14 |
| Prefs | `localStorage` + GPC (`Sec-GPC` + `navigator.globalPrivacyControl`) | E17-16/17 |
| Abuse | **`slowapi`** in-memory; 60/min public, 10/min dissemination, 2 MB body | E17-15/19 |
| Auth package | **Delete `packages/auth`** | E17-22 |
| Cutover | Single deploy (IndexedDB then Auth strip in same train) | E17-10/18 |
| Export/import | JSON `tac-work-sessions-export-v1` | E17-20 |
| ADR | **ADR-031** supersedes ADR-020 | E17-23 |
| Deploy | API + frontend (+ worker unchanged secrets) | Render |

## Feature ↔ Milestone Mapping

| Fn / AC | Milestone | Deliverable |
|---------|-----------|-------------|
| ADR + deps | M1 | ADR-031 Accepted; inventory + env rewrite |
| F7.h / F5 | M2 | IndexedDB store, migrate, export/import, TC-004 |
| F21 abuse | M3 | slowapi + body limit on public routes |
| F21 FE | M4 | Remove login/JWT; wire IndexedDB UI |
| F21 BE | M5 | 404 `/auth/*` + work-sessions; delete packages/auth |
| F22 | M6 | Privacy notice + settings + GPC; TC-F22-* |
| Cleanup | M7 | E2E Auth-gone; docs/CI; H4–H5 |

## Data Dependencies

| Asset | Staging | Needed By |
|-------|---------|-----------|
| Existing `workSessionPayload` / ConverterSnapshot | in-repo | M2 |
| Guest `sessionStorage` key (`metar_guest_converter_state`) | runtime | M2 migrate |
| Legacy `tac_work_sessions` rows | ops archive (~30d) — not product API | M5/M7 docs |
| Model weights / external corpora | **N/A** | — |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-017` · `feature_ids: [F21, F22]`

### M1 — ADR + inventory + env contract

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Docs | Accept ADR-031; mark ADR-020 Superseded | ADR-031; E17-23 | — | completed |
| T1.2 | Docs | dependency-inventory: add `idb`, `slowapi`; remove `packages/auth` / operator supabase-js Auth | E17-12/15/22 | T1.1 | completed |
| T1.3 | Docs | env-contract full F21 rewrite (rate-limit env names; drop E2E_USER/DISABLE_AUTH) | E17-24; C-EV017.5 | T1.1 | completed |
| T1.4 | Docs | Back-add rate-limit env names to config-spec / staging-secrets-matrix stubs | connectivity; E17-19 | T1.3 | completed |

### M2 — IndexedDB local sessions (F7.h / F5)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Unit tests: IDB CRUD, My METARs filter, soft-delete, export/import round-trip (TC-004) | TC-004; UJ-004/018 | T1.2 | completed |
| T2.2 | Test | One-time sessionStorage → IndexedDB migrate test | E17-14 | T2.1 | completed |
| T2.3 | Code | Add `idb` dep; implement local session store reusing `workSessionPayload` | E17-12/13; ADR-031 | T2.1 | pending |
| T2.4 | Code | Wire autosave/resume/sidebar/My METARs to IndexedDB (no `workSessionApi` HTTP) | UJ-004/018; F7.h | T2.3 | pending |
| T2.5 | Code | Export/import UI for `tac-work-sessions-export-v1` | E17-20 | T2.3 | pending |

### M3 — Public API abuse controls (F21)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | Rate-limit + body-size unit/integration (429 / 413) | E17-19; api-contract | T1.3 | pending |
| T3.2 | Code | Add `slowapi`; wire limits on public `/api/v1/*`; env knobs | ADR-031; E17-15 | T3.1 | pending |
| T3.3 | Test | Dissemination routes use stricter limit; allowlist unchanged | ADR-029; E17-19 | T3.2 | pending |

### M4 — Frontend Auth removal (F21)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Vitest/Playwright: no login chrome; convert without JWT; Auth routes absent in FE | TC-F21-auth-gone; UJ-001 | T2.4 | pending |
| T4.2 | Code | Remove authService/login/register UX; stop attaching Bearer to public API | F21; api-contract | T4.1 | pending |
| T4.3 | Code | Drop FE Supabase Auth client usage from `/config.json` path (if any) | E17-24 | T4.2 | pending |

### M5 — Backend Auth + work-sessions teardown + delete packages/auth

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | `/auth/*` and `/api/v1/work-sessions*` → 404; convert without Authorization | TC-F21-auth-gone | T3.2 | pending |
| T5.2 | Code | Remove auth routers/middleware/JWT gates; retire DISABLE_AUTH | F21; ADR-031 | T5.1 | pending |
| T5.3 | Code | Remove work-sessions routers; stop writing `tac_work_sessions` from API | F7.h; E17-5 | T5.2 | pending |
| T5.4 | Config | Delete `packages/auth` workspace member; fix Docker/CI/Makefile/coverage gates; inline residuals | E17-22 | T5.2 | pending |
| T5.5 | Docs | Ops note: ~30-day archive of legacy rows (no public API) | E17-5 | T5.3 | pending |

### M6 — Privacy preference center (F22)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | TC-F22-001..003: notice, settings, GPC | UJ-033; TC-F22-* | T4.2 | pending |
| T6.2 | Code | First-visit notice + Privacy settings; localStorage prefs; disclose IndexedDB | F22; E17-7/16/17 | T6.1 | pending |
| T6.3 | Code | Honor Sec-GPC + `navigator.globalPrivacyControl` | E17-16 | T6.2 | pending |

### M7 — E2E / docs / connectivity gate

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T7.1 | Test | Playwright: public UJ-001/004/013/018; Auth-gone negative; privacy smoke | test-plan; H6 | M2–M6 | pending |
| T7.2 | Test | H4–H5 connectivity after FE/API deploy | connectivity-gates | T7.1 | pending |
| T7.3 | Docs | Update deploy.md / CORPUS refs; session 04 report; CHANGELOG draft bullets | docs corpus | T5.4 | pending |
| T7.4 | Config | Confirm Render env: remove Auth secrets from API if unused; keep F8 + allowlist | env-contract | T1.3 | pending |

## Phase Gate Check (B→C)

- [x] Execution plan approved (E17-25 / D-S023-04-plan-approve-A)
- [x] ADR-031 Accepted (T1.1 / D-S023-04-plan-approve-A)
- [x] 05/06 skipped per Standard (re-open only if hooks/deps conflict)
- [x] env-contract rewrite committed (E17-24; bf4eaf1; T1.3 affirms)
- [x] No tasks outside F21/F22/F5/F7.h/auth-delete scope

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-017-public-app-privacy` |
| Commits | `[T{n}.{m}]` per task; docs commits for ADR/env |
| PR | Minor PR to `main` after Phase C/D per routing |
| Cutover | Single release: M2–M6 land before/at same deploy (E17-18) |

## PR Plan

| PR | When | Status |
|----|------|--------|
| Draft #786 | Interim docs | open |
| Final EV-017 | After 08–11 (or earlier docs+code) | pending |

## References

- ADR-031, evolve-decisions EV-017 (E17-12..25)
- reports/02-verify-plan.md; impact-analysis.md
- Issue #783
