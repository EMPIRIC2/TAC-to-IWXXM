# Evolve summary — EV-038 / S046 (Epic #846 corpus residuals)

> Date: 2026-08-06  
> Status: **completed** (`D-S046-13` = 1 — approve 13 / close)  
> Merge: [#890](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/890) @ `619a7ac3`  
> DOKS: `20260806144346-619a7ac` · CI Deploy [31112016561](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31112016561)  
> Features: deepen **F2 / F4 / F6 / F7 / F32** — no new Fn  
> Epic: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) **CLOSED** (children #849–#861 closed)

## What shipped

1. **M1 docs/process** — OOS / modelling watch / deprecation template (#858/#861/#855)
2. **M2 release-line** — Python SoT → committed JSON → FE Latest/Previous picker + OpenAPI/CI drift (#851–#854); UJ-050
3. **M3 soft gates** — codelist URI drift CI; translation-failed inventory; SWXA A7-4/A7-5 unlock (#859/#860/#857)
4. **M4 encode** — VONA vertical extent; RESUSPENDED cite-only deferral; VA-EGGX → `wmoPass` (#849/#850/#856)

## Stages

| Stage | Result |
|-------|--------|
| 00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13 | **completed** |
| 03 / 06 | **skipped** |
| Gates A→B / B→C / C→D / Deploy | **passed** |

## Live proof (13)

| Item | Value |
|------|-------|
| Merge | #890 @ `619a7ac3` |
| CI Deploy | [31112016561](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31112016561) **success** |
| Tag | `20260806144346-619a7ac` |
| H1–H3 | `/health` 200 · live API **20 passed**, 1 skipped |
| H0c / H4 / H5 | **6 / 2 / PASS** (`config.json` → `api.tac-to-iwxxm.com`) |
| UJ-050 | Live App chunk SoT + `Latest`/`Previous` labels |

## Artifacts

- `reports/01-requirements-summary.md` … `verify-impl.md` · `deploy-checklist.md` · `deploy-smoke.md`
- `reports/execution-plan.md` · `routing-plan.md` · `session-brief.md`
- Decisions: [evolve-decisions.md §EV-038](../../../decisions/evolve-decisions.md)

## Follow-ups

- Land `scripts/deploy/verify_connectivity.sh` bash 3.2 / `set -u` empty-array fix on `main` (used for this H4–H5 run)
- No remaining #846 children open

## Decisions (close)

| ID | Choice |
|----|--------|
| D-S046-13 | **1** — approve 13-deploy-smoke and close EV-038 / S046 |
