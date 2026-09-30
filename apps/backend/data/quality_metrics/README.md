# Quality metrics corpus artifact

Precomputed official WMO IWXXM corpus quality data for the operator **Quality
metrics** tab (public `GET /api/v1/quality-metrics*`).

## File

- `corpus_metrics.json` — list summaries + file rows + per-stem `details`

## Regenerate

From the repository root (requires workspace packages: `tac2iwxxm`,
`tac-validate`, `iwxxm-validate`, `metar-shared`):

```bash
make generate-quality-metrics
# equivalent: uv run python scripts/ci/generate_quality_metrics.py
```

Re-run when the official TAC inventory, annex3 goldens, vendor IWXXM pin, or
encode/lint/validate engines change in a way that affects corpus diagnostics.
CI verifies that the committed metrics content still matches a fresh local
regeneration, while ignoring the timestamp-only `generated_at` field.

Do **not** hand-edit match/residual/lint/validate fields — regenerate instead.

## Count honesty

[Corpus: product §F7.q] [Corpus: api] [Corpus: tests]

- Deferred stems increment `deferred_gaps` only. They are not unpaired examples and they
  are not mismatches.
- `match_fail` counts non-deferred rows whose `match_status` is not `equal` (a convert
  failure is a mismatch with the official example).
- `residual_nonempty` counts leftover TAC spans whose text is non-blank.
- `validate_fail` counts error-severity findings after XPath-engine errors
  (`SCHEMATRON_XPATH_UNSUPPORTED`, messages that start with `XPath error`) and
  `SCHEMA_IMPORT_WARNING` are dropped. The operator detail pane hides the same noise
  even when an older artifact still contains it. The next `make generate-quality-metrics`
  writes the filtered issues into this file.
- `generated_at` and `iwxxm_pin` stay on the artifact and the API. The operator page
  subtitle does not display them. Regenerating this file must not change the product
  default IWXXM pin.
