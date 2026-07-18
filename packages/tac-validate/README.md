# tac-validate

TAC parse gate and shared business-rule pack for F6 products. MIT licensed.

## Install

```bash
pip install tac-validate==0.1.0
# or from the monorepo workspace:
uv sync --package tac-validate
```

## Library

```python
from tac_validate import lint

report = lint("METAR KJFK ...=", product="METAR")
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

Exit code `0` when lint `ok`; `1` when error-severity issues are present (or the file cannot be read).

Rule depth (E10-21): METAR/SPECI/TAF full checklist; SIGMET/AIRMET/VAA/TCA template+gates.
Citations live in `docs/domain/TAC_VALIDATION.md` — no Annex prose in the wheel.

See ADR-015 / ADR-016. No FastAPI/Supabase imports; HTTP maps msgspec → pydantic.
