# T5.1 — msgspec high-churn HTTP parity tests (TC-F11-001)

**Session:** S014 / EV-010  
**Task:** T5.1  
**Date:** 2026-07-19  
**Status:** completed (red until T5.2)

## Pass criteria (spec)

| Check | How |
|-------|-----|
| Contract coverage | convert / convert-bulletin / validate / lint-tac / decode-tac |
| msgspec encode path | Spy `msgspec_json_response`; helper module + reused Encoder |
| OpenAPI aliases | pydantic `response_model` schemas still in OpenAPI |
| Auth unchanged | `/auth/login` stays pydantic; helper not called |
| convert-zip | Still `application/zip` (not msgspec JSON) |
| Multipart intake | JSON body rejected on lint-tac (E10-28) |

## Test

`apps/backend/tests/unit/test_tc_f11_001_msgspec_http_parity.py`

## Result (pre-T5.2)

11 failed / 7 passed — missing `src.msgspec_http` + handlers not wired.

## Next

**T5.2** — thin helper Struct→`msgspec.json.encode`→`Response`; wire high-churn JSON routes.
