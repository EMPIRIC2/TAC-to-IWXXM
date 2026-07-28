# 02-verify-plan report — S023 / EV-017

**Stage**: 02-verify-plan (delta)  
**Date**: 2026-07-27  
**Features**: F21, F22; deepen F5/F7 (F7.h); deprecate operator M4  
**Issue**: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)  
**Gate**: User **A** — run 02 (`D-S023-02-verify-plan-gate-A`)  
**Contradiction batch**: User **A** — `D-S023-02-C-EV017-A`  
**Status**: **completed** (Phase A corpus consistency)

## Document inventory (delta audit)

| # | Document | Path | Focus | Status |
|---|----------|------|-------|--------|
| 1 | Feature List | `docs/feature-list.md` | F21/F22/F5/F7.h/M4 | complete (01 deltas) |
| 2 | Spec | `docs/spec.md` | F5/F7/F21/F22 + overview drift | **fixed** (C3) |
| 3 | User Journeys | `docs/user-journeys.md` | UJ-003/004/018/033 + UJ-013/015 | **fixed** (C4) |
| 4 | Test Plan | `docs/test-plan.md` | UJ map + TC bodies + stubs | **fixed** (C2, C6) |
| 5 | API Contract | `docs/api-contract.md` | Auth removal residual | **fixed** (C1) |
| 6 | Env contract | `docs/env-contract.md` | Auth secrets still current | **banner** (C5) — rewrite 04/12 |

## Embedded consistency (EV-017) — after fixes

| Check | Result | Notes |
|-------|--------|-------|
| Feature ↔ Spec | **Pass** | Backend/frontend overview aligned to F21 public + IndexedDB |
| Feature ↔ Journey | **Pass** | F21→UJ-001/002/004/018; F22→UJ-033; UJ-003 superseded |
| Journey ↔ Test | **Pass** | TC-004 IndexedDB; TC-F21-auth-gone; TC-F22-001..003 stubs |
| Feature ↔ Test | **Pass** | Stub TCs present; detailed steps in 04 |
| Cross-doc naming | **Pass** | IndexedDB / F7.h / R2″ |
| Scope boundaries | **Pass** | Stale JWT claims removed or marked historical |
| Template `static+api+worker` | **Pass** | F8 worker unchanged |

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

## Contradictions — resolved (`D-S023-02-C-EV017-A`)

| ID | Verdict | Action taken |
|----|---------|--------------|
| C-EV017.1 | modified | lint/decode/catalog/dissemination Auth → **None (F21 public)** |
| C-EV017.2 | modified | TC-003 retired; TC-004 + live E2E → IndexedDB / no JWT; TC-F7-005 local |
| C-EV017.3 | modified | `apps/backend` + frontend overview, UI overlay, Security → public + abuse + IndexedDB |
| C-EV017.4 | modified | UJ-013/015/017/020/022 → public + IndexedDB |
| C-EV017.5 | deferred | `env-contract.md` **stale-until-F21** banner; full rewrite 04/12 |
| C-EV017.6 | modified | Added `TC-F21-auth-gone` + `TC-F22-001..003` stubs |

## Results

| Metric | Count |
|--------|-------|
| Documents audited | 6 |
| Auto-approved (high) | 10 |
| Contradictions found | 6 |
| Contradictions resolved now | 5 (C1–4, C6) |
| Deferred | 1 (C5 env full rewrite) |

## Next

Phase A checkpoint (Standard) → AskQuestion proceed to **04-tech-plan** (03 skipped per routing).
)
