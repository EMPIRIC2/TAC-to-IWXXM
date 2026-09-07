# BUG-2026-08-28 — promote_release_reminder bats fails on stage→main PR

| Field | Value |
| --- | --- |
| **Severity** | CI (blocks promote PR #1067) |
| **Branch** | `fix/promote-reminder-bats-ci` |
| **Workflow** | CI/CD Pipeline → Scripts coverage (py + bats) |

## Error description

On the draft promote PR (`stage` → `main`, #1067), job **Scripts coverage (py + bats)**
fails `make test-bats` at:

`scripts/ci/promote_release_reminder.sh: skip outside stage→main PR context`

Push CI on `stage` alone is green (no `GITHUB_BASE_REF=main` / `HEAD_REF=stage`), so the
failure only appears on the promote PR.

## Error logs

```
not ok 4 scripts/ci/promote_release_reminder.sh: skip outside stage→main PR context
# (in test file tests/bats/ci/promote_release_reminder.bats, line 8)
#   `[ "$status" -eq 0 ]' failed
make: *** [Makefile:583: test-bats] Error 1
```

Run: https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/33203935523

## Investigation

1. Promote PR injects `GITHUB_EVENT_NAME=pull_request`, `GITHUB_BASE_REF=main`,
   `GITHUB_HEAD_REF=stage`.
2. `promote_release_reminder.sh` therefore does **not** take the skip branch.
3. Bats helpers put `tests/bats/helpers/bin/git` first on `PATH`; that stub returns
   `deadbeef` for `rev-parse`, so `cd "${ROOT}"` fails under `set -e` → non-zero status.
4. Same class of CI-env pollution as EV-080 `staging_gate.bats` / `alembic_upgrade.bats`
   (clear Actions-injected vars so the intended path is measurable).

## Root cause

The bats case asserts the **skip** path but does not clear CI-injected `GITHUB_*` vars.
On a real stage→main PR job those vars are set, so the script enters the git-using path
against the stub `git` and exits non-zero.

## Repro test

- `tests/bugs/test_bug_2026_08_28_promote_reminder_bats_ci.py` — runs the bats file with
  stage→main `GITHUB_*` env (red before fix, green after).
- Bats file itself must use `env -u GITHUB_EVENT_NAME -u GITHUB_BASE_REF -u GITHUB_HEAD_REF`.

## Fix

Clear Actions PR context vars in `tests/bats/ci/promote_release_reminder.bats` before
invoking the script (mirror `staging_gate.bats`).

## Status

fixed (pending merge to `stage`)
