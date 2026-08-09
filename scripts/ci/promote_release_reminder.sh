#!/usr/bin/env bash
# Advisory reminder for stage→main promote PRs: bump semver + tag a release.
# Always exits 0 — does not block Staging gate (ADR-034 release-on-promote).
# Traces: docs/deploy.md §Promote · doks-promote-from-stage.mdc §Release on promote
set -euo pipefail

EVENT_NAME="${GITHUB_EVENT_NAME:-}"
BASE_REF="${GITHUB_BASE_REF:-}"
HEAD_REF="${GITHUB_HEAD_REF:-}"

if [[ "${EVENT_NAME}" != "pull_request" || "${BASE_REF}" != "main" || "${HEAD_REF}" != "stage" ]]; then
  echo "promote-release-reminder: skip (not a stage→main PR)"
  exit 0
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

last_deploy="$(git tag -l 'v*-deploy' --sort=-v:refname | head -n1 || true)"
range_note="full stage tip (no prior v*-deploy tag found)"
if [[ -n "${last_deploy}" ]]; then
  range_note="since ${last_deploy}"
fi

changed_pkgs=()
if [[ -n "${last_deploy}" ]]; then
  for pkg in tac2iwxxm tac-validate iwxxm-validate; do
    path="packages/${pkg}"
    [[ -d "${path}" ]] || continue
    if ! git diff --quiet "${last_deploy}...HEAD" -- "${path}" 2>/dev/null; then
      changed_pkgs+=("${pkg}")
    fi
  done
fi

{
  echo "::notice::Release on promote (recommended): bump changed publishable package semver on stage, cut docs/CHANGELOG.md, then after merge to main tag vYYYY.MM.DD-deploy (+ PyPI package tags if publishing). See docs/deploy.md §Promote."
  echo "promote-release-reminder: range ${range_note}"
  if [[ -z "${last_deploy}" ]]; then
    echo "promote-release-reminder: no prior v*-deploy tag — review tac2iwxxm / tac-validate / iwxxm-validate manually."
    echo "::notice::No prior v*-deploy tag found — confirm semver + CHANGELOG before merge; tag after merge to main."
  elif [[ "${#changed_pkgs[@]}" -gt 0 ]]; then
    echo "promote-release-reminder: publishable packages changed: ${changed_pkgs[*]}"
    echo "::notice::Publishable packages changed ${range_note}: ${changed_pkgs[*]} — confirm semver bump (or explicit none) before merge."
  else
    echo "promote-release-reminder: no publishable package tree diffs ${range_note} — CHANGELOG + deploy tag still recommended."
  fi
  echo "promote-release-reminder: checklist docs/deploy.md §Release checklist (stage → main)"
}

exit 0
