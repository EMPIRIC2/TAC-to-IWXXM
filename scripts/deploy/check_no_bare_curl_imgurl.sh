#!/usr/bin/env bash
# Fail if ci-cd.yml regresses to brittle deploy-hook+imgURL curl (BUG-2026-08-03).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WF="${ROOT}/.github/workflows/ci-cd.yml"

if grep -nE '\$\{DEPLOY_HOOK\}&imgURL=|imgURL=\$\{ENCODED_URL\}' "${WF}"; then
  echo "ERROR: brittle Render deploy-hook imgURL curl found in ${WF}" >&2
  echo "Use scripts/deploy/trigger_render_image_deploy.py instead." >&2
  exit 1
fi

if ! grep -q 'trigger_render_image_deploy.py' "${WF}"; then
  echo "ERROR: ${WF} must call trigger_render_image_deploy.py for image deploys." >&2
  exit 1
fi

echo "OK: ci-cd.yml uses resilient Render image deploy trigger"
