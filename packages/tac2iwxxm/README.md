# tac2iwxxm

Convert Traditional Alphanumeric Code (TAC) aviation weather reports to IWXXM XML.
MIT licensed.

Supports METAR, SPECI, TAF, SIGMET, AIRMET, VAA, and TCA. This library has no FastAPI
or database dependencies.

## Install

```bash
# Convert only
pip install tac2iwxxm

# Convert + TAC lint + IWXXM XSD/Schematron
pip install 'tac2iwxxm[validate]'
```

The `[validate]` extra installs [`tac-validate`](https://pypi.org/project/tac-validate/)
and [`iwxxm-validate`](https://pypi.org/project/iwxxm-validate/). Conversion works without
the extra.

Requires Python ≥ 3.12.

## Convert

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

## Decode and bulletins

```python
from tac2iwxxm import decode_tac, split_bulletin

decoded = decode_tac(tac, product="METAR")
parts = split_bulletin(bulletin_text)
```

## Optional native extension

Optional Rust helpers live under `rust/` and import as `tac2iwxxm._rust`. Pure Python is
the default install path.

```bash
# from a git checkout (requires rustc + maturin):
make build-tac2iwxxm-native
make test-tac2iwxxm-native
```

When adding or changing a METAR/SPECI encode theme in this monorepo, also update the F29
quality matrices — see [`tests/quality_matrices/AUTHORING.md`](../../tests/quality_matrices/AUTHORING.md)
(TC-F29-007).

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- PyPI: [tac2iwxxm](https://pypi.org/project/tac2iwxxm/)
