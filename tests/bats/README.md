# Shell script bats suite (EV-080 / #1077)

[Corpus: adr/ADR-007] [Corpus: tests]

**bats-core** tests for every `scripts/**/*.sh`. Layout mirrors `scripts/`
(e.g. `tests/bats/ci/run_metar_quality.bats` → `scripts/ci/run_metar_quality.sh`).

```bash
make test-bats
```

Until Build M4 adds `*.bats` files, the make target prints a scaffold notice and exits 0.
Prefer `--help` / dry-run / mock env — no live credentials (NFR-EV080-006).

Manifest / count guards: TC-EV080-007..008 (Build).
