# Python packages example

This example shows lint, convert, validate, and decode for one METAR in a local
Python environment.

## Goal

Install the packages, convert the sample TAC to IWXXM XML, and make sure that
lint and validate reports are acceptable.

## Sample TAC

```text
METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=
```

## Before you start

1. Install Python 3.12 or newer.
2. Open a shell in an empty working directory.
3. Create a virtual environment if your organization requires one.

## Steps

1. Install convert with the validate extra.
2. Lint the sample TAC with `tac-validate`.
3. Convert the sample TAC with `tac2iwxxm`.
4. Validate the IWXXM XML with `iwxxm-validate`.
5. Decode the sample TAC with `tac-decoding` when you want plain language.
6. Write the XML to a file for your local archive procedure.

## Install

```bash
pip install 'tac2iwxxm[validate]' tac-decoding
```

The `[validate]` extra installs `tac-validate` and `iwxxm-validate`.

## Full example

```python
from pathlib import Path

from tac_validate import lint
from tac2iwxxm import convert
from iwxxm_validate import validate_iwxxm
from tac_decoding import decode_tac

tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="

lint_report = lint(tac, product="METAR")
assert lint_report.ok, lint_report.issues

result = convert(tac, product="METAR")
assert result.ok and result.xml

val_report = validate_iwxxm(result.xml, iwxxm_version="2025-2")
assert val_report.ok, val_report.issues

decoded = decode_tac(tac, product="METAR")
print(decoded.summary)

Path("kjfk-metar.xml").write_text(result.xml, encoding="utf-8")
print("wrote kjfk-metar.xml")
```

## What you should see

| Step | Expected result |
|------|-----------------|
| Lint | `lint_report.ok` is true for this sample |
| Convert | `result.ok` is true and `result.xml` is not empty |
| Validate | `val_report.ok` is true for the chosen IWXXM version |
| Decode | A plain-language summary prints |
| File | `kjfk-metar.xml` exists in the working directory |

If your site pins a different IWXXM version line, change `2025-2` to that line.

## Minimal convert-only path

```bash
pip install tac2iwxxm
```

```python
from tac2iwxxm import convert

result = convert(
    "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
    product="METAR",
)
assert result.ok and result.xml
print(result.xml[:200])
```

## If something fails

| Symptom | What to do |
|---------|------------|
| Import error | Make sure that the packages installed into this Python environment. |
| Lint not ok | Print `lint_report.issues`. Fix the TAC. Lint again. |
| Convert not ok | Make sure that `=` is present. Make sure that `product` matches the TAC. |
| Validate not ok | Print `val_report.issues`. Try the IWXXM version your procedure needs. |

## Next step

- Package pages: [Python packages overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages)
- Other paths: [Examples](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Examples)
