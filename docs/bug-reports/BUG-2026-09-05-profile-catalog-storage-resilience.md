# BUG-2026-09-05 — Profile catalog should survive storage outages

## Error description

`GET /api/v1/profiles/catalog` regressed from a static YAML-backed response into a
storage-coupled route. The new EV-1120 counts logic calls profile-storage reads before
returning the catalog, so missing `DATABASE_URL`, missing tables, or a transient DB outage
can now turn the whole read-only catalog response into `503 Profile storage unavailable`.

This was caught during PR review for [#1148](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1148).

## Error logs

Review finding:

```text
This changes /profiles/catalog from a static read into a route that always calls
list_rule_packs() and list_overlays() first. Those helpers fail with 503 when
DATABASE_URL is missing or the profile tables are unavailable, so the whole
catalog endpoint now goes down in cases where it previously still served the
YAML-backed catalog.
```

Relevant current failure path in `ConversionProfilesService`:

```text
Profile rule packs unavailable - missing DATABASE_URL
Profile storage unavailable
```

## Investigation

| Time | Note |
|---|---|
| 2026-09-05 | PR review identified that `/profiles/catalog` now depends on `list_rule_packs()` and `list_overlays()` before calling `load_profile_catalog()`. |
| 2026-09-05 | Existing router tests cover happy-path counts, but not storage-failure resilience for the static catalog route. |
| 2026-09-05 | Repro plan: inject a profiles service whose storage calls raise `HTTPException(503)` and assert the route still returns catalog rows with missing counts. |
| 2026-09-05 | Repro confirmed: `tests/bugs/test_bug_2026_09_05_profile_catalog_storage_resilience.py` failed with `assert 503 == 200`. |
| 2026-09-05 | Root cause confirmed: `get_catalog()` let storage-layer `HTTPException(503)` escape before `load_profile_catalog()` ran. |
| 2026-09-05 | Fix applied: treat `503` from rule-pack/overlay count reads as best-effort and still return the static catalog with null counts. |

## Repro test

- Path: `tests/bugs/test_bug_2026_09_05_profile_catalog_storage_resilience.py`
- Red: `uv run pytest -q tests/bugs/test_bug_2026_09_05_profile_catalog_storage_resilience.py` -> failed (`503` returned)
- Green: `uv run pytest -q tests/bugs/test_bug_2026_09_05_profile_catalog_storage_resilience.py apps/backend/tests/unit/test_conversion_profiles_router.py` -> passed
- Expectation: catalog stays `200 OK` and still returns baseline profile rows when counts cannot be loaded

## Fix

- `apps/backend/src/routers/conversion_profiles.py`
  - Catch storage `HTTPException(503)` while computing rule-pack and overlay counts
  - Re-raise non-503 failures so auth/ownership errors still behave normally
- `apps/backend/tests/unit/test_conversion_profiles_router.py`
  - Add route-level regression coverage for storage-unavailable fallback
- `tests/bugs/test_bug_2026_09_05_profile_catalog_storage_resilience.py`
  - Preserve a CI-enrolled red/green repro for the bug

## Interview record

- `19-address-pr-review` scope: fix blocker first, then advisory if still warranted
- Blocker approach: keep static catalog available and make counts best-effort when storage is unavailable
- Remediation path: fix locally first with a repro test, then push after verification

## Prevention & countermeasures

- Add route-level regression tests whenever a static/read-only response starts depending on optional storage enrichment.
- Keep user-specific counts or decorations best-effort when the underlying surface is still useful without them.

## Cursor rule

- Deferred unless the fix reveals a reusable guardrail worth codifying
