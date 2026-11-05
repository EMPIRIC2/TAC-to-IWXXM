# iwxxm-validate

The **iwxxm-validate** package makes sure that IWXXM XML is well-formed and
meets XSD and Schematron rules.

Pinned schema snapshots ship inside the wheel. This package does not parse TAC
text.

## Install

```bash
pip install iwxxm-validate
```

You need Python 3.12 or newer. The default wheel is pure Python (`lxml`). An
optional Rust extension can speed validation when you build from source.

## Start here

| Goal | Import |
|------|--------|
| Validate IWXXM XML (XSD and Schematron) | `from iwxxm_validate import validate` |
| Prefer the Rust engine when built | `from iwxxm_validate import validate_iwxxm, rust_available` |
| Compare two IWXXM documents and ignore formatting | `from iwxxm_validate import to_canonical_xml, canonical_xml_equal` |

Canonical XML means W3C Canonical XML 1.0 (also called C14N).

## Library

```python
from iwxxm_validate import validate, validate_iwxxm

report = validate(xml, iwxxm_version="2023-1", profile="annex3")

report = validate_iwxxm(xml, iwxxm_version="2023-1", profile="annex3")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
```

Common version lines include `2023-1` and `2025-2`. Profile `annex3` is the
default ICAO Annex 3 path.

## CLI

```bash
iwxxm-validate path/to/report.xml --version 2023-1 --profile annex3
iwxxm-validate path/to/report.xml --json
```

## Links

- PyPI: [iwxxm-validate](https://pypi.org/project/iwxxm-validate/)
- Related: [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm), [tac-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-validate)
