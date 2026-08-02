# 02-verify-plan audit — S036 / EV-029

**Date**: 2026-08-01  
**Mode**: delta  
**Issue**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823)

## Scope audited

`feature-list.md` (F28 + EV-029 deepen) · `spec.md` (F28 / S036) · `user-journeys.md` (UJ-043) ·
`test-plan.md` (TC-EV029 / TC-F28) · `api-contract.md` (`product=swxa`) ·
`evolve-decisions.md` §EV-029 · session brief / context

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F28 + S036/EV-029 in both |
| Feature ↔ Journey | **PASS** — F28 + deepen ↔ **UJ-043** |
| Journey ↔ Test | **PASS** — UJ-043 ↔ TC-EV029-001..008 + TC-F28-001..006 |
| Feature ↔ Test | **PASS** — F28 ↔ TC-F28-*; deepen ↔ TC-EV029-* |
| API ↔ Feature/Spec | **PASS** — additive `product=swxa`; TC SIGMET under `sigmet` |
| Naming | **PASS** — SWXA / `swxa` / `iwxxm:SpaceWeatherAdvisory` consistent; no `swx` alias |
| Scope boundaries | **PASS** — SIGWX/VONA/QVACI OOS; sink UI OOS; #806 OOS |
| F23 deepen vs Done | **PASS** — Done for gen/VA; TC SIGMET added via EV-029 / #738 |
| Connectivity | **PASS** — H4–H5 only via TC-EV029-008 / TC-F28-005 when FE ships; no new origins |
| Template | **PASS** — static+api+worker; no new deployable |

## Auto-approved (high confidence) — 14

Derived from `D-S036-open` / `D-S036-fn` / `D-S036-E29-M`:

1. Umbrella #823 = mine-then-implement eight-family lint/convert/IWXXM-validate
2. Phase A then Phase B product order: AHL/COM → METAR → SPECI → TAF → SIGMET×3/CNL → AIRMET → VAA → TCA → SWXA
3. New **F28** SWXA quality bar + deepen F6/F12/F2/F13/F15/F20/F23/F24/F26/F27
4. Absorb #738 / #820 / #740 into this cycle
5. Shared AHL/`T1T2`/filename in-cycle; dissemination drawer UI out
6. Standard routing (skip 03/05/06)
7. UI N/A this session
8. New **UJ-043** + **TC-EV029-001..008** + **TC-F28-001..006**
9. Exclude SIGWX / VONA / QVACI as TAC converter inputs
10. Target IWXXM **2025-2** vendor pin
11. Additive API **`product=swxa`** (Manifest Q1=2)
12. TC SIGMET selected under existing `product=sigmet` (no `tc_sigmet` enum)
13. No `swx` wire alias
14. Close 01 → start 02 (`D-S036-E29-M` Q2=1)

## Medium / low confidence — pending user Batch F

| ID | Conf | Statement | Recommendation |
|----|------|-----------|----------------|
| S02.M1 | Med | Runtime enum enforcement for `swxa` lands in **07-build** (backend + packages); docs lead until then — 02 does not require code green yet | **1** Approve |
| S02.M2 | Med | TC SIGMET quality (#738) is **F23 deepen** (not a new Fn); acceptance tracked under TC-EV029-004 + F23 suite deepen | **1** Approve |
| S02.M3 | Med | Phase A mining may open **child issues** for residual encode gaps; umbrella #823 stays open until children linked or closed | **1** Approve |
| S02.L1 | Low | Official SWXA golden peer may be `wmoReference` (not ADR-032 equality) in v1 if vendor TAC↔XML parity is incomplete — defer equality via child | **1** Approve (prefer equality when peer exists) |

## Gate A

Pending Batch F + AskQuestion.
)
