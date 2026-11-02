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
- [ ] CalVer bumps committed on `stage` (or explicit **none** for docs/infra-only):
      `YYYY.MM.DD` / `YYYY.MM.DD.N` (ADR-043)
- [ ] `docs/CHANGELOG.md` cut with dated section
- [ ] After merge: tag `vYYYY.MM.DD-deploy` on `main` tip and push
- [ ] If publishing: per-package PyPI tags after pypi-release-checklist
      (e.g. `tac-validate-v2026.09.10`)

## Summary

<!-- What is shipping to prod and why -->

## Evaluation metrics (required — broken down, not a single %)

Paste live-tac-eval (or equivalent) figures for the tip being promoted. Do **not**
collapse to one opaque pass rate. Prefer linking a session report under
`~/.cursor/workflow/.../sessions/<id>/reports/` (or a committed summary path).

- [ ] **Lint** — pass/fail counts × severity (error / warn / info); top codes
- [ ] **Convert** — pass/fail counts (and convert-fail share if non-zero)
- [ ] **IWXXM validate** — pass/fail counts (XSD vs Schematron if split)
- [ ] **By product** — METAR / SPECI / TAF / SIGMET(+VA/TC) / other as applicable
- [ ] **By region / profile** (when the eval scoped regions) — top residual pockets
- [ ] **Top Schematron / issue codes** — ranked list with counts (e.g. TAF-7, SIGMET-4)
- [ ] **Promote dispositions** — keep-as-error / prefer-profile / fixed-this-promote /
      deferred (with one-line rationale)
- [ ] **Session / report link** — path or URL to the eval artifact used above

See [docs/deploy.md](../../docs/deploy.md) §Promote · Evaluation metrics and
[docs/guides/promote-eval-metrics.md](../../docs/guides/promote-eval-metrics.md).

## Test plan

- [ ] Staging smoke green for tip SHA
- [ ] Staging gate green on this PR
- [ ] **EV-061 / #1015:** full CI unit jobs (`Test (*)`), `Lint`, `Typecheck`, and
      **`E2E Full (Playwright)`** (not smoke-only) green; see `docs/deploy.md` §Promote table
- [ ] Post-merge: confirm tip CI on `main` green (**Deploy must not run** on bare main push);
      ship prod via `vYYYY.MM.DD-deploy` tag
