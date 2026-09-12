# Evolve summary — S014 / EV-010

> Completed: 2026-07-19 (Phase 4 closed — D-S014-EV010-phase4-close-1)
> Features: F11 (msgspec HTTP + layer matrix + xsdata), F12 (`tac-validate` PyPI),
> F13 (`iwxxm-validate` Rust + Schematron), F14 (`tac2iwxxm[+validate]` + OIDC matrix)
> Branch: `evolve/EV-010-package-publish-validation` → PR [#726](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/726) → `main` @ `c73e0ad`
> Follow-up on `main`: T6.6 schema cache through tip `bed719e` (pushed; CI green)
> PyPI `0.1.0` bootstrap; issues #703/#698/#699/#693 closed
> Orchestrator: 16-evolve

## Outcome

F11–F14 implemented and Render-deployed. Hard publish gates PASS after Rust schema cache.
PyPI projects `tac-validate` / `iwxxm-validate` / `tac2iwxxm` at `0.1.0` created via one-time
API token (monorepo pending-publisher limit); Trusted Publishers on existing projects for
future OIDC tags. Live tag `*-v0.1.0` via GHA skipped (version already published).

## Stage trail

| Stage | Result |
|-------|--------|
| 00–06 | Session + product/tech deltas; ADR-026/027; tooling |
| 07–08 | M1–M5 build; 08-verify-build PASS |
| 09–10 | QA PASS (advisory); E2E UJ-022 / DEV-005 PASS |
| 11 | F11–F14 + journeys approved |
| 12 | Deploy checklist; PR #726 merged |
| 13 | Render H0ci–H5 + H6′ UJ-022 PASS; T6.6 hard gates PASS; UJ-023 via token bootstrap |

## Key decisions

- `D-S014-EV010-t65-approve-A` — T6.5 Render smokes approved
- `D-S014-EV010-t66-lib-gate` option 3 — optimize native to 0.85×
- `D-S014-EV010-t66-close-2` — commit T6.6 on main
- `D-S014-EV010-pypi-bootstrap-3` — API token create projects; TP on existing

## Artifacts

Session reports under `docs/sessions/S014-package-publish-validation/reports/`.
Standing: `docs/evolve-report-EV-010.md`, `docs/CHANGELOG.md`, `docs/deploy-state.md`.
