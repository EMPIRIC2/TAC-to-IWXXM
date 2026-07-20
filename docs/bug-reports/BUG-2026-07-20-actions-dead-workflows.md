# BUG-2026-07-20 — GitHub Actions dead / always-red workflows

| Field | Value |
|-------|-------|
| **Status** | fixing |
| **Feature** | M5 (workspace tooling / CI) — ops hygiene |
| **Severity** | medium (noise on Actions board; not blocking `main` merge) |
| **Classification** | integration / process (broken scheduled + legacy workflows) |
| **Remediation path** | Fix locally + PR (P0+P1; Vendor Sync explained, not fixed this PR) |
| **Session** | — |
| **Branch** | `fix/BUG-2026-07-20-actions-dead-workflows` |
| **PR** | https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/745 |

## Error description

The [Actions board](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions)
shows frequent red runs that look like flaky CI. Investigation of ~500 recent
runs (2026-05-08 → 2026-07-20) shows **most failures are permanently broken or
obsolete workflows**, not intermittent flakes in the required `CI/CD Pipeline`.

User ask: identify which jobs/workflows we can **drop**.

## Error logs

### Vendor Schema Sync — 5/5 fail (schedule)

```
ValueError: post-sync checksum mismatch for iwxxm:
  manifest=660380ff2a3077e46803dabde20c2667e1f900297b13a6f15b283dca561c64cd,
  actual=f807d665a84a36f3fa20327f3437772c4c1688d6ca6b11c1b0b88efbe0ab44ec
```

Run: https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29723715733

### E2E Tests — schedule 28/28 fail; push 22/22 “success”

```
cd backend && uv pip install --system -e ".[dev]" httpx asyncpg
/home/runner/work/_temp/.../sh: line 2: cd: backend: No such file or directory
##[error]Process completed with exit code 1.
```

Job: **Performance Benchmarks** (`if: schedule` only). Push runs skip that job,
so the workflow stays green while still using legacy `./backend` paths in
`setup-services` (`continue-on-error: true` → fake green).

Run: https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29714130736

### Smoke Tests on Deploy — always skipped

Triggers on workflow name `"CI/CD Pipeline - 95% Coverage Required"` which no
longer exists after EV-002 consolidation to `ci-cd.yml`.

### CI/CD Pipeline — not flaky on main

Among last 30 `main` runs: **28 success / 2 failure** (both from June hotfixes).
Recent PR failures are legitimate WIP (Validate / package tests), not flakes.

## Investigation

### Timeline

| When | Finding |
|------|---------|
| 2026-07-20 | Pulled 500 runs + per-workflow samples via `gh` |
| 2026-07-20 | Confirmed E2E schedule-only job fails on missing `backend/` |
| 2026-07-20 | Confirmed Vendor Sync checksum mismatch every Monday |
| 2026-07-20 | EV-002 (`docs/decisions/evolve-decisions.md`) already deferred deleting legacy/smoke schedules |

### Hypotheses

| ID | Hypothesis | Result |
|----|------------|--------|
| H1 | Required CI jobs are flaky | **Rejected** — `main` CI healthy; PR reds are WIP |
| H2 | Scheduled E2E is broken post-monorepo | **Confirmed** — `backend/` gone; Performance Benchmarks always fails |
| H3 | Smoke deploy workflow is dead | **Confirmed** — wrong `workflow_run` name; always skipped |
| H4 | Vendor Sync is flake | **Rejected** — see root cause below |
| H5 | Legacy manual CI still useful | **Unlikely** — `test-coverage-95.yml` targets pre-monorepo paths |

### Vendor Sync root cause (2026-07-20)

Not flaky. Two coupled bugs:

1. **Stale pin vs moved tag tip.** Manifest pins `iwxxm` / `iwxxm-modelling` at
   tag `v2025-2` with commit `35180cbe…` / `ec099bfd…`. GitHub
   `releases/latest` for the same tag name now resolves to different SHAs
   (`2c4db03d…` / `4c7fbbfc…`) — confirmed via API vs `vendor/manifest.json`.
2. **Workflow step order.** `vendor-sync.yml` runs:
   - `check_upstream.py --update` → writes new `commit_sha`, **leaves old
     `tree_sha256`**
   - `sync_iwxxm.py --no-legacy` → fetches the new tree, then **requires**
     `tree_sha256` match → raises `ValueError: post-sync checksum mismatch`
   - `check_upstream.py --refresh-tree-hashes` → **never reached**

