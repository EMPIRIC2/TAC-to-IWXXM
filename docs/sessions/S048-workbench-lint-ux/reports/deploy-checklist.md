# Deploy checklist — S048 / EV-040

**Status:** approved for push + PR (D-S048-12 assumed from plan complete-all)  
**Branch:** `evolve/EV-040-workbench-lint-ux` → `main`  
**H4–H5:** required after deploy (UI)

## Checklist

- [x] AC1–AC7 verified (verify-impl.md)
- [x] Targeted tests green
- [x] Push + CI green (tip after FE coverage fix — watch PR #893)
- [x] PR opened — https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/893
- [x] H1/H3/H0c/H4/H5 on current live DOKS (see deploy-smoke.md)
- [ ] Merge to `main` + tip CD re-smoke (explicit approval)
