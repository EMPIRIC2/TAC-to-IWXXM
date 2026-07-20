# Evolve report — S015 METAR lint quality (F15)

- **Cycle**: EV-011
- **Session**: S015-metar-lint-quality
- **Status**: completed (Phase 4 closed — D-S015-EV011-phase4-close-1)
- **Scope**: Maintainable TAC lint issue registry (`info`/`warning`/`error`) + #732 METAR/SPECI
  lint/validate/convert quality bar; deepen F6 convert goldens and F12 METAR/SPECI rules;
  HTTP catalog for workbench UX (E11-31)
- **Stages run**: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 16
- **ADRs**: ADR-028 (tac-validate issue registry)
- **Deploy**: Render API + frontend-v4-web @ merge `b405a96` (CI Deploy `29718764520`);
  smoke report tip `10efcf2` (PR #743)
- **PyPI**: `tac-validate-v0.1.1` **not cut** this close (deferred per E11-25 / close decision)
- **GitHub issues**: #732 **closed**
- **Follow-ups** (non-blocking): tag/publish `tac-validate-v0.1.1`; optional 17-retrospective on
  R1–R8 fixture strategy; F7 remains Planned (F15 smoke only)

## Summary

EV-011 introduced a frozen registry (`issue_registry.py` + `ISSUE_CATALOG.{md,json}`), CI gates
against unknown codes / ad-hoc severity literals, research themes R1–R8 closed in the coverage
matrix, expanded accept/negative fixtures and convert goldens (Annex-3 + iwxxm-us), and a
authenticated catalog API consumed by the workbench for tooltips and a lightweight panel.
Production smokes including H4–H5 and live catalog (35 issues) passed after merge #742.

## Artifacts changed (high level)

- `packages/tac-validate` — registry, product_rules wiring, fixtures, catalog regen script
- `packages/tac2iwxxm` — METAR/SPECI golden expansion + R6/R7 tests
- `apps/backend` — `GET /api/v1/lint-issue-catalog`
- `apps/frontend` — `useLintIssueCatalog`, WorkbenchConsole tooltips/panel
- Docs: feature-list F15, ADR-028, COVERAGE_MATRIX, api-contract, CHANGELOG
- Session reports under `docs/sessions/S015-metar-lint-quality/`

## Verification

- 08-verify-build: PASS
- 09-qa / 10-e2e: PASS (UJ-024 / TC-F15; live H4–H5 at 13)
- 11-verify-impl: APPROVED
- 12-verify-deploy: READY → merge #742
- 13-deploy-smoke: PASS (`deploy-smoke.md`)
