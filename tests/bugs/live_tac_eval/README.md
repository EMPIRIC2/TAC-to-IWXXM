# Live TAC eval — regression tests

[Corpus: product] [Corpus: tests]

Regressions for cases found by the **live-tac-eval** skill
(`.cursor/skills/live-tac-eval/`) and the Sep 2026 Downloads two-week dump.
Prefer real staging live-map / dump TAC snippets (no secrets; raw dumps not
committed). CI runs this tree via `pytest tests/bugs`.

## Layout

| Path | Purpose |
|------|---------|
| `helpers.py` | Shared `body_tac`, `lint_annex3`, issue assert helpers |
| `fixtures/downloads_two_week.py` | Minimal TAC snippets + param tables |
| `test_downloads_two_week_failure_modes.py` | `MISSING_VISIBILITY` keep-as-error |
| `test_downloads_two_week_success_modes.py` | VCSH/VCTS/TS, MKJP `////`, clean reports |
| `test_ca_rvr_slash_before_trend.py` | Product-rule: CA `…FT/N` RVR trend slash |
| `test_ws_runway_not_invalid_rvr.py` | Product-rule: `WS R14R` wind-shear runway ≠ RVR |
| `test_unknown_wmo_membership_live.py` | Keep-as-error: concatenated wx / MOD TURB on SIGMET |
| `test_keep_as_error_live_residuals.py` | Anti-soften: `MISSING_*`, `INVALID_PROB` |

Session audit reports (not in git):  
`~/.cursor/workflow/…/sessions/<id>/reports/live-Nd-regression-coverage.md`  
`~/.cursor/workflow/…/sessions/EV-downloads-test-result-regressions/reports/downloads-inventory.md`

## Rules

- Do **not** soften `INVALID_PROB`, invent Europe profiles, or CW* VIS/QNH softens.
- Do **not** soften `MISSING_*` / CW* VIS/QNH / `INVALID_PROB` for dump residuals.
- Product-rule fixes are grammar/accept only — not severity remaps.
- New live-eval gaps → add a module here (or waive in the coverage report).
- Convert/validate-only dump rows (AIRPORT_ICAO, year dating, SIGMET AHL) stay
  waived in the session inventory unless a lint code exists.
