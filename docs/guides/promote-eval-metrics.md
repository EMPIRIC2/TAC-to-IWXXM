# Promote evaluation metrics (stage → main)

[Corpus: deploy] [Corpus: tests] [Corpus: product §F6]

When opening a **stage → main** promote PR, include a **broken-down** evaluation
metrics section — not a single opaque percentage. The checklist lives in
[`.github/PULL_REQUEST_TEMPLATE/promote-stage-to-main.md`](../../.github/PULL_REQUEST_TEMPLATE/promote-stage-to-main.md).

## Required breakdown

| Dimension | What to report |
|-----------|----------------|
| Lint | Counts by severity; top issue codes |
| Convert | Pass / fail counts |
| IWXXM validate | Pass / fail (split XSD vs Schematron when available) |
| Product | METAR, SPECI, TAF, SIGMET family, others in scope |
| Region / profile | Only when the eval was region-scoped; top residual pockets |
| Top codes | Ranked Schematron / lint codes with counts |
| Dispositions | keep-as-error · prefer-profile · fixed-this-promote · deferred |
| Provenance | Link to live-tac-eval (or equivalent) session report |

## Sources

Prefer `.cursor/skills/live-tac-eval` session artifacts under
`~/.cursor/workflow/{owner}/{repo}/sessions/<id>/reports/`. Summaries may be
copied into the PR body; do not invent metrics.

## Non-goals

- Softening source-quality `MISSING_*` / related keep-as-error codes to inflate rates
- Europe (or other) blanket region policy without an explicit decision
- Operator-facing copy that embeds planning IDs
