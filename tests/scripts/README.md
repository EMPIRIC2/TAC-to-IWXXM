# Scripts Python coverage harness (EV-080 / #1077)

[Corpus: adr/ADR-007] [Corpus: tests]

Unit tests for `scripts/**/*.py`. Run via:

```bash
make test-coverage-scripts
```

Enforces `--cov=scripts` (plus hyphen-path files) at **100%** line+branch via
`tests/scripts/coveragerc` and `check_per_file_coverage.py --min-pct 100`.

Load hyphen-dir modules with `load_script()` from `conftest.py`.
