# Live TAC eval — regression tests

[Corpus: product] [Corpus: tests]

Regressions for cases found by the **live-tac-eval** skill
(`.cursor/skills/live-tac-eval/`). Prefer real staging live-map TAC snippets
(no secrets). CI runs this tree via `pytest tests/bugs`.

## Layout

| Path | Purpose |
|------|---------|
| `test_ca_rvr_slash_before_trend.py` | Product-rule: CA `…FT/N` RVR trend slash |
| `test_unknown_wmo_membership_live.py` | Keep-as-error: concatenated wx / MOD TURB on SIGMET |
| `test_keep_as_error_live_residuals.py` | Anti-soften: `MISSING_*`, `INVALID_PROB` |

Session audit reports (not in git):  
`~/.cursor/workflow/…/sessions/<id>/reports/live-Nd-regression-coverage.md`

## Rules

- Do **not** soften `INVALID_PROB`, invent Europe profiles, or CW* VIS/QNH softens.
- Product-rule fixes are grammar/accept only — not severity remaps.
- New live-eval gaps → add a module here (or waive in the coverage report).
