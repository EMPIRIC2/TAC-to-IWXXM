# Execution plan — S024 / EV-018 (F16 multi-file export selection / #785)

> **Status**: **approved** (D-S024-04-plan-approve-A)  
> **Active task**: 08-verify-build (M1–M4 code complete)

## Current State

| Field                | Value                                      |
| -------------------- | ------------------------------------------ |
| **Active phase**     | Phase C — 07-build complete → 08           |
| **Active milestone** | M4 done                                    |
| **Active task**      | handoff to 08                              |
| **Tasks**            | 14 / 14 completed                          |
| **Last updated**     | 2026-07-28                                 |

## Tech Stack Summary (S024 delta)

| Area              | Choice                                                                                         | Source        |
| ----------------- | ---------------------------------------------------------------------------------------------- | ------------- |
| Template          | `static+api+worker` (unchanged)                                                                | ADR-018       |
| Scope             | Frontend dissemination drawer multi-select + sequential preflight/send + progress graphic      | E18-2 / #785  |
| API               | Existing `POST /api/v1/dissemination/preflight` + `/send` only; N sequential client calls      | E18-5         |
| Caps              | Selection count ≤20; existing body/size limits                                                 | E18-6         |
| Candidates        | Current-session convert outputs + dropped files only (no Finished IndexedDB)                   | E18-4         |
| Single candidate  | Auto-select; Export selection collapsed/optional                                               | E18-9         |
| Sequencing        | **Interleaved** per file: preflight→send→next; continue on failure                             | E18-10 / E18-11 |
| Progress UI       | Per-file mail→destination along arrow; green check / red fail; CSS + `motion` + lucide         | E18-10 / E18-13 |
| Reduced motion    | Hide graphic; text-only progress list when `prefers-reduced-motion`                            | E18-14        |
| Primary action    | One **Disseminate** (preflight→send per file); optional **Preflight only** secondary           | E18-15        |
| New npm deps      | **None** — reuse `motion`, `lucide-react`, Radix checkbox                                      | E18-13        |
| Auth              | Public app (F21); no Bearer JWT                                                                | ADR-031       |
| Security          | BYOC memory-only; allowlist unchanged                                                          | ADR-021/029/030 |
| Tests             | Vitest (selection/aggregator/progress states) + Playwright UJ-027–030 + screenshot snapshot    | E18-16        |
| CORS / API / env  | No new routes, CORS, or `DISSEMINATION_EGRESS_ALLOWLIST` changes                               | Lean+build    |
| Deploy            | Frontend static redeploy; H6′ live at 13                                                       | E18-7         |

## Feature ↔ Milestone Mapping

| AC / decision                                              | Milestone | Deliverable                                      |
| ---------------------------------------------------------- | --------- | ------------------------------------------------ |
| Candidate list; ≤20; empty disables; E18-4 sources         | M1        | Selection model + pure helpers                   |
| Interleaved N sequential; continue on fail; aggregate      | M2        | `runDisseminationQueue` aggregator               |
| Panel UI; select-all/clear; progress graphic; E18-9/15     | M3        | Drawer UX + `DisseminationProgressRow`           |
| TC-F16-005; UJ-027–030; visual snapshot of progress row    | M4        | Vitest + Playwright                              |

## Data Dependencies

