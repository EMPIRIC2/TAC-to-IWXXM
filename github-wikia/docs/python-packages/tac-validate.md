# tac-validate

The **tac-validate** package lints Traditional Alphanumeric Code (TAC) aviation
weather products before conversion. The package returns structured issues and
optional fixes.

Supported products include METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA, and
SWXA.

This package does not parse or validate IWXXM XML. The package has no FastAPI or
database dependencies.

## Install

```bash
pip install tac-validate
```

You need Python 3.12 or newer.

## Library

```python
from tac_validate import lint

report = lint("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=", product="METAR")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
    for fix in report.fixes:
        print(fix.code, fix.replacement)
```

## CLI

```bash
tac-validate --product METAR path/to/report.tac
tac-validate --product METAR --json path/to/report.tac
```

Exit code `0` means lint is OK. Exit code `1` means error-severity issues are
present, or the file cannot be read.

## Optional policy files

You can set `TAC_VALIDATE_POLICY_DIR` to a directory of TAC quality policy YAML
files. You can set `TAC_VALIDATE_DETECTOR_DIR` to a directory of detector YAML
files. See the package `examples/` tree for starter files.

## Links

- PyPI: [tac-validate](https://pypi.org/project/tac-validate/)
- Related: [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm), [iwxxm-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-iwxxm-validate)
