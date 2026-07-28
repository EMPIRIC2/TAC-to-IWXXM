# 01-requirements report — S023 / EV-017

**Stage**: 01-requirements (delta)  
**Date**: 2026-07-27  
**Features**: F21, F22; deepen F5/F7 (F7.h); deprecate operator M4  
**Issue**: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)  
**Status**: completed (pending user confirm → 02-verify-plan)

## Scope lock (E17-4A … E17-11)

| ID | Decision |
|----|----------|
| E17-4 | F21 + F22; IndexedDB F5/F7; deprecate operator M4 |
| E17-5 | Legacy rows: no public API; ~30-day archive |
| E17-6 | Baseline abuse controls in this cycle |
| E17-7 | Privacy Solution A + settings + notice + GPC |
| E17-8 | Auth model 1 — public + local history |
| E17-9 | No non-essential tracking |
| E17-10 | Local history before auth teardown |
| E17-11 | UI preview → 11-verify-impl |

## Document manifest (delta)

| Doc | Delta |
|-----|-------|
| `docs/feature-list.md` | F21, F22; F5/F7.h/M4; non-goals S023 |
| `docs/spec.md` | F5/F7 IndexedDB; F21/F22 sections |
| `docs/user-journeys.md` | UJ-003 superseded; UJ-001/004/018/019/027; UJ-033 |
| `docs/test-plan.md` | UJ map + H3 auth drop; TC-F22 |
| `docs/api-contract.md` | Auth/work-sessions removed; public convert |
| `docs/decisions/evolve-decisions.md` | Batch 2 + Fn allocation |
| `docs/decisions/requirements-decisions.md` | EV-017 table |
| `docs/context/public-app-privacy.md` | R4–R11 locked |

## Impact analysis (Phase 1)

| Area | Impact |
|------|--------|
| Frontend | Remove auth UX; IndexedDB store; Privacy settings/notice; export/import |
| Backend | Drop JWT deps on public routes; remove `/auth/*` + work-sessions; rate limits |
| packages/auth | Teardown or narrow (ADR) |
| Supabase | Keep for F8/infra as needed; retire operator Auth secrets from required matrix |
| E2E | Retire login journeys; public convert + privacy + local history |
| Dissemination | Still memory-only BYOC; no login prerequisite |
| Docs/env | env-contract, staging secrets, AUTH_SERVICE.md in later milestones |

## ADR (deferred to 04 / early 07)

Public app + local-only history + operator Auth retirement (replaces dual `DISABLE_AUTH` path).

## Next

**02-verify-plan** consistency pass on F21/F22 / UJ-033 / api-contract Auth removal.

## AskQuestion

Unavailable — written interview; recommendations applied per user “Proceed with recommendations”.
