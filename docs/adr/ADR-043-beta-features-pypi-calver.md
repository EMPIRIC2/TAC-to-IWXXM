# ADR-043: Beta feature surfacing + PyPI CalVer / CD TestPyPI

> **Status**: Accepted (EV-1150); **Amended** 2026-11-07 (EV-cd-conjoined-calver-release:
> drop scheduled nightlies; CD on `stage` and `main`; TestPyPI `{CalVer}+test`)  
> **Date**: 2026-09-10 (amend 2026-11-07)  
> **Deciders**: User (evolve intake; CD re-eval Q1–Q5 / R1–R4)  
> **Related**: F12–F14; F16–F19; [ADR-034](ADR-034-doks-staging-promote-from-stage.md); [docs/deploy.md](../deploy.md)  
> **Sessions**: EV-1150-beta-feedback-pypi-calver; EV-cd-conjoined-calver-release

## Context

Dissemination and Send are back in the operator UI (EV-091) but are still early.
Operators need a clear beta signal and a one-click path to file feedback on GitHub.

Publishable packages (`tac-validate`, `iwxxm-validate`, `tac2iwxxm`, plus later
`tac-decoding` / `metar-shared` / `reference-lookup`) use CalVer. EV-1150 added
scheduled TestPyPI nightlies. That cycle also kept prod PyPI tag-driven and rejected
auto-publish on every `main` push. EV-cd-conjoined-calver-release replaces that reject:
stage and prod CD must ship DOKS, GHCR, and PyPI/TestPyPI together under one CalVer, and
must create a GitHub Release on each `main` ship.

## Decision

### A — Beta surfacing + feedback

1. Operator UI marks Dissemination and Send (including Convert&Send and Dissemination ops)
   as beta with plain-language copy and a link to GitHub Issues:
   `https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback`.
2. Operator UI marks Conversion profiles (shell nav + ConversionProfile editor) as beta
   with the same badge and feedback path (EV-beta-ux-export-auth).
3. The Upload to Database toolbar control is removed (EV-beta-ux-export-auth). Operators
   use Disseminate / Convert&Send for outside send. Do not bring the control back without
   beta and acceptance criteria.
4. Root README and GitHub repo About mention beta status and the same feedback path.
5. Issue template `.github/ISSUE_TEMPLATE/beta_feedback.md` + label `beta-feedback`.
6. Agent process: when adding new product features, recommend (AskQuestion first option)
   shipping as beta with Issues feedback wiring; see `.cursor/rules/core/beta-feature-rollout.mdc`.
7. Operator-visible strings must not embed internal doc refs (EV-048).

### B — PyPI CalVer + CD publish (amended)

1. CalVer for publishable packages: `YYYY.M.D` as integers without leading zeros
   (example: `2026.9.10`, not `2026.09.10`). Same-day rebuilds use `YYYY.M.D.N`
   (auto-bump on a second ship the same day). `Cargo.toml` cannot take a fourth numeric
   segment or a raw PEP 440 local label. Map via `bump_calver.pep440_to_cargo_version`
   (EV-ci-runtime-failures): same-day `.N` → `+N`; TestPyPI local `+test` maps to a
   Cargo-safe form in Build (tech-plan). Docs may still say `YYYY.MM.DD` as a date shape.
   Emitted versions drop zero-padding.
2. Tag patterns stay `{package}-v{version}` (examples: `tac-validate-v2026.9.10`,
   `tac-validate-v2026.9.10+test` for TestPyPI).
3. Prod PyPI publishes when `main` CD succeeds. CD creates package tags for packages that
   changed only. Those tags start `pypi-publish.yml` (OIDC). Docs-only or infra-only ships
   skip PyPI but still create one GitHub Release (`vYYYY.M.D[.N]`).
4. Stage / TestPyPI publishes when `stage` CD succeeds. Use the same CalVer with PEP 440
   local segment `+test` (`{CalVer}+test`) for packages that changed only. Trusted Publisher
   Environment `testpypi` on `pypi-publish.yml`.
5. Stop using scheduled soft-fail `pypi-nightly.yml` / `.devN` nightlies for TestPyPI.
   Stop using manual `v*-deploy` tags as the prod DOKS gate (see ADR-034 amend).
6. Existing `0.x` releases remain installable. CalVer is for new releases.

## Consequences

- Trusted Publisher filters on PyPI and TestPyPI must accept CD-created CalVer tags
  (including `+test` locals for TestPyPI).
- Promote PR template and `pypi-package-publish.mdc` cite CalVer and CD-created tags,
  not nightlies.
- ADR-034 and deploy.md: a merge to `main` ships prod DOKS, Release, and PyPI.
- UI tests assert the beta badge and the feedback `href`.
- Agents default new operator surfaces toward beta and feedback unless waived.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Hide Dissemination again | Already restored; beta labeling is clearer |
| Nightly → prod PyPI | Risk of unstable installs |
| Keep scheduled TestPyPI nightlies | Soft-fail and drift from stage CD; operator asked to drop |
| Keep tag-only prod PyPI without main CD | DOKS/GHCR versions diverge from package versions |
| Keep `v*-deploy` as prod gate | Operator asked to drop; main merge is the ship |
| Literal `test.YYYY.M.D` version string | Not PEP 440; use `{CalVer}+test` instead |
| Keep semver | Operator asked for date versioning |

## References

- [Corpus: product] F12–F14, F16–F19, F7.w / F35 (conversion profiles beta), F30  
- [Corpus: tech-spec] / [Corpus: deploy]  
- EV-1150 requirements report; EV-cd-conjoined-calver-release session requirements  
