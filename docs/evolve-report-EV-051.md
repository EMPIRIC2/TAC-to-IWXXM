# Evolve report — EV-051

**Session:** S060-tag-driven-prod-deploy  
**Completed:** 2026-08-09  
**PR:** [#966](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/966) → `stage` @ `8882856b`  
**Summary:** [docs/sessions/S060-tag-driven-prod-deploy/reports/evolve-summary.md](sessions/S060-tag-driven-prod-deploy/reports/evolve-summary.md)

## Outcome

F30 deepen: Deploy `needs` include full CI (+ `e2e-smoke`); staging still
auto-Deploys after those needs on `stage`; prod Deploy no longer runs on `main`
push — only on `vYYYY.MM.DD-deploy` tag (`v*-*-deploy`) or optional
`workflow_dispatch`. ADR-034, deploy docs, promote rules, and TC-F30-010 amended.

## Stages

Lean+ completed: `00 → 16 → 01 → 02 → 03 → 07 → 08 → 09 → 11`.  
Skipped/waived: `04`, `05`, `06`, `10`, `12`, `13`.

## Corpus

[Corpus: product §F30] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: tests]
[Corpus: decisions §EV-051]
