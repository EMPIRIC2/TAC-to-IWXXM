# tac-validate

TAC parse gate and shared business-rule pack for F6 products. MIT licensed.

## Usage

```python
from tac_validate import lint

report = lint("METAR KJFK ...=", product="METAR")
if not report.ok:
    for issue in report.issues:
        print(issue.code, issue.message)
    for fix in report.fixes:
        print(fix.code, fix.replacement)
```

See ADR-015 / ADR-016. No FastAPI/Supabase imports; HTTP maps msgspec → pydantic.