So every Monday the job updates pins (when the release tip moved) and then
fails verification before hashes can be refreshed / a PR opened.

**Fix (out of P0+P1 scope):** after `--update`, either clear `tree_sha256`,
run sync with `--no-verify` then `--refresh-tree-hashes` then verify, or
refresh hashes immediately after pin update before integrity checks.

### Failure rates (≈500 runs)

| Workflow | Failish rate | Notes |
|----------|--------------|-------|
| Vendor Schema Sync | 100% (5/5) | Broken; keep intent, fix or pause schedule |
| E2E Tests with Real Services | ~54% overall; **schedule 100% fail** | Drop Performance Benchmarks job and/or disable until monorepo rewrite |
| Load Tests (Locust) | historically ~50%; **disabled_inactivity** | Already off |
| Smoke Tests on Deploy | 100% skipped | Safe to delete |
| Legacy CI Pipeline (Manual) | old failures | Safe to delete (EV-002) |
| CI/CD Pipeline | high on PR WIP; **main healthy** | Keep |
| Supabase Sync | ~5% | Keep |

### Drop candidates (ranked)

| Priority | Action | Rationale |
|----------|--------|-----------|
| P0 | Delete or disable **Performance Benchmarks** job in `e2e-tests.yml` | Sole cause of daily red schedule; legacy path |
| P0 | Delete **`smoke-tests-deploy.yml`** | Never runs; wrong trigger (EV-002) |
| P1 | Delete **`test-coverage-95.yml`** (Legacy CI Manual) | EV-002 “delete if still present” |
| P1 | Disable schedule on **`e2e-tests.yml`** (or whole file) until rewritten for `apps/` | Push “green” is fake (`continue-on-error` + missing `backend/`) |
| P2 | Leave **`load-tests.yml`** disabled or delete | Already inactive |
| P2 | **Do not drop** Vendor Sync without replacement — fix checksum / step order, or `workflow_dispatch` only until fixed |
| — | **Keep** `ci-cd.yml`, `supabase-sync.yml`, `pypi-publish.yml` | Required / healthy |

## Repro test

| Field | Value |
|-------|-------|
| Path | `tests/bugs/test_bug_2026_07_20_actions_dead_workflows.py` |
| Status | green (2026-07-20) |
| Assertions | deleted smoke/legacy workflows; E2E has no `schedule` / no `performance-benchmarks` / no `cd backend` |

## Fix

P0+P1 applied on `fix/BUG-2026-07-20-actions-dead-workflows`:

- Delete `.github/workflows/smoke-tests-deploy.yml`
- Delete `.github/workflows/test-coverage-95.yml`
- `e2e-tests.yml`: remove `schedule` cron; remove Performance Benchmarks job
- Vendor Sync: **documented only** — fix deferred (step order + stale `tree_sha256`)

## Interview record

| Step | Answer |
|------|--------|
| Intent | New bug / drop dead workflows (user: "1") |
| symptom_type | Always-red / obsolete Actions (not intermittent flake) |
| where_seen | GitHub Actions board |
| when_started | Ongoing (E2E schedule red since at least mid-June; Vendor Sync 5 consecutive Mondays) |
| Scope | P0+P1 (user: "2:2") + explain Vendor Sync (user: "+ Why…") — not pausing Vendor Sync |
| Remediation path | Fix locally + open PR (user: "3:1") |

## Spec conformance

- [Corpus: decisions] EV-002 — scheduled e2e/load/vendor out of consolidation scope; legacy + smoke called out for delete/fix
- [Corpus: tests] `docs/test-plan.md` lists scheduled `vendor-sync`, load/e2e
- Required PR gate remains `ci-cd.yml` ([ci-after-push](.cursor/rules/optional/ci-after-push.mdc))

## Related

- https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions
- `docs/decisions/evolve-decisions.md` §EV-002 (CI consolidation)
- Workflows: `.github/workflows/{e2e-tests,smoke-tests-deploy,test-coverage-95,vendor-sync,load-tests}.yml`

## Prevention & countermeasures

TBD (Phase 5).

## Cursor rule

TBD.
