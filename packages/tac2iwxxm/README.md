# tac2iwxxm

General TAC → IWXXM converter package (F6 / F14). MIT licensed.

See ADR-013 / ADR-014 / ADR-016 / ADR-017.

## Install

```bash
# Convert only (no validators)
pip install tac2iwxxm

# Convert + TAC lint + IWXXM XSD/Schematron (F14)
pip install 'tac2iwxxm[validate]'
```

The `[validate]` extra depends on **`tac-validate`** and **`iwxxm-validate`** (E10-20).
Convert works without the extra.

```python
from tac2iwxxm import convert

result = convert(
    "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
    product="METAR",
)
assert result.ok and result.xml
```

With `[validate]` installed:

```python
from tac_validate import lint
from iwxxm_validate import validate_iwxxm

assert lint(tac, product="METAR").ok
assert validate_iwxxm(result.xml, iwxxm_version="2025-2").ok
```

## Native extension (PyO3)

Optional Rust hotspots live under `rust/` and import as `tac2iwxxm._rust`
(ADR-017). Pure Python remains the default `uv sync` path.

```bash
# requires rustc + maturin
make build-tac2iwxxm-native
make test-tac2iwxxm-native
```
