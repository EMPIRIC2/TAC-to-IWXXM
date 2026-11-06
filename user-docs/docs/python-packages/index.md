# Python packages overview

These packages let you convert and examine aviation weather text in Python
without the web app. Each package is MIT licensed and publishes to the Python
Package Index (PyPI).

## Packages

| Package | Role |
|---------|------|
| [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm) | Convert TAC text to IWXXM XML |
| [tac-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-validate) | Lint TAC text against product rules |
| [iwxxm-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-iwxxm-validate) | Make sure that IWXXM XML meets well-formed, XSD, and Schematron rules |
| [tac-decoding](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-decoding) | Decode TAC into plain-language segments and a summary |

## Shared rules

1. Use Python 3.12 or newer.
2. Install from PyPI with `pip` unless your organization pins another index.
3. Keep FastAPI and database code out of these libraries. Call the HTTP API when
   you need the hosted service.
4. Copy examples from these pages without changing protected code blocks unless
   your TAC input changes.

## Suggested order

1. Lint TAC with `tac-validate` when you need rule checks before convert.
2. Convert with `tac2iwxxm`.
3. Validate IWXXM with `iwxxm-validate` when your procedure needs schema checks.
4. Use `tac-decoding` when you need a plain-language summary for operators.

The optional extra `tac2iwxxm[validate]` installs `tac-validate` and
`iwxxm-validate` together.

## Example

Follow the [Python packages example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages-Example)
for lint, convert, validate, and decode of one sample METAR.
