# 02-verify-plan audit — S011 / EV-008

> **Date**: 2026-07-13  
> **Mode**: delta (F7 operator UI)  
> **Session**: S011-f7-operator-ui  
> **Cycle**: EV-008

## Consistency checklist (16-evolve)

| Check | Result | Notes |
|-------|--------|-------|
| F7 in feature-list + spec + tests | **PASS** | F7 detail + UJ-013/015–019 + TC-F7-001–006 |
| Config param names | **PASS** (after deploy.md fix) | `E2E_USER_*`; no `/admin` on baseUrl |
| api-contract vs deploy topology | **PASS** | static+api+worker; decode/preview on API |
| test-plan ↔ journey IDs | **PASS** | UJ-015–019 mapped; acceptance-criteria skipped by manifest |
| CodeMirror in dependency-inventory | **PASS** | Pins deferred to 04 (noted) |
| data-management-plan | **N/A** | No new external datasets |
| execution-plan tasks | **N/A** | 04 not started |
| ADRs referenced | **PASS** | ADR-020/021/022; inline HTML comments optional |
| template contradiction | **PASS** | BYO does not add deployable |
| Stale denied statements | **PASS** after fixes below |

## Auto-approved (high confidence)

| ID | Statement | Source |
|----|-----------|--------|
| H1 | F7 built this cycle (EV-008) | feature-list, session brief |
| H2 | Unified `tac_work_sessions` + migrate F5 (R2′) | ADR-020, spec, feature-list |
| H3 | `/admin/*` removed; BYO credentials | ADR-021, api-contract |
| H4 | `preview=true` on `/convert` (not separate route) | ADR-022, api-contract |
| H5 | `POST /api/v1/decode-tac` + optional issue `start`/`end` | api-contract, UJ-015 |
| H6 | H4–H5 connectivity required for workbench | test-plan, feature-list AC#7 |
| H7 | CodeMirror 6 approved; install in 04/07 | dependency-inventory, R3 |
| H8 | `ADMIN_*` → `E2E_USER_*` | config-spec, env-contract, ADR-021 |

## Fixed during audit (no user decision needed)

| Fix | Evidence |
|-----|----------|
| `deploy.md` `/admin` on baseUrl → removed | contradicted api-contract/config-spec |
| `deploy.md` `ADMIN_*` → `E2E_USER_*` | contradicted ADR-021 |
| F6 Non-Goals “Extend F5…” annotated superseded by R2′ | contradicted ADR-020 |

## Medium / low confidence — user review

| ID | Conf | Statement | Ask |
|----|------|-----------|-----|
| M1 | Medium | **One WIP per user total** across all products on unified table | Keep, or one WIP **per product**? |
| M2 | Medium | `decode-tac` requires `product` (same as convert) | Keep required, or allow omit+auto in 04? |
| L1 | Low | CodeMirror exact npm package set/versions | Defer pins to 04 (recommended) |
| L2 | Low | Dual-write duration for `metar_work_sessions` → `tac_work_sessions` | Defer cutover plan to 04 (recommended) |

## Connectivity audit

- UI journeys UJ-013/015–019 describe browser→API calls → test-plan includes H4–H5 and H6′ — **PASS**
- Vitest-only not claimed as sole E2E — **PASS**
- Different-origin topology documented — **PASS**

## Verdict (pending M1/M2)

Pending user batch on M1–M2 / L1–L2. Recommended: keep M1 as one WIP total; product required on decode; defer L1–L2 to 04.

## User verdicts (2026-07-13)

| ID | Decision |
|----|----------|
| M1 | **Approved** — one WIP per user total across products |
| M2 | **Approved** — `decode-tac` `product` required |
| L1 | **Approved** — CodeMirror pins deferred to 04 |
| L2 | **Approved** — migration dual-write deferred to 04 |

**Overall**: **PASS** — 02-verify-plan complete; ready for A→B gate → 04-tech-plan (03 skipped).
