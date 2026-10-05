# BUG-2026-10-04 — Staging Decode visuals shows no reports

## Error description

Decode visuals on staging draws a world map and the notice, then says there are no reports in the view. Continent chips and station popups never appear.

## Error logs

```text
GET https://api.staging.tac-to-iwxxm.com/api/v1/live-map?... 
{"places": [], "space_weather": []}

metar-api env: LIVE_MAP_REFRESH=0, LIVE_MAP_CACHE_URL absent
translator: live map region 0 stored 920
```

| Field | Value |
|-------|--------|
| Env | staging DOKS `metar-iwxxm-staging` |
| App | `https://app.staging.tac-to-iwxxm.com` Decode visuals |
| Observed | 2026-10-04 |

## Investigation

1. The translator pod is running and logs hundreds of stored reports per area.
2. The public live-map route returns an empty place list for a world box.
3. The API container has the refresh timer turned off and no shared cache URL, so it reads an empty process cache.
4. The image rollout sets `LIVE_MAP_REFRESH=0` and updates images. It never applied `LIVE_MAP_CACHE_URL` from the API manifest. The translator manifest, which is applied as a file, does set that variable from `DATABASE_URL`.

## Repro test

`tests/bugs/test_bug_2026_10_04_staging_map_empty.py` — red before the rollout script names `LIVE_MAP_CACHE_URL` and `metar-api-secrets`.

## Fix

Staging rollout patches `metar-api` so `LIVE_MAP_CACHE_URL` comes from secret `metar-api-secrets` key `DATABASE_URL`. [Corpus: tech-spec] [Corpus: product §F37]
