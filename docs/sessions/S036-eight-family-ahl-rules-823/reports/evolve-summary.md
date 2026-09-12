# Evolve summary — S036 / EV-029

**Status**: completed (session closed `D-S036-EV029-phase4-close` = 1)  
**PRs**: [#827](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/827) (M1) · [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) merged @ `4e6577a`  
**Issues**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) **closed** · [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740) **closed** · [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) closed (M7)  
**Report**: `docs/evolve-report-EV-029.md`  
**Smoke**: `docs/sessions/S036-eight-family-ahl-rules-823/reports/deploy-smoke.md` — **PASS** (`D-S036-13` = 1)

## Acceptance

1. Coverage matrix eight families × roles — **PASS** (TC-EV029-001)
2. Example inventory TAC + IWXXM peers — **PASS** (TC-EV029-002)
3. Shared AHL/`T1T2`/BBB — **PASS** (TC-EV029-003; M1)
4. TC SIGMET → `TropicalCycloneSIGMET` — **PASS** (#738; residual [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829))
5. VAA/TCA #823 B4 / #820 — **PASS** (M9/M10; decode residual stays on #820)
6. F28 SWXA quality bar — **PASS** (TC-F28-*; #740 closed)
7. Product-order + report-state smoke; #823 closable with children linked — **PASS**

## Stage outcomes

| Stage | Outcome |
|-------|---------|
| 01 / 02 | Delta specs + Gate A |
| 04 | 48-task M0–M12 plan; Gate B |
| 07 | M0–M12 build (AHL → … → SWXA); `tac2iwxxm` 0.2.3 |
| 08–12 | Verify PASS; `D-S036-11` / `D-S036-12` approved |
| 13 | Deploy smoke PASS — H0c/H1/H3/H4/H5 + live SWXA |

## Residuals (open)

| Issue | Note |
|-------|------|
| #829 | TC SIGMET lint pack / STNR / A6-2-TC menu |
| #820 | VAA/TCA decode deepen beyond F9 G4 |
| #831 | Parameterized happy/sad/edge matrices |

## Live

| Surface | Evidence |
|---------|----------|
| API | `dep-d9ntlclbedkc73fvcuvg` · image `…4e6577a` |
| FE | `dep-d9ntlde1egvs738ph9h0` · Examples `swxa_a7_3` / `spacewx-A7-3` |
