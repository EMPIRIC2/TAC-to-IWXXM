# BUG-2026-08-22 — Mutation pnpm conflict + Vendor Sync same-tag drift

| Field | Value |
| --- | --- |
| **Severity** | CI / scheduled workflows |
| **Branch** | `fix/ci-mutation-vendor-sync` |
| **Workflows** | `Mutation`, `Vendor Schema Sync` |

## Error description

1. **Mutation** (nightly on `main`): `pnpm/action-setup` fails with
   `Multiple versions of pnpm specified` — workflow `version: 9` vs
   `packageManager: pnpm@9.15.4` in `package.json`.
2. **Vendor Schema Sync** (weekly on `main`): after `check_upstream --update`,
   sync replaces `vendor/schemas/iwxxm` with GitHub tag tip `v2025-2` at commit
   `2c4db03…` (flat `IWXXM/` layout). TC-M002 expects versioned paths such as
   `iwxxm/2025-2/IWXXM/iwxxm.xsd` from intentional pin `35180cbe…`.

## Error logs

```
Error: Multiple versions of pnpm specified:
  - version 9 in the GitHub Action config with the key "version"
  - version pnpm@9.15.4 in the package.json with the key "packageManager"
```

```
FAILED tests/vendor/test_schema_presence.py::... - missing vendored schema path: iwxxm/2025-2/IWXXM/iwxxm.xsd
```

## Investigation

- Mutation run `32554273227` (2026-08-22): both `stryker (frontend)` and
  `stryker (shared)` failed at Install pnpm; Python gremlins jobs passed.
- Vendor sync: `check_upstream` updated `commit_sha` when release **tag name**
  matched but tip commit differed. wmo-im republished `v2025-2` with a
  different tree (see `docs/domain/IWXXM_VALIDATION.md` pin vs tip note).

## Root cause

1. `mutation.yml` duplicated pnpm version pin instead of using
   `packageManager` from `package.json` (as `ci-cd.yml` does).
2. `check_upstream.py` treated same-tag / different-commit as an update,
   overwriting intentional ahead-of-tip pins.

## Repro test

- `tests/bugs/test_bug_2026_08_22_ci_mutation_vendor_sync.py` — green after fix.
- Updated `tests/bugs/test_bug_2026_07_20_actions_dead_workflows.py` — tag-change
  update still clears `tree_sha256`.

## Fix

- `mutation.yml`: remove `version: 9`; align pnpm/node setup with `ci-cd.yml`.
- `check_upstream.py`: when release tag matches pin, keep `commit_sha` even if
  GitHub tip moved.
