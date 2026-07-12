# iwxxm-validate

IWXXM XSD + Schematron validation engine (F2). MIT licensed.

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
