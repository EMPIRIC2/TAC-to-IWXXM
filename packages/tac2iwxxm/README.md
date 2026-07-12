# tac2iwxxm

General TAC → IWXXM converter package (F6). MIT licensed.

See ADR-013 / ADR-014 / ADR-016 / ADR-017.

## Native extension (PyO3)

Optional Rust hotspots live under `rust/` and import as `tac2iwxxm._rust`
(ADR-017). Pure Python remains the default `uv sync` path.

```bash
# requires rustc + maturin
make build-tac2iwxxm-native
make test-tac2iwxxm-native
```
