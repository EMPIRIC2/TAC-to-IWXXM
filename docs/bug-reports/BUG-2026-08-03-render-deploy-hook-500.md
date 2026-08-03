# BUG-2026-08-03 — Render deploy hook `imgURL` returns HTTP 500 (main CI Deploy)

| Field | Value |
|-------|-------|
| **Status** | fixed (pending merge) |
| **Feature** | M5 / deploy (CI CD) |
| **Severity** | high (main `CI/CD Pipeline` Deploy red after green tests) |
| **Classification** | integration / platform |
| **Remediation path** | Resilient trigger script + REST fallback; pre-commit guards |
| **Branch** | `fix/render-deploy-hook-500-fallback` |
| **CI run** | https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30826197508 |

## Error description

On merge of PR #832 (`8bd111c`), Validate + all Test jobs passed, but **Deploy**
failed at "Deploy backend image to Render" when the deploy hook was called with
`imgURL`. GHCR images were pushed successfully; live services were recovered via
manual Render REST `POST /services/{id}/deploys` with `imageUrl`.

## Error logs

```
curl -fsSL "${DEPLOY_HOOK}&imgURL=${ENCODED_URL}"
curl: (22) The requested URL returned error: 500
##[error]Process completed with exit code 22.
```

IMAGE_URL: `ghcr.io/empiric2/tac-to-iwxxm/backend:20260803151459-8bd111c`

## Investigation

1. Failure is isolated to Render deploy-hook + `imgURL` (HTTP 500), not build/test.
2. Docs-only follow-up commit `86c9722` Deploy later succeeded — intermittent/platform.
3. Manual REST with `imageUrl` for the same tag succeeded (deploy-smoke workaround).
4. Root cause for CI redness: brittle one-liner with no retry/REST fallback.

## Repro test

- `tests/bugs/test_bug_2026_08_03_render_deploy_hook_500.py`
- Simulates hook 500 → expects REST fallback success; guards `ci-cd.yml` against bare curl.

## Fix

- `scripts/deploy/trigger_render_image_deploy.py` — hook retries → REST `imageUrl` → optional hook without `imgURL`
- `ci-cd.yml` Deploy steps call the script; wire optional `RENDER_API_KEY` secret
- Pre-commit hook runs the bug unit tests so regressions fail locally via husky
