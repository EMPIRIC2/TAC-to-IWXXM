# tac2iwxxm

The **tac2iwxxm** package converts Traditional Alphanumeric Code (TAC) aviation
weather reports to IWXXM XML.

Supported products include METAR, SPECI, TAF, SIGMET, AIRMET, VAA, and TCA. The
package has no FastAPI or database dependencies.

## Install

```bash
# Convert only
pip install tac2iwxxm

# Convert + TAC lint + IWXXM XSD/Schematron
pip install 'tac2iwxxm[validate]'
```

The `[validate]` extra installs `tac-validate` and `iwxxm-validate`. Conversion
works without that extra.

You need Python 3.12 or newer.

## Convert

```python
from tac2iwxxm import convert

result = convert(
    "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
    product="METAR",
)
assert result.ok and result.xml
```

## Lint and validate with the extra

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

Optional Rust helpers can build from a git checkout. Pure Python is the default
install path. See the package README in the source repository for build
commands.

## Links

- PyPI: [tac2iwxxm](https://pypi.org/project/tac2iwxxm/)
- Related: [tac-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-validate), [iwxxm-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-iwxxm-validate),
  [tac-decoding](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-decoding)
