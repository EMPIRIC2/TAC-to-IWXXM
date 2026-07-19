# iwxxm-validate

IWXXM XSD + Schematron validation engine (F2 / F13). MIT licensed.

## CLI (optional / E10-39)

```bash
iwxxm-validate path/to/report.xml --version 2023-1 --profile annex3
iwxxm-validate path/to/report.xml --json
```

Exit `0` when `report.ok`; `1` on validation or I/O errors.

## Usage

```python
from iwxxm_validate import validate, validate_iwxxm

# lxml path (parity / no rustc)
report = validate(xml, iwxxm_version="2023-1", profile="annex3")

# F13 SDK — prefers Rust (xmloxide) when the extension is built; else lxml
report = validate_iwxxm(xml, iwxxm_version="2023-1", profile="annex3")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
```

Consumes pinned schemas from the **runtime subset** bundled in the wheel
(E10-34 / E10-6): XSD + Schematron + RDF codelists + `externalSchema` + IWXXM-US.
Modelling / translation documentation trees are **not** shipped. In the monorepo,
paths fall back to `vendor/schemas/*` until you sync:

```bash
make sync-iwxxm-validate-schemas
```

See ADR-015 / ADR-016 / D-S008-T21-sch (xslt2 Schematron → `SCHEMATRON_SKIPPED`
on the **lxml** path only). Native `validate_iwxxm` evaluates Schematron via
**xmloxide** (D-S014-T33-crates / E10-46) and does not emit `SCHEMATRON_SKIPPED`.

## Optional native extension (F13)

Default install is pure Python (hatch). The PyO3 crate under `rust/` uses
**xmloxide** 0.4.x for well-formed + XSD + native ISO Schematron:

```bash
make build-iwxxm-validate-native
# or: cd packages/iwxxm-validate && uv run maturin develop --manifest-path rust/Cargo.toml --uv
```

```python
from iwxxm_validate import rust_available, validate_iwxxm

assert rust_available()
report = validate_iwxxm(xml, iwxxm_version="2023-1", levels=("schematron",))
```
