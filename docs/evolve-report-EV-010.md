# Evolve report — S014 package publish + validation stack (F11–F14)

- **Cycle**: EV-010
- **Session**: S014-package-publish-validation
- **Status**: completed (Phase 4 closed — D-S014-EV010-phase4-close-1)
- **Scope**: Validation stack perf (#703); publish `tac-validate` / `iwxxm-validate` /
  `tac2iwxxm[+validate]` (#698/#699/#693); msgspec HTTP; xsdata; PyPI OIDC + Render 12–13
- **Stages run**: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 16
- **ADRs**: ADR-026 (msgspec HTTP), ADR-027 (xsdata)
- **Deploy**: Render API + frontend-v4-web @ merge `c73e0ad`; T6.6 + close prep on `main` `bed719e` (pushed; CI green)
- **PyPI**: `tac-validate` / `iwxxm-validate` / `tac2iwxxm` **0.1.0** live (token bootstrap); OIDC Trusted Publishers for later tags
- **GitHub issues**: #703, #698, #699, #693 **closed**
- **Follow-ups** (non-blocking): next package bump `0.1.1` for maturin/OIDC tag path; rotate bootstrap token after TP attached
- **CI @ bed719e**: [CI/CD](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29708459114) · [E2E](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29708459110) · [Supabase Sync](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29708459115) — all success

## Summary

EV-010 delivered F11–F14: msgspec high-churn HTTP responses, layer-cost matrix + hard gates,
xsdata IWXXM models, Rust `iwxxm-validate` with process-wide schema cache (E10-35 0.85× PASS),
publishable packages, and a single `pypi-publish.yml` OIDC matrix. Render smokes including
H4–H5 and H6′ UJ-022 passed. Monorepo pending-publisher uniqueness forced a one-time
`PYPI_API_TOKEN` bootstrap for `0.1.0`; subsequent publishes use Trusted Publisher only.

## Artifacts changed (high level)

- `packages/{tac-validate,iwxxm-validate,tac2iwxxm}/` + Rust cache in `iwxxm-validate`
- `apps/backend` msgspec HTTP helper; FE types
- `.github/workflows/pypi-publish.yml`
- Docs: feature-list F11–F14, config/deploy, ADR-026/027, CHANGELOG
- Session reports under `docs/sessions/S014-package-publish-validation/reports/`

## Verification

- 08-verify-build: PASS
- 09-qa: PASS (advisory cleared by live H4–H5)
- 10-e2e: PASS (UJ-022 / DEV-005; UJ-023 via bootstrap)
- 11-verify-impl: APPROVED
- 12-verify-deploy: APPROVED; PR #726 merged
- 13-deploy-smoke: PASS (Render + T6.6 hard gates)
