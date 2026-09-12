# T5.2 — msgspec JSON response helper + high-churn wiring (E10-38)

**Session:** S014 / EV-010  
**Task:** T5.2  
**Date:** 2026-07-19  
**Status:** completed

## Changes

| Item | Path |
|------|------|
| Helper | `apps/backend/src/msgspec_http.py` — reused `json_encoder` + `msgspec_json_response` |
| Wiring | `lint_tac`, `decode_tac_endpoint`, `convert_bulletin`, `validate_comprehensive`, `convert` → `msgspec_json_response(...)` |
| Dep | `msgspec>=0.19` direct on `apps/backend` |
| OpenAPI | pydantic `response_model=` aliases retained (no dual runtime validation) |
| Unchanged | multipart Form/File intake; `/auth/*`; `convert-zip` StreamingResponse |

## Encode path

- Prefer msgspec Struct; pydantic OpenAPI alias models accepted via `model_dump(mode="json")` then single msgspec encode.
- Auth/work-sessions remain pydantic FastAPI serialization.

## Verification

`test_tc_f11_001_msgspec_http_parity.py` — 18 passed; related TC-F6/F7/F11/auth smokes — 49 passed.

## Next

**T5.3** — soft HTTP bench ≤1.0× pydantic map baseline.
