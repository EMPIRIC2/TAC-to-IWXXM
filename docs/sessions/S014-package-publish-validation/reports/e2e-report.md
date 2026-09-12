# E2E Behavior Report — S014 / EV-010 (stage 10-e2e, T6.2)

> Generated: 2026-07-19  
> Mechanism: mixed — in-process (pytest/Vitest) + live local API (httpx/urllib vs `:18001`)  
> Journeys tested: UJ-022, UJ-023, UJ-DEV-005 (cycle feature_ids F11–F14)

## Summary

| # | Journey | Mechanism | Steps | Passed | Failed | Status |
|---|---------|-----------|-------|--------|--------|--------|
| 1 | UJ-022 Operator convert/validate after msgspec (F11) | T0 pytest/Vitest + live local API | 4 | 4 | 0 | PASS (T3/H6′ → 13) |
| 2 | UJ-023 PyPI tag → install smoke (F12–F14) | workflow unit + checklist (CI tier) | 2 | 2 | 0 | PASS (live PyPI → 13) |
| 3 | UJ-DEV-005 pip install packages + convert/validate | clean-venv / wheel smokes | 3 | 3 | 0 | PASS |

## Tier status (connectivity-gates §Stage 10)

| Tier | What ran | Result |
|------|----------|--------|
| T0 in-process | TC-F11-001 (26), TC-F12/F13/F14 + wheels (67), FE utils Vitest (222) | PASS |
| T2-local API | Authenticated convert/validate/lint/decode vs local `:18001` | PASS (below) |
| T2-local browser | Playwright H6′ workbench | Deferred to 13 (no dedicated F11 Playwright spec; parity covered by T0 + API) |
| T2 deploy smoke (H1–H5) | — | Deferred to 13-deploy-smoke (T6.5) |
| T3 live UJ | — | Deferred to 13 / 15 |

## Journey details

### UJ-022: Operator convert/validate after msgspec HTTP (F11)

- **Feature**: F11; tests TC-F11-001  
- **T0**: `test_tc_f11_001_msgspec_http_parity.py` + CORS after msgspec — **26 passed**  
- **FE**: `src/utils` Vitest including `api.test.ts` — **222 passed** (20 files)  
- **Live local API** (`http://127.0.0.1:18001`, admin JWT):

| Step | Result |
|------|--------|
| POST `/api/v1/convert` JSON golden METAR | 200, `successful=1`, XML len 2611 |
| POST `/api/v1/validate` multipart | 200, `is_valid=true` |
| POST `/api/v1/lint-tac` | 200, `ok=true` |
| POST `/api/v1/decode-tac` | 200, `summary` present |

Response keys match msgspec/FE contract (`results`, `metadata`, `summary`, etc.).

### UJ-023: PyPI release tag → install smoke (F12–F14)

- **Tier: CI** (user-journeys.md)  
- `tests/unit/test_tc_f14_001_pypi_publish_workflow.py` — OIDC matrix + dry-run defaults **PASS**  
- Live tag → TestPyPI/PyPI publish deferred to **T6.4/T6.5** (Trusted Publisher still pending from M4)

### UJ-DEV-005: pip install published packages + convert/validate

- `packages/tac-validate/tests/test_tc_f12_wheel_smoke.py` — PASS  
- `packages/iwxxm-validate/tests/test_tc_f13_*` — PASS  
- `packages/tac2iwxxm/tests/test_tc_f14_002_validate_extra.py` (`[validate]` extra clean venv) — PASS  

## Journey → test file matrix (cycle scope)

| Journey | Test module | T0 | T2-local | T3 |
|---------|-------------|----|----------|----|
| UJ-022 | `apps/backend/tests/unit/test_tc_f11_001_*.py`; FE `api.test.ts` / utils | PASS | live API PASS | → 13 H6′ |
| UJ-023 | `tests/unit/test_tc_f14_001_pypi_publish_workflow.py` | PASS | n/a (CI) | → 13 tag smoke |
| UJ-DEV-005 | `test_tc_f12_wheel_smoke.py`, `test_tc_f13_*`, `test_tc_f14_002_*` | PASS | n/a | → 13 |

## Run notes

```bash
cd apps/backend && uv run pytest tests/unit/test_tc_f11_001_*.py -v --no-cov
uv run pytest packages/tac-validate/tests/test_tc_f12_*.py \
  packages/iwxxm-validate/tests/test_tc_f13_*.py \
  packages/tac2iwxxm/tests/test_tc_f14_002_validate_extra.py \
  tests/unit/test_tc_f14_001_pypi_publish_workflow.py -v --no-cov
pnpm --filter @metar/frontend exec vitest run src/utils
# live API: login + convert/validate/lint/decode against :18001 (see session shell log)
```
