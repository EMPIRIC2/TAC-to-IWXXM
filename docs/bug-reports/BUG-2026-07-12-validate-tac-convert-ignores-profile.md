# BUG-2026-07-12-validate-tac-convert-ignores-profile

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F6 / F2 (`/api/v1/validate` profile) |
| **Severity** | high |
| **Classification** | code bug |
| **Remediation path** | PR #711 / PRM-015 |
| **GitHub** | [PR #711 review PRR-018](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/711#pullrequestreview-4680875095) |

## Error description

`POST /api/v1/validate` accepts a `profile` form field and passes it to `iwxxm_validate`, but when the caller supplies TAC via `manual_text` without `xml_content`, the auto-convert step calls `convert_metar_tac_with_metadata` without `profile`. Generated XML uses default `annex3` while package validation runs against the requested profile (e.g. `iwxxm_us`).

## Error logs

Bugbot (18-pr-review PRR-018):

```
Validate TAC convert ignores profile
apps/backend/src/api.py:1012
convert_metar_tac_with_metadata(manual_text, iwxxm_version=iwxxm_version)
```

## Investigation

1. Confirmed on `evolve/S008-general-tac-iwxxm-converter`: line ~1012 omits `profile=`.
2. Convert/bulletin paths already forward `profile`; validate auto-convert was missed.
3. Repro: monkeypatch convert and assert kwargs include `profile="iwxxm_us"`.

## Repro test

| Path | Status |
|------|--------|
| `apps/backend/tests/unit/test_bug_2026_07_12_validate_tac_convert_ignores_profile.py` | green |

## Fix

Pass `profile=profile or "annex3"` and `validate=False` into the auto-convert call (endpoint validates afterward).
