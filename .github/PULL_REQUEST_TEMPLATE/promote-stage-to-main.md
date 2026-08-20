<!--
Use this template when opening PR stage → main (prod promote).
See docs/deploy.md §Promote / §Release checklist. ADR-034.
-->

## Promote `stage` → `main`

- [ ] Tip on `stage` has green **Staging smoke**
- [ ] No feature branch → `main` (head is `stage` only)
- [ ] Staging API `/health` expected green (Staging gate will check)

## Release (recommended)

- [ ] Reviewed publishable package diffs since last `v*-deploy` tag
      (`tac2iwxxm` / `tac-validate` / `iwxxm-validate`)
- [ ] Semver bumps committed on `stage` (or explicit **none** for docs/infra-only)
- [ ] `docs/CHANGELOG.md` cut with dated section
- [ ] After merge: tag `vYYYY.MM.DD-deploy` on `main` tip and push
- [ ] If publishing: per-package PyPI tags after pypi-release-checklist

## Summary

<!-- What is shipping to prod and why -->

## Test plan

- [ ] Staging smoke green for tip SHA
- [ ] Staging gate green on this PR
- [ ] **EV-061 / #1015:** full CI unit jobs (`Test (*)`), `Lint`, `Typecheck`, and
      **`E2E Full (Playwright)`** (not smoke-only) green — see `docs/deploy.md` §Promote table
- [ ] Post-merge: confirm tip CI on `main` green (**Deploy must not run** on bare main push);
      ship prod via `vYYYY.MM.DD-deploy` tag
