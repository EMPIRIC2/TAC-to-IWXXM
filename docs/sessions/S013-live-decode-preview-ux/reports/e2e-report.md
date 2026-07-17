# E2E Behavior Report — S013 / EV-009 (stage 10-e2e, T4.2)

> Generated: 2026-07-17
> Mechanism: mixed — browser (Playwright, local dev stack) + API (curl vs local backend) + in-process (Vitest/pytest)
> Journeys tested: UJ-020, UJ-021 (cycle feature_ids F9, F10)

## Summary

| # | Journey | Mechanism | Steps | Passed | Failed | Status |
|---|---------|-----------|-------|--------|--------|--------|
| 1 | UJ-020 Value-aware decode + plain-language summary (F9) | browser + API | 5 | 5 | 0 | PASS |
| 2 | UJ-021 IWXXM preview pane + terminator quick fix (F10) | browser + API | 4 | 4 | 0 | PASS |

## Tier status (connectivity-gates §Stage 10)

| Tier | What ran | Result |
|------|----------|--------|
| T0 in-process | TC-F9-001/002 + TC-F10-001/002 unit/Vitest/API-contract suites (in `make test`) | PASS (see qa-report.md counts) |
| T2-local browser | Playwright `f9-f10-live-decode-preview.e2e.spec.ts` vs local dev stack (frontend :18000 + API :18001; F9/F10 API routes stubbed in-page per spec design) | **2/2 PASS** (16.2 s) |
| Live local API (unstubbed) | curl vs running backend: decode-tac `summary` + lint-tac info/fixes | PASS (below) |
| T2 deploy smoke (H1–H5) | — | Deferred to 13-deploy-smoke (T4.5) |
| T3 live UJ | — | Deferred to 13-deploy-smoke / 15-service-health |

Note: mocked-route Playwright passing does **not** claim production connectivity; H4–H5 run at deploy.

## Journey details

### UJ-020: Value-aware decode + plain-language summary (F9)

- **Feature**: F9 (`docs/feature-list.md`); tests TC-F9-001/002
- **Mechanism**: Playwright (chromium, 1 worker) + live API
- **Steps**:
  1. Open converter workbench — PASS
  2. Type METAR without refresh (`METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011`) — PASS
  3. `decode-plain-language` block becomes visible live — PASS
  4. Summary contains value-aware content (`KJFK` / `180°` / `24 °C`) — PASS
  5. Live unstubbed API: `POST /api/v1/decode-tac` (multipart, product=METAR) returns 9 segments and
     `summary: "Report type (routine meteorological aerodrome report); station KJFK; day 12 at
     12:51 UTC; from 180° at 4 kt; Prevailing visibility 10 statute miles; Few clouds at
     25,000 ft; Temperature 24 °C, dewpoint 18 °C; Altimeter 30.11 inHg."` — PASS

### UJ-021: IWXXM preview pane + terminator quick fix (F10)

- **Feature**: F10 (`docs/feature-list.md`); tests TC-F10-001/002
- **Mechanism**: Playwright (chromium) + live API
- **Steps**:
  1. `iwxxm-preview-pane` mounts with empty state visible — PASS
  2. Paste single report without `=`; open workbench console — PASS
  3. `console-action-add_terminator` ("Add `=`") visible and clickable — PASS
  4. Editor buffer ends with `=` after quick fix (poll) — PASS
  - Live unstubbed API: `POST /api/v1/lint-tac` returns `ok: true` with **info**-severity
    `MISSING_TERMINATOR` ("Reports in bulletins end with '=' — add it before publishing") and
    `fixes[0] = add_terminator` with full-text `replacement` ending in `=` — PASS

## Journey → test file matrix (cycle scope)

| Journey | Test module | T0 | T2-local | T3 |
|---------|-------------|----|----------|----|
| UJ-020 | `apps/e2e/f9-f10-live-decode-preview.e2e.spec.ts`; `packages/tac2iwxxm/tests/test_decode_{value_aware,summary}.py`; `apps/backend/tests/unit/test_tc_f9_002_decode_tac_summary.py`; `DecodePanel.test.tsx` | PASS | PASS | deferred → 13 |
| UJ-021 | same spec; `packages/tac-validate/tests/test_tc_f10_002_terminator_info.py`; `apps/backend/tests/unit/test_tc_f10_002_lint_tac_terminator.py`; `IwxxmPreviewPane.test.tsx`, `WorkbenchConsole.terminator.test.tsx` | PASS | PASS | deferred → 13 |

## Run notes

- Playwright's own `webServer` bootstrap (`start-dev-servers.sh` via config) timed out at 300 s in
  this environment (same behavior noted at T3.7); resolved by starting the dev stack manually and
  running Playwright with `PLAYWRIGHT_BASE_URL=http://0.0.0.0:18000` (skips webServer/globalSetup).
  Not a product defect; CI `e2e-tests.yml` owns the managed-server path.
- Repro:

```bash
AUTO_KILL_PORTS=true METAR_CONFIG_ENV=local bash start-dev-servers.sh --kill &
cd apps/e2e && PLAYWRIGHT_BASE_URL=http://0.0.0.0:18000 \
  pnpm exec playwright test f9-f10-live-decode-preview.e2e.spec.ts
```
