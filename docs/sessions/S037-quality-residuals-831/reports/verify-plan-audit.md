# 02-verify-plan audit — S037 / EV-030

**Date**: 2026-08-02  
**Mode**: delta  
**Issues**: [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) · [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) · [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820)

## Scope audited

`feature-list.md` (F29 + EV-030 deepen) · `spec.md` (F29 / S037) · `user-journeys.md` (UJ-044) ·
`test-plan.md` (TC-EV030 / TC-F29) · `api-contract.md` (S037/EV-030 endpoint review) ·
`evolve-decisions.md` §EV-030 · session brief / context

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F29 + S037/EV-030 in both |
| Feature ↔ Journey | **PASS** — F29 + deepen ↔ **UJ-044** |
| Journey ↔ Test | **PASS** — UJ-044 ↔ TC-EV030-001..006 + TC-F29-001..007 |
| Feature ↔ Test | **PASS** — F29 ↔ TC-F29-*; #829/#820 ↔ TC-EV030-004..006 |
| API ↔ Feature/Spec | **PASS** — no new product enum; catalog tier + lint codes + decode deepen |
| Naming | **PASS** — F29 / UJ-044 / TC-EV030 / TC-F29 consistent |
| Scope boundaries | **PASS** — #830/#806/SIGWX/VONA/QVACI OOS; work order #831→#829→#820 |
| F23/F9 Done vs deepen | **PASS** — Done bars retained; deepen rows for #829/#820 |
| Connectivity | **PASS** — H4–H5 only via TC-EV030-005 when FE catalog unlock ships |
| Template | **PASS** — static+api+worker; no new deployable |

## Auto-approved (high confidence)

Derived from `D-S037-open` / `D-S037-fn` / `D-S037-E30-M`:

1. Residuals #831 → #829 → #820 in one Standard evolve cycle
2. New **F29** rule matrices + deepen F23/F12/F2/F13/F9/F26/F27
3. UI preview declined; H4–H5 only if FE menu unlock ships
4. New **UJ-044** + **TC-EV030-001..006** + **TC-F29-001..007**
5. No new product enum; TC SIGMET stays under `product=sigmet`
6. API amend documents #829 catalog tier + lint catalog codes + #820 decode deepen
7. F29 v1 is CI/pytest harness (no new public routes)
8. Design-before-bulk for #831 (eval questions before flooding fixtures)
9. Exclude #830 Supabase strip, #806 WIS2, SIGWX/VONA/QVACI
10. Close 01 → start 02 (`D-S037-E30-M` Q2=1)

## Medium / low confidence — Batch F (*pending AskQuestion*)

| ID | Conf | Statement | Options |
|----|------|-----------|---------|
| S02.M1 | Med | #831 pilot product set is **METAR/SPECI** lint+encode+validate first; other products inventory-gated | 1 Approve / 2 Expand pilot / 3 Explain |
| S02.M2 | Med | #829 STNR/geometry may be **explicit OOS with cite** if encode engine work is out of cycle | 1 Approve / 2 Require STNR fixtures / 3 Explain |
| S02.M3 | Med | #820 may leave a **child residual** if official peers cannot reach `residuals == []` this cycle | 1 Approve / 2 Require empty residuals / 3 Explain |
| S02.L1 | Low | #831 harness shape may be **session design note** (not full ADR) unless 04 needs standing ADR | 1 Approve / 2 Require ADR / 3 Explain |

## Gate A

*Pending Batch F + Gate A AskQuestion.*
