# iwxxm-validate

IWXXM XSD + Schematron validation engine (F2 / F13). MIT licensed.

## Usage

```python
from iwxxm_validate import validate

report = validate(xml, iwxxm_version="2023-1", profile="annex3")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
```

Consumes `vendor/schemas/*` read-only. See ADR-015 / ADR-016 / D-S008-T21-sch
(xslt2 Schematron → `SCHEMATRON_SKIPPED` on the lxml path; optional Docker/Saxon via
`IWXXM_VALIDATE_SCHEMATRON_DOCKER=1`).

## Optional native extension (F13)

Default install is pure Python (hatch). The PyO3 crate under `rust/` is built with
maturin when you want the native scaffold (XSD + Schematron hotspots land in later
tasks):

```bash
make build-iwxxm-validate-native
# or: cd packages/iwxxm-validate && uv run maturin develop --manifest-path rust/Cargo.toml --uv
```

Check availability:

```python
from iwxxm_validate import rust_available

assert rust_available()  # True after maturin develop
```
