# Quality metrics corpus artifact

Precomputed official WMO IWXXM corpus quality data for the operator **Quality
metrics** tab (public `GET /api/v1/quality-metrics*`).

## File

- `corpus_metrics.json` — list summaries + file rows + per-stem `details`

## Regenerate

From the repository root (requires workspace packages: `tac2iwxxm`,
`tac-validate`, `iwxxm-validate`, `metar-shared`):

```bash
uv run python scripts/ci/generate_quality_metrics.py
```

Re-run when the official TAC inventory, annex3 goldens, vendor IWXXM pin, or
encode/lint/validate engines change in a way that affects corpus diagnostics.

Do **not** hand-edit match/residual/lint/validate fields — regenerate instead.
