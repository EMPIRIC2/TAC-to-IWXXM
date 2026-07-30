# BUG-2026-07-30 — SPECI A3-2 decode residuals (F9)

| Field | Value |
|-------|-------|
| **Status** | fixed locally — awaiting commit/PR/deploy approval |
| **Feature** | F9 value-aware decode / plain-language (operator CODE panel) |
| **Severity** | medium (catalog SPECI demo shows undecoded residuals; IWXXM convert OK) |
| **Classification** | code bug (decode explainer gaps vs convert parser) |
| **Remediation path** | local-first — deploy only after explicit approval |
| **Session** | ad-hoc 14-hotfix (active_session was null) |
| **Branch** | fix/BUG-2026-07-30-speci-decode-residuals |
| **PR** | — |

## Error description

Loading / decoding Annex 3 **SPECI A3-2** (`SPECI YUDO … 1200NE +TSRA BKN005CB … TEMPO TL1200 … BECMG AT1200 8000 NSW NSC=`) shows CODE/PLAIN LANGUAGE residuals for groups that convert already maps into IWXXM:

- `1200NE` (minimum visibility + sector)
- `BKN005CB` (cloud + CB)
- `TEMPO TL1200` / `BECMG AT1200` (trend change + time)
- `NSW` (no significant weather in trend)

Plain-language summary also mis-attributes trend visibility (`0600`, `8000`) as prevailing observation visibility because those tokens match the generic 4-digit vis explainer while trend keywords stay residual.

Convert (`tac2iwxxm.convert`, profile `annex3`) succeeds with `minimumVisibility`, cloud CB, and both trend forecasts — **not** an IWXXM emit bug.

## Error logs

User UI (operator workbench decode panel, 2026-07-30):

```
[lint-tac] 1 issue(s): [MISSING_PRODUCT_KEYWORD] SPECI TAC must contain one of ['SPECI']
[lint-tac] 2 issue(s): [INVALID_RVR] METAR invalid RVR token 'R12/1000U' — research R8; [NSW_PRESENT] METAR NSW present — research T3 / S1
PLAIN LANGUAGE
… Prevailing visibility 3000 m; Heavy thunderstorm with rain; … Prevailing visibility 600 m; Prevailing visibility 8000 m; No significant cloud. Not decoded: 1200NE BKN005CB TEMPO TL1200 BECMG AT1200 NSW.
RESIDUALS
1200NE
BKN005CB
TEMPO TL1200
BECMG AT1200
```

Local library probe (`decode_tac(..., product="SPECI")`):

```
residuals: ['1200NE', 'BKN005CB', 'TEMPO TL1200', 'BECMG AT1200', 'NSW']
convert(..., product='SPECI', profile='annex3') → ok=True, issues=[]
  minimumVisibility / trendForecast present
```

Note: lint lines referencing `R12/1000U` / `MISSING_PRODUCT_KEYWORD` look like cross-product UI noise — **out of scope** for this hotfix (decode-only).

## Investigation

### Timeline

| When | Note |
|------|------|
| 2026-07-30 | User reports SPECI residuals on “standard IWXXM” workbench decode |
| 2026-07-30 | Confirmed fixture = `speci_a3_2.tac` / frontend `speci_a3_2.tac` |
| 2026-07-30 | Convert OK; gaps isolated to `_explain_metar_speci` in `decode.py` |

### Hypotheses

| # | Hypothesis | Result |
|---|------------|--------|
| H1 | Convert/IWXXM missing min-vis / cloud / trends | **Rejected** — annex3 emit includes them |
| H2 | F9 METAR/SPECI explainer lacks min-vis, CB/TCU, trend tokens, NSW | **Confirmed** |
| H3 | Cloud regex rejects `BKN005CB` (no CB/TCU group) | **Confirmed** |

### Root cause (provisional)

`packages/tac2iwxxm/src/tac2iwxxm/decode.py` `_explain_metar_speci` / `_CLOUD` do not cover groups that `products/metar_speci.py` already parses for convert. TAF decode already explains `TEMPO`/`BECMG`; METAR/SPECI path does not.

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_07_30_speci_decode_residuals.py` | **RED** 2026-07-30 → **GREEN** 2026-07-30 |

TDD iteration log:

1. Asserted SPECI A3-2 explains `1200NE`, `BKN005CB`, `TEMPO`/`TL1200`, `BECMG`/`AT1200`, `NSW` and keeps them out of residuals — failed as expected.
2. Extended `_explain_metar_speci` + cloud/min-vis/trend-time patterns — repro green; F9 decode suites (61) green.

## Fix

- `packages/tac2iwxxm/src/tac2iwxxm/decode.py`:
  - `_VIS_MIN` — minimum visibility + compass sector
  - `_CLOUD` — optional `CB`/`TCU`; `_fmt_cloud` names the type
  - `_TREND_TIME` — `TL`/`AT`/`FM` + HHMM for METAR/SPECI trends
  - Explain `TEMPO` / `BECMG` / `NOSIG` / `NSW`; mark `in_trend` so trend vis/wx/cloud wording is distinct from observation

## Interview record

| Step | Answer |
|------|--------|
| Intent | Investigate + fix (go-ahead) |
| Scope | Decode / plain-language residuals only |
| Sample | SPECI A3-2 (exact golden / catalog) |

## Prevention & countermeasures

— (Phase 5)

## Cursor rule

— (deferred until close)
