# 02-verify-plan report — S023 / EV-017 (in progress)

**Stage**: 02-verify-plan (delta)  
**Date**: 2026-07-27  
**Features**: F21, F22; deepen F5/F7 (F7.h); deprecate operator M4  
**Issue**: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)  
**Gate**: User **A** — run 02 (`D-S023-02-verify-plan-gate-A`)  
**Status**: **in_progress** — awaiting contradiction batch verdicts

## Document inventory (delta audit)

| # | Document | Path | Focus | Status |
|---|----------|------|-------|--------|
| 1 | Feature List | `docs/feature-list.md` | F21/F22/F5/F7.h/M4 | statements extracted |
| 2 | Spec | `docs/spec.md` | F5/F7/F21/F22 + overview drift | contradictions open |
| 3 | User Journeys | `docs/user-journeys.md` | UJ-003/004/018/033 + UJ-013/015 | contradictions open |
| 4 | Test Plan | `docs/test-plan.md` | UJ map + legacy TC bodies | contradictions open |
| 5 | API Contract | `docs/api-contract.md` | Auth removed + residual `DISABLE_AUTH` | contradictions open |
| 6 | Env contract | `docs/env-contract.md` | Auth secrets still current | deferral candidate |

## Embedded consistency (EV-017)

| Check | Result | Notes |
|-------|--------|-------|
| Feature ↔ Spec | **Partial** | F21/F22 sections exist; `apps/backend` overview still JWT/auth/work-sessions |
| Feature ↔ Journey | **Pass** (core) | F21→UJ-001/002/004/018; F22→UJ-033; UJ-003 superseded |
| Journey ↔ Test | **Partial** | Map rows for UJ-033 / TC-F22; detailed TC bodies still JWT/`tac_work_sessions` |
| Feature ↔ Test | **Partial** | TC-F22 referenced; TC bodies not fully rewritten |
| Cross-doc naming | **Pass** | IndexedDB / F7.h / R2″ consistent where updated |
| Scope boundaries | **Fail open** | Stale JWT/`DISABLE_AUTH` claims contradict F21 |
| Template `static+api+worker` | **Pass** | F8 worker unchanged; no new deployable |

## Auto-approved (high confidence) — from E17-4A…E17-11

| ID | Statement | Source |
|----|-----------|--------|
| S-EV017.1 | F21 = public unauthenticated operator app | E17-4 / E17-8 |
| S-EV017.2 | F22 = privacy preference center Solution A + GPC | E17-7 / E17-9 |
| S-EV017.3 | F5/F7 history → browser IndexedDB (F7.h); no server ownership | E17-4 / E17-8 |
| S-EV017.4 | Operator M4 Auth deprecated; F8 machine auth remains | E17-4 |
| S-EV017.5 | Legacy Supabase rows: no public API; ~30-day archive | E17-5 |
| S-EV017.6 | Baseline abuse controls in this cycle | E17-6 |
| S-EV017.7 | IndexedDB before JWT/`/auth/*` teardown | E17-10 |
| S-EV017.8 | UI preview deferred to 11-verify-impl | E17-11 |
| S-EV017.9 | UJ-003 superseded; UJ-033 added | 01 corpus + E17-4 |
| S-EV017.10 | Dissemination BYOC remains memory-only (ADR-021/029) | Scope summary |

**Count**: 10 high-confidence auto-approved.

## Open contradictions (user review)

| ID | Category | Evidence | Recommended fix |
|----|----------|----------|-----------------|
| **C-EV017.1** | `[Contradiction]` | `api-contract.md` lint/decode/preview still say `unless DISABLE_AUTH=true` | Change Auth lines to **None (F21 public)** |
| **C-EV017.2** | `[Contradiction]` | `test-plan.md` TC-004 / live E2E still JWT + `tac_work_sessions` + `DISABLE_AUTH=false` | Mark server-session TCs superseded; rewrite TC-004 for IndexedDB; drop login preconditions for public path |
| **C-EV017.3** | `[Contradiction]` | `spec.md` `apps/backend` overview still JWT middleware + work-sessions + `DISABLE_AUTH` | Patch overview to public convert + abuse controls; IndexedDB client history |
| **C-EV017.4** | `[Contradiction]` | UJ-013 “login required for session persist”; UJ-015 “JWT when required” | Amend actors/steps to public + IndexedDB (F21/F7.h) |
| **C-EV017.5** | `[Ambiguity]` | `env-contract.md` still requires `E2E_USER_*` / `DISABLE_AUTH` | **Defer** full rewrite to 04/12; add **stale-until-F21** banner now |
| **C-EV017.6** | `[Contradiction]` | UJ map cites `TC-F22-001..003` / `TC-F21-auth-gone` but bodies missing | Add stub TC sections in `test-plan.md` (objectives + pass criteria) |

## Recommended batch verdict

**Approve recommended fixes for C-EV017.1–4 + C-EV017.6 now; C-EV017.5 = banner + defer to 04/12.**

## Next

Await user batch on contradictions → apply surgical doc fixes → complete product-audit append → handoff Phase A checkpoint / 04-tech-plan.
