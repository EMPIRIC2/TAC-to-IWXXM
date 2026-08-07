# BUG-2026-08-07 — Supabase Sync CI fails on `supabase link` (`inserted_at` SchemaError)

| Field | Value |
|-------|-------|
| **Status** | fixed (pending merge) |
| **Feature** | M5 / ops (Supabase migrations CI) |
| **Severity** | high (blocks `Supabase Sync` on `main` + PR checks, e.g. #901) |
| **Classification** | integration / tooling |
| **Remediation path** | Pin Supabase CLI below broken `latest`; strip stale onrender allow-list leftovers |
| **Branch** | `fix/BUG-2026-08-07-supabase-sync-cli-pin` |
| **CI runs** | https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31178626341/job/92866314571 · PR #901 https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31190674882 |

## Error description

GitHub Action **Supabase Sync → Sync database migrations** fails at **Link project**
when `supabase/setup-cli` installs `version: latest` (CLI **2.112.0**). The same
failure appears on `main` after merges and on open PRs that run the workflow
(e.g. docs PR #901). Edge-function job is unaffected (no `link`).

## Error logs

```
failed to get api keys: SchemaError(Expected a string matching the RegExp ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
  at [2]["inserted_at"])
Try rerunning the command with --debug to troubleshoot the error.
##[error]Process completed with exit code 1.
```

Annotation warning (non-fatal): Node.js 20 deprecated for `supabase/setup-cli@v1`.

## Investigation

| Time (UTC) | Note |
|------------|------|
| 2026-08-07 | Main run 31178626341 / job 92866314571 — fail at `supabase link` |
| 2026-08-07 | PR #901 run 31190674882 — same SchemaError |
| 2026-08-07 | Local CLI **2.111.0** `supabase link --project-ref ktvxijislbtgqapllmuk` succeeds |
| 2026-08-07 | Publishable key `inserted_at` is `…+00:00` (not `Z`); index `[2]` matches CLI decode failure |
| 2026-08-07 | Upstream: [supabase/cli#6115](https://github.com/supabase/cli/issues/6115) — regression in 2.112.0; workaround pin **2.111.0** |

### Hypotheses

1. **Primary (confirmed):** `version: latest` pulled CLI 2.112.0; generated API-keys schema requires `Z` suffix; Management API returns `+00:00` → `link` aborts.
2. Secrets missing — rejected (token/password present; fail is schema decode).
3. Project paused / network — rejected (same credentials work on 2.111.0).

### Onrender callback / CORS leftovers (same hotfix)

User also asked to strip callbacks to `https://metar-to-iwxxm-frontend-v4-web.onrender.com/`.

| Surface | Status 2026-08-07 |
|---------|-------------------|
| Live Supabase Auth `site_url` / `uri_allow_list` | Already `app.tac-to-iwxxm.com` (+ local); **no** onrender |
| Live API CORS `Origin: …onrender.com` | **400** `Disallowed CORS origin` |
| Live `/config.json` | DOKS hosts only |
| `deploy/doks/base/configmap-*.yaml` | Still listed onrender in CORS — **strip** |
| `docs/ops/env-sync-runbook.md` Step 1 redirect example | Still onrender — **update** |
| `scripts/deploy/apply_render_cors_env.sh` default | Still onrender — **retarget / deprecate default** |

## Repro test

- Path: `tests/bugs/test_bug_2026_08_07_supabase_sync_cli_inserted_at.py`
- Asserts `supabase-sync.yml` pins CLI `2.111.0` (not `latest`) and DOKS/prod config omit the suspended Render frontend origin.

## Fix

- Pin `supabase/setup-cli` `version: 2.111.0` in `.github/workflows/supabase-sync.yml` (migrations + functions).
- Remove `metar-to-iwxxm-frontend-v4-web.onrender.com` from DOKS base CORS ConfigMaps.
- Update env-sync runbook Auth redirect examples to `https://app.tac-to-iwxxm.com/**`.
- Default `FRONTEND_ORIGIN` in `apply_render_cors_env.sh` to DOKS frontend host (script remains Render-API based for archive/emergency use).

## Interview record

- Intent: fix CI failure on linked runs + strip onrender callbacks (user `/14-hotfix` + URLs).
- AskQuestion tool unavailable this turn; proceeded on explicit user scope.

## Prevention & countermeasures

- Keep CLI pin until [supabase/cli#6115](https://github.com/supabase/cli/issues/6115) is fixed and verified.
- Regression test guards against `version: latest` in this workflow.
- Prefer `app.tac-to-iwxxm.com` in any Auth/CORS allow-list docs (Render decommissioned).

## Cursor rule

- Deferred — existing CI pin + bug test sufficient; revisit if `latest` is reintroduced elsewhere.
