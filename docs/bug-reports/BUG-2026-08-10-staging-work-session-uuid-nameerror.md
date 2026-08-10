# BUG-2026-08-10 — Staging work-sessions `NameError: UUID`

## Error description

Authenticated `GET /api/v1/work-sessions` on **staging** returned HTTP 500.
Live Playwright UJ-046 / TC-F31-003–004 failed (login OK; sessions list / draft
upload toast failed). Prod work-sessions remained healthy.

## Error logs

```text
File "/app/apps/backend/src/services/work_session_service.py", line 141, in list_sessions
    stmt = select(table).where(table.c.user_id == UUID(self.user_id))
                                                  ^^^^
NameError: name 'UUID' is not defined
```

| Field | Value |
|-------|--------|
| Env | staging DOKS `metar-iwxxm-staging` |
| API | `https://api.staging.tac-to-iwxxm.com` |
| Image tag | `ghcr.io/.../backend:20260810182452-b0565cc` (image itself **had** `UUID` import) |
| Observed | 2026-08-10 |

## Investigation

1. Health/CORS/H1 connectivity green; only authenticated work-sessions path 500.
2. GHCR image content matched git (`from uuid import UUID, uuid4` present).
3. Running pod file **differed** (import + `uuid4()` id default missing).
4. Root cause: Deployment volume `work-session-ssl-fix` mounts a **stale ConfigMap**
   over `/app/apps/backend/src/services/work_session_service.py` (T7.1 interim sslmode
   rewrite). Staging ConfigMap was out of date vs in-image `_sync_database_url` fix.

## Repro test

- Path: `tests/bugs/test_bug_2026_08_10_staging_work_session_ssl_fix_mount.py`
- Asserts DOKS API Deployment no longer mounts ConfigMap over `work_session_service.py`
- Asserts source file keeps runtime `UUID` / `uuid4` imports

## Fix

1. Live: refreshed staging ConfigMap from current source + rollout restart (immediate).
2. Git: removed `work-session-ssl-fix` volume/mount from
   `deploy/doks/base/deployment-api.yaml` (ssl rewrite is in-image).
3. Docs: `deploy/doks/README.md` — ConfigMap no longer required.

## Interview record

N/A — AskQuestion unavailable; user asked to promote with UJs green; failure caught
during staging UJ verification.

## Prevention & countermeasures

- Do not mount application Python modules from ConfigMaps after the fix is in the image.
- Keep a regression test on the Deployment manifest.
- Prefer image rebuilds over live file overlays for code hotfixes.

## Cursor rule

Deferred — covered by bug regression test + README note.
