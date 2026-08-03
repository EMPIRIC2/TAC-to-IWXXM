# tac-validate

Lint Traditional Alphanumeric Code (TAC) aviation weather products before conversion.
Returns structured issues (code, severity, span) and optional fixes. MIT licensed.

Supported products: METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA, SWXA.

This package does **not** parse or validate IWXXM XML. It has no FastAPI or database
dependencies.

## Install

```bash
pip install tac-validate
```

Requires Python ≥ 3.12.

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

Exit code `0` when lint is OK; `1` when error-severity issues are present (or the file
cannot be read).

## Rule coverage

METAR, SPECI, and TAF use a full product checklist. SIGMET, AIRMET, VAA, TCA, and SWXA use
structured templates plus coverage gates. The wheel does not ship copyrighted Annex
prose — rules cite external standards only.

When adding or changing a METAR/SPECI lint rule in this monorepo, also update the F29
quality matrices — see [`tests/quality_matrices/AUTHORING.md`](../../tests/quality_matrices/AUTHORING.md)
(TC-F29-007).

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related packages: [`tac2iwxxm`](https://pypi.org/project/tac2iwxxm/),
  [`iwxxm-validate`](https://pypi.org/project/iwxxm-validate/)
