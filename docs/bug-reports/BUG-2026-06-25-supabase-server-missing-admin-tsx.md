# BUG-2026-06-25 — Supabase Sync CI: server edge function missing admin.tsx

| Field | Value |
|-------|-------|
| **Status** | verifying |
| **Feature** | F3 (legacy upload edge functions) / deploy infra |
| **Severity** | medium (CI red on main; legacy path) |
| **Classification** | config / implementation drift — missing file since monorepo move |
| **Remediation path** | investigate-only (user 2026-06-25) |

## Error description

GitHub Actions workflow **Supabase Sync** fails on push to `main` during **Deploy edge functions**.
The `server` edge function cannot bundle because `./admin.tsx` is imported but not present.

## Error logs

```
Bundling Function: make-server-2e3cda33
Deploying Function: make-server-2e3cda33 (script size: 977 kB)
Bundling Function: server
Error: failed to create the graph

Caused by:
    Module not found "file:///home/runner/work/metar-to-IWXXM/metar-to-IWXXM/apps/frontend/supabase/functions/server/admin.tsx".
        at file:///home/runner/work/metar-to-IWXXM/metar-to-IWXXM/apps/frontend/supabase/functions/server/index.ts:8:24
failed to bundle function: exit 1
```

- **Run:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/28173223579
- **Job:** Deploy edge functions (job 83442630009)
- **Commit:** `a79c86e` — `[hotfix] F5 work session persist 502 — remove .select() on mutations (#690)`
- **Trigger:** push to `main` (unrelated hotfix content; workflow runs on every main push)

## Symptoms & reproduction

| Field | Value |
|-------|-------|
| Symptom | CI failure — edge function bundle |
| Where | GitHub Actions (`supabase-sync.yml`) |
| When | 2026-06-25 after hotfix merge to main |
| Frequency | Every main push that runs Supabase Sync deploy |
| Repro env | CI (local: `supabase functions deploy` from `apps/frontend` with project ref) |
| Severity | Medium — blocks Supabase edge deploy; `make-server-2e3cda33` still deploys |
| Evidence | CI logs above |

## Investigation

### Root cause

`apps/frontend/supabase/functions/server/index.ts` (line 8) and `index.tsx` (line 7) import:

```ts
import * as admin from './admin.tsx';
```

`admin.tsx` **does not exist** under `server/`. It **does** exist under the sibling function:

- `apps/frontend/supabase/functions/make-server-2e3cda33/admin.tsx` ✓

`server/` directory contents:

| File | Present |
|------|---------|
| auth.tsx | ✓ |
| database.tsx | ✓ |
| index.ts | ✓ |
| index.tsx | ✓ |
| kv_store.tsx | ✓ |
| **admin.tsx** | **✗ missing** |

The import has been present since monorepo migration commit `cb7791e` (`[T6.2] feat: move frontend to apps/frontend`, 2026-06-20). The file was never copied into `server/` at move time; only `make-server-2e3cda33/` received `admin.tsx`.

`admin` module is used for:

- `admin.sendEmailNotification()` — approve/reject user emails
- `admin.getSystemSettings()` / `admin.saveSystemSettings()` — admin settings endpoints

### Why it surfaced now

`supabase-sync.yml` runs `supabase functions deploy --project-ref …` with **no function filter**, deploying **all** directories under `apps/frontend/supabase/functions/`:

1. `make-server-2e3cda33` — bundles and deploys successfully
2. `server` — fails on missing `admin.tsx`

The failure is **latent since T6.2**; it triggers whenever Supabase Sync deploy runs on main with secrets configured.

### Production impact

Per `apps/frontend/ARCHITECTURE.md` and `docs/deploy.md` workflow comments, the **active** legacy upload path uses `make-server-2e3cda33` (see `apps/frontend/src/utils/supabase/info.ts` — `edgeServerSlug = 'make-server-2e3cda33'`). The `server` function appears to be a duplicate/legacy copy. CI failure blocks **full** edge deploy, not necessarily the function the frontend calls today.

## Spec conformance

| Spec | Section | Result |
|------|---------|--------|
| docs/deploy.md | Supabase CI sync | workflow expects all functions to bundle |
| docs/feature-list.md | F3 / legacy upload | drift — incomplete `server/` tree |
| M4 auth on backend | admin routes on metar-api | admin UI already migrated to API host (BUG-2026-06-21) |

No blocking spec contradiction. Fix options are implementation choices.

## Recommended fix options

| Option | Change | Risk | Notes |
|--------|--------|------|-------|
| **A (recommended)** | Add `server/admin.tsx` (copy from `make-server-2e3cda33/admin.tsx`) | Low | Minimal; unblocks CI; matches existing import |
| **B** | Remove `server/` function if unused | Medium | Confirm nothing calls `functions/v1/server/*` in Supabase dashboard |
| **C** | Deploy only `make-server-2e3cda33` in CI | Low | Change workflow to `supabase functions deploy make-server-2e3cda33` |

### Regression test (for fix session)

Static import-resolution test under `tests/bugs/`:

- Scan `apps/frontend/supabase/functions/**/{index.ts,index.tsx}` relative imports
- Assert each `./foo.tsx` target exists in the same directory

No Supabase credentials required; catches this class before CI.

## Fix

Added `apps/frontend/supabase/functions/server/admin.tsx` (same module as
`make-server-2e3cda33/admin.tsx`). Regression test:
`tests/bugs/test_bug_2026_06_25_supabase_server_missing_admin_tsx.py`.

## Verification plan (draft)

| Layer | Check |
|-------|-------|
| L1 | New repro test green; existing pytest suite pass |
| L2 | Local `supabase functions deploy server --project-ref …` bundles (needs token) or PR dry-run lists functions |
| L3 | Re-run Supabase Sync on fix branch / after merge — both functions deploy |

## Timeline

| When | Event |
|------|-------|
| 2026-06-20 | T6.2 monorepo move — `server/index.ts` created with `admin.tsx` import; file missing |
| 2026-06-25 | Supabase Sync fails on main push `a79c86e` |
| 2026-06-25 | Investigation opened (hotfix 14, investigate-only) |
