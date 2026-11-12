<!--
Use this template when opening a pull request from the `stage` Git branch to the
`main` Git branch (production promote).
See docs/deploy.md §Promote / §Release checklist.
-->

## Promote `stage` → `main`

- [ ] The tip commit on the `stage` branch has a green **Staging smoke** check
- [ ] This pull request does not promote a feature branch into `main` (the head
      branch is `stage` only)
- [ ] Staging API `/health` is expected green (the Staging gate will check)

## Release (recommended)

- [ ] Reviewed publishable package diffs since the last `v*-deploy` tag
      (`tac2iwxxm` / `tac-validate` / `iwxxm-validate`)
- [ ] Calendar version (CalVer) bumps committed on `stage`, or an explicit
      **none** note for docs-only or infra-only changes:
      `YYYY.MM.DD` / `YYYY.MM.DD.N`
- [ ] `docs/CHANGELOG.md` cut with a dated section
- [ ] After merge: tag `vYYYY.MM.DD-deploy` on the `main` tip commit and push
      the tag
- [ ] If publishing to PyPI: per-package PyPI tags after the pypi-release
      checklist (for example `tac-validate-v2026.09.10`)

## Summary

<!-- What is shipping to production and why -->

## Evaluation metrics (required — broken down, not a single percent)

Paste live-TAC evaluation (or equivalent) figures for the tip commit being
promoted. Do **not** collapse the figures into one opaque pass rate. Prefer
linking a session report under
`~/.cursor/workflow/.../sessions/<id>/reports/` (or a committed summary path).

- [ ] **Lint** — pass/fail counts by severity (error / warn / info); top codes
- [ ] **Convert** — pass/fail counts (and convert-fail share if non-zero)
- [ ] **IWXXM validate** — pass/fail counts (XSD vs Schematron if split)
- [ ] **By product** — METAR / SPECI / TAF / SIGMET (+ volcanic ash / tropical
      cyclone) / other as applicable
- [ ] **By region / profile** (when the evaluation scoped regions) — top residual
      pockets
- [ ] **Top Schematron / issue codes** — ranked list with counts (for example
      TAF-7, SIGMET-4)
- [ ] **Promote dispositions** — keep-as-error / prefer-profile /
      fixed-this-promote / deferred (with a one-line rationale)
- [ ] **Session / report link** — path or URL to the evaluation artifact used
      above

See [docs/deploy.md](../../docs/deploy.md) §Promote · Evaluation metrics and
[docs/guides/promote-eval-metrics.md](../../docs/guides/promote-eval-metrics.md).

## Test plan

- [ ] Staging smoke green for the tip commit SHA
- [ ] Staging gate green on this pull request
- [ ] Full CI unit jobs (`Test (*)`), `Lint`, `Typecheck`, and
      **`E2E Full (Playwright)`** (not smoke-only) green; see `docs/deploy.md`
      §Promote table
- [ ] After merge: confirm tip CI on `main` is green (**Deploy must not run** on
      a bare `main` push); ship production with a `vYYYY.MM.DD-deploy` tag
