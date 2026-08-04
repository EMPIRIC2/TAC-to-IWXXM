# 02-verify-plan audit — S040 / EV-032

**Date**: 2026-08-04  
**Mode**: delta  
**Issues**: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) · [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) · [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741) · [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) · related [#847](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/847)

## Scope audited

`feature-list.md` (F32 + EV-032 deepen) · `spec.md` (F32 / S040) · `user-journeys.md` (UJ-045) ·
`test-plan.md` (TC-EV032 / TC-F32) · `api-contract.md` (`product=vona` + S040 review) ·
`evolve-decisions.md` §EV-032 · session brief / context

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F32 + S040/EV-032 in both |
| Feature ↔ Journey | **PASS** — F32 ↔ **UJ-045**; deepen ↔ UJ-039/034/042 |
| Journey ↔ Test | **PASS** — UJ-045 ↔ TC-F32-001..006 + TC-EV032-001..008 |
| Feature ↔ Test | **PASS** — F32 ↔ TC-F32-*; #835/#808/corpus ↔ TC-EV032-002..005 |
| API ↔ Feature/Spec | **PASS** — additive `product=vona` enum + endpoint review |
| Naming | **PASS** — F32 / UJ-045 / TC-EV032 / TC-F32; alias IDs fixed → 002..005 |
| Scope boundaries | **PASS** — #836 OOS; order #835→#741→#808→corpus |
| Connectivity | **PASS** — H4–H5 when FE VONA / catalog ships |
| Template | **PASS** — static+api+worker; no new deployable |

## Auto-approved (high confidence)

Derived from `D-S040-open` / `D-S040-route` / `D-S040-E32-M`:

1. Epic **#846** umbrella; children #835 / #741 / #808 (+ corpus gaps)
2. New **F32** VONA quality bar + deepen F23 / F4 / F6 / F2 / F13
3. Full product pack + **full F7 VONA surface** (picker + Examples when unlocked)
4. New **UJ-045** + **TC-EV032-001..008** + **TC-F32-001..006**
5. Additive API enum `product=vona` (docs lead; runtime in 07)
6. Exclude metrics UI #836 / workbench epic #840
7. Work order #835 → #741 → #808 → corpus
8. Close 01 → start 02 (`D-S040-E32-M` Q4=1)

## Medium / low confidence — Batch F locked (`D-S040-02-batch-f` = 1,1,1,1)

| ID | Conf | Statement | Decision |
|----|------|-----------|----------|
| S02.M1 | Med | VONA AHL / T1T2 designator detail deferred to **04** (“when known”); specs stay non-binding until then | **1** Approve |
| S02.M2 | Med | Examples unlock is **incremental** — unlock VONA Examples when F32 golden greens (peer VAA/TCA) | **1** Approve |
| S02.M3 | Med | #808 this cycle is **docs + child issues only** (ticket AC; no tooling). Related [#847](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/847) = non-technical staff review of maintainability docs | **1** Approve |
| S02.L1 | Low | Gate A consistency PASS after TC ID alignment | **1** Approve (bundled in Q4) |

## Gate A

**PASS** (`D-S040-02-phase-a` = 1) — 2026-08-04.  
Consistency PASS + Batch F locked → complete **02-verify-plan** → start **04-tech-plan**.
