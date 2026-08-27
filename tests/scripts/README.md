# Scripts Python coverage harness (EV-080 / #1077)

[Corpus: adr/ADR-007] [Corpus: tests]

Unit tests for `scripts/**/*.py`. Run via:

```bash
make test-coverage-scripts
```

Until Build M4 adds collected `test_*.py` files here, the make target prints a scaffold
notice and exits 0. After tests land: `--cov=scripts --cov-fail-under=100` +
`check_per_file_coverage.py --min-pct 100`.

Do not raise package/app `fail_under` floors in this tree — those flip in M2 after fills.
