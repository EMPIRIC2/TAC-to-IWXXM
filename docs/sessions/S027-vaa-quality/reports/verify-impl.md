# 11-verify-impl — S027 / EV-021 (F26 / F27)

> Date: 2026-07-30 · Branch: `evolve/EV-021-vaa-quality` · Tip: `0886093` (+ T6.3 report)  
> Inputs: `verification-report.md` (08), `e2e-report.md` (10), `acceptance-criteria.md`

## UI preview

AskQuestion tool unavailable in this environment. **Offer recorded as pending user reply:**

- Non-deployed local preview of VAA/TCA Examples + convert (not staging/production)?
- Options: Yes / No (approve from reports) / Later / Explain

## Per-criterion status

### F26 — VAA (#736)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| F26.1 | Registry codes | **MET** | `test_tc_f26_v1_vaa.py` |
| F26.2 | Themes V1/V2 | **MET** | TC-F26-004 / TC-F26-006 |
| F26.3 | A7-2 golden | **MET** | TC-F26-002 |
| F26.4 | XSD+SCH | **MET** | TC-F26-003 |
| F26.5 | Theme C1 | **MET** | TC-F26-004 |
| F26.6 | Smoke + catalog | **MET** (H4–H5 → 13) | TC-F26-005; examplesCatalog Vitest |

### F27 — TCA (#737)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| F27.1 | Registry codes | **MET** | `test_tc_f27_t1_tca.py` |
| F27.2 | Themes T1/T2 | **MET** | TC-F27-004 / TC-F27-006 |
| F27.3 | A2-2 golden | **MET** | TC-F27-002 |
| F27.4 | XSD+SCH | **MET** | TC-F27-003 |
| F27.5 | Theme C1 | **MET** | TC-F27-004 |
| F27.6 | Smoke + catalog | **MET** (H4–H5 → 13) | TC-F27-005; examplesCatalog Vitest |

### Deepen

| # | Status | Evidence |
|---|--------|----------|
| F6.f1 | **MET** | TC-F26-002 / TC-F27-002 |
| F12.d1 | **MET** | TC-F26-001 / TC-F27-001 |
| F7.g1 | **MET** (H4–H5 → 13) | catalog unlock Vitest; TC-F7-008 |

## Connectivity waiver (UI)

T0 proves catalog + API smoke in-process. **Browser H4–H5 deferred to T6.5 / 13-deploy-smoke**
(same Lean+build+11 pattern as S026). Recorded in `e2e-report.md`.

## Sign-off table (awaiting user)

| Fn | Reviewer | Date | Result |
|----|----------|------|--------|
| F26 | — | — | pending user |
| F27 | — | — | pending user |
| F6.f / F12 / F7.g | — | — | pending user |

## Recommendation

Approve F26/F27 AC from reports (**option 1**) and proceed to **T6.5 / 13-deploy-smoke**
(API+FE redeploy + H1–H5), unless a local UI preview is requested first.
