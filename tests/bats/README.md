# Shell script bats suite (EV-080 / #1077)

[Corpus: adr/ADR-007] [Corpus: tests]

**bats-core** tests for every `scripts/**/*.sh`. Layout mirrors `scripts/`.

```bash
make test-bats
```

Helpers/stubs: `tests/bats/helpers/bin/` (no live credentials — NFR-EV080-006).  
Manifest: `tests/bats/MANIFEST.md` (TC-EV080-008).
