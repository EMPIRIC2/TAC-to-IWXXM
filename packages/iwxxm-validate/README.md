# iwxxm-validate

Validate IWXXM XML: well-formedness, XSD, and Schematron. MIT licensed.

Pinned schema snapshots ship inside the wheel (XSD, Schematron, RDF codelists, and
related runtime assets). This package does **not** parse TAC text.

## Install

```bash
pip install iwxxm-validate
```

Requires Python ≥ 3.12. The default wheel is pure Python (lxml). An optional Rust
extension speeds up validation when built from source (see below).

## Library

```python
from iwxxm_validate import validate, validate_iwxxm

# Pure-Python path (lxml)
report = validate(xml, iwxxm_version="2023-1", profile="annex3")

# Prefer native Rust when available; otherwise falls back to lxml
report = validate_iwxxm(xml, iwxxm_version="2023-1", profile="annex3")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
```

Common version lines include `2023-1` and `2025-2`. Profile `annex3` is the default ICAO
Annex 3 path; IWXXM-US is available when that schema set is present in the wheel.

## CLI

```bash
iwxxm-validate path/to/report.xml --version 2023-1 --profile annex3
iwxxm-validate path/to/report.xml --json
```

Exit `0` when `report.ok`; `1` on validation or I/O errors.

## Optional native extension

Default `pip install` is pure Python. Building the PyO3 extension (requires `rustc` and
`maturin`) enables faster well-formed + XSD + Schematron evaluation:

```bash
# from a git checkout of the monorepo:
make build-iwxxm-validate-native
```

```python
from iwxxm_validate import rust_available, validate_iwxxm

assert rust_available()
report = validate_iwxxm(xml, iwxxm_version="2023-1", levels=("schematron",))
```

On the pure-Python path, some Schematron dialects may be reported as skipped; the native
path evaluates Schematron in-process and does not emit that skip.

When adding or changing METAR/SPECI Schematron-facing coverage in this monorepo, also
update the F29 quality matrices — see
[`tests/quality_matrices/AUTHORING.md`](../../tests/quality_matrices/AUTHORING.md)
(TC-F29-007).

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related packages: [`tac-validate`](https://pypi.org/project/tac-validate/),
  [`tac2iwxxm`](https://pypi.org/project/tac2iwxxm/)
