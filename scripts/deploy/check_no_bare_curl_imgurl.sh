#!/usr/bin/env bash
# Fail if ci-cd.yml regresses to brittle deploy-hook+imgURL curl (BUG-2026-08-03).
# After T6.5 / D-S038-t65-waive, Render deploy triggers are retired — GHCR-only Deploy
# is OK; do not require trigger_render_image_deploy.py in the workflow.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WF="${ROOT}/.github/workflows/ci-cd.yml"

if grep -nE '\$\{DEPLOY_HOOK\}&imgURL=|imgURL=\$\{ENCODED_URL\}' "${WF}"; then
  echo "ERROR: brittle Render deploy-hook imgURL curl found in ${WF}" >&2
  echo "Render CD is retired (T6.5). Do not reintroduce bare curl imgURL deploys." >&2
  exit 1
fi

if grep -q 'trigger_render_image_deploy.py' "${WF}"; then
  echo "ERROR: ${WF} still calls trigger_render_image_deploy.py after T6.5 Render decommission." >&2
  echo "Deploy must be GHCR-only; keep the script for emergency resume tooling only." >&2
  exit 1
fi

if grep -nE 'RENDER_BACKEND_DEPLOY_HOOK|RENDER_FRONTEND_DEPLOY_HOOK' "${WF}"; then
  echo "ERROR: ${WF} still wires Render deploy hook secrets after T6.5." >&2
  exit 1
fi

echo "OK: ci-cd.yml has no Render deploy hooks (T6.5) and no brittle imgURL curl"
