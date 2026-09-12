# Evolve report — S021 Golden examples UI (F7.g)

- **Cycle**: EV-016
- **Session**: S021-golden-examples-ui
- **Status**: completed (Phase 4 closed — live H4–H5 waived to #781)
- **Scope**: Frontend-only pre-loaded golden examples in FileConverter (TAC / AHL / happy-path
  IWXXM); deepen F7 slice F7.g / #780; no backend / env / DB
- **Stages run**: 00, 01, 02, 04, 07, 08, 09, 10, 11, 13*, 16 (Lean+build; skip 03/05/06/12)
- **ADRs**: none new (ADR-024 modes reused)
- **Deploy**: Code merged to `main` @ `c49f22b` (PR #782). CI pushed
  `ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend,worker}:20260727004311-c49f22b`.
  **Live Render not updated** — still joseph GHCR paths (#781). Live UJ-032 / H4–H5
  **waived** by user (2026-07-27 option 3).
- **GitHub issues**: #780 **closed**; follow-up live smoke owned by **#781**
- **Follow-ups**: Finish EMPIRIC2 rename cutover (#781) then H4–H5 + Examples UI on live FE;
  F7 remains **Planned**; product quality chain (#731…) and #777 after that

## Summary

EV-016 shipped workbench golden examples: typed FE catalog copied from package fixtures,
product-aware Examples control, demo/non-operational labeling, Vitest TC-F7-008 (catalog +
click-to-load). UJ-032 verified at T0 + local UI preview (11-verify-impl). Merge #782 landed
on `main`; production browser proof deferred until Render can pull EMPIRIC2 GHCR images.

## Artifacts changed (high level)

- `apps/frontend` — `fixtures/examples/`, `examplesCatalog`, GoldenExamplesSelect, FileConverter
- Docs: feature-list F7.g; user-journeys UJ-032; test-plan TC-F7-008; context brief
- Session reports under `docs/sessions/S021-golden-examples-ui/`

## Verification

- 08-verify-build: PASS
- 09-qa / 10-e2e: PASS (UJ-032 / TC-F7-008 T0; H4–H5 → 13)
- 11-verify-impl: APPROVED (E16-19)
- 13-deploy-smoke: **WAIVED** live H4–H5 / UJ-032 → #781 (`deploy-smoke.md`)
