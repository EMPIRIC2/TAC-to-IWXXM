# Evolve summary — EV-051 / S060

**Cycle:** EV-051 — Tag-driven prod deploy + full CI Deploy needs  
**Session:** S060-tag-driven-prod-deploy  
**Preset:** Lean+ (`D-S060-route=1`)  
**PR:** [#966](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/966) **MERGED** → `stage` @ `8882856b`  
**Decisions:** `D-S060-merge=1` (continue = merge when CI green)

## Delivered

| Area | Change |
|------|--------|
| CI/CD | `.github/workflows/ci-cd.yml` — widen Deploy `needs`; stop auto Deploy on `main` push; tag + `workflow_dispatch` for prod |
| ADR | ADR-034 amended (solo gate = tag/dispatch) |
| Docs | `docs/deploy.md`, F30 / TC-F30-010 / TC-EV051-* |
| Rules | `doks-promote-from-stage.mdc`, `atomic-commits.mdc`, `ci-after-push.mdc` |

## Acceptance (AC1–AC6)

Met in 11-verify-impl; see `reports/verify-impl.md`.

## Deploy

12/13 waived this cycle. First prod cutover after promote to `main` requires
explicit `vYYYY.MM.DD-deploy` tag (or Actions → Run workflow). Staging should
auto-Deploy from `stage` tip after post-merge full CI.

## Corpus

[Corpus: product §F30] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: tests]
[Corpus: decisions §EV-051]