| Asset                         | Staging | Needed By |
| ----------------------------- | ------- | --------- |
| Backend / DB / new fixtures   | **N/A** | —         |
| Existing drawer Vitest mocks  | present | T1.1+     |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-018` · `feature_ids: [F16]` · deepen multi-file selection

### M1 — Candidate model + selection state

| Task | Type | Description                                                                                          | Spec Source                    | Depends On | Status  |
| ---- | ---- | ---------------------------------------------------------------------------------------------------- | ------------------------------ | ---------- | ------- |
| T1.1 | Test | Unit tests: build candidates from session+drops only; ≤20 reject; empty disables; sole auto-select   | TC-F16-005; E18-4/6/9          | —          | completed |
| T1.2 | Code | `ExportCandidate` type + selection helpers (`toggle`/`selectAll`/`clear`/`cap`) in `utils/` or hook  | feature-list F16 EV-018; E18-9 | T1.1       | completed |

### M2 — Sequential interleaved aggregator

| Task | Type | Description                                                                                                | Spec Source              | Depends On | Status  |
| ---- | ---- | ---------------------------------------------------------------------------------------------------------- | ------------------------ | ---------- | ------- |
| T2.1 | Test | Aggregator tests: interleaved preflight→send; continue after fail; per-file pass/fail/skip status machine  | E18-10/11; TC-F16-005 #4 | T1.2       | completed |
| T2.2 | Code | `runDisseminationQueue` (async generator or callbacks) wrapping existing `disseminationPreflight`/`Send`   | api-contract EV-018      | T2.1       | completed |
| T2.3 | Test | Preflight-only mode does not call send; Disseminate mode runs both per file                                | E18-15                   | T2.2       | completed |

### M3 — Drawer UI + progress graphic

| Task | Type | Description                                                                                                      | Spec Source           | Depends On | Status  |
| ---- | ---- | ---------------------------------------------------------------------------------------------------------------- | --------------------- | ---------- | ------- |
| T3.1 | Test | Vitest: Export selection panel (>1); empty disables; Disseminate primary + Preflight-only; sole candidate collapsed | E18-9/15; UJ-027   | T2.2       | completed |
| T3.2 | Code | Wire selection panel into `DisseminationDrawer` (checkboxes, select-all/clear, ≤20 error)                        | #785 AC; E18-6        | T3.1       | completed |
| T3.3 | Test | Progress row states: pending → in-flight (mail along arrow) → success check / fail red X; reduced-motion text-only | E18-10/13/14        | T3.2       | completed |
| T3.4 | Code | `DisseminationProgressRow` with `motion` + lucide (Mail → sink icon); respect `prefers-reduced-motion`           | E18-13/14             | T3.3       | completed |
| T3.5 | Code | Run queue from Disseminate / Preflight-only; live-update per-file progress; keep BYOC memory-only                | ADR-029; E18-15       | T3.4       | completed |

### M4 — Coverage gate + handoff

| Task | Type   | Description                                                                                         | Spec Source              | Depends On | Status  |
| ---- | ------ | --------------------------------------------------------------------------------------------------- | ------------------------ | ---------- | ------- |
| T4.1 | Test   | Playwright: multi-select UJ-027 path + one forced fail shows red mark; remaining continue           | UJ-027; TC-F16-005       | T3.5       | completed |
| T4.2 | Test   | Playwright **visual snapshot** of progress row (in-flight + failed) via `toHaveScreenshot`          | E18-16                   | T3.4       | completed |
| T4.3 | Test   | Full FE Vitest green for touched modules                                                            | test-plan F16            | T3.1–T3.5  | completed |
| T4.4 | Docs   | HANDOFF for 08→10→13: FE-only; H6′ UJ-027–030 at 13; no API/env checklist                           | routing-plan; connectivity | T4.3     | completed |

## Phase Gate Check (B→C)

- [x] Execution plan approved (user AskQuestion) — **D-S024-04-plan-approve-A**
- [x] 05/06 skipped per Lean+build (re-open only if deps/ADR conflict) — **no new deps**
- [x] No new backend routes or env knobs
- [x] Tasks T1.1–T4.4 scoped to F16 deepen / #785 only
- [x] Progress graphic uses existing `motion` + lucide only (E18-13)

## Git Strategy

| Item               | Value                                                                      |
| ------------------ | -------------------------------------------------------------------------- |
| Branch             | `evolve/EV-018-dissemination-file-select`                                  |
| Commits            | One logical task (or tight TDD pair) per commit: `[T1.1]`, `[T1.2]`, …     |
| PR                 | Minor PR to `main` after M4 + 08 + 10; 13 after FE deploy                  |
| Out of scope files | `apps/backend/**`, `packages/dissemination/**` (read-only), env contracts  |

## PR Plan

| PR                    | Scope                                              | Status  |
| --------------------- | -------------------------------------------------- | ------- |
| S024 / F16 deepen     | Multi-select + interleaved queue + progress graphic | pending |

## Phase Gate Log

| Gate   | Result  | Date       | Notes                                      |
| ------ | ------- | ---------- | ------------------------------------------ |
| A→B    | passed  | 2026-07-28 | D-S024-02-phase-a-A; M1/M2 → 04            |
| B→C    | passed  | 2026-07-28 | D-S024-04-plan-approve-A; start 07 @ T1.1   |
| C→D    | pending | —          | after 07+08                                |
| Deploy | pending | —          | 13 H6′                                     |

## ADR / dependency note

- **No new ADR** — UI-only sequential client + progress graphic; security ADRs unchanged.
- **No dependency-inventory delta** — `motion` and `lucide-react` already in `apps/frontend/package.json`.
- **Visual regression** — first `toHaveScreenshot` for dissemination progress row (Playwright built-in; no Percy/Chromatic).
