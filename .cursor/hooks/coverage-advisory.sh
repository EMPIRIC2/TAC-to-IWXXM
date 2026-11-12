#!/usr/bin/env bash
# Cursor afterFileEdit hook (advisory): EV-080 / ADR-007 coverage fill-before-flip.
# Always exit 0 — never block edits; emit additional_context when relevant.
set -euo pipefail

payload="$(cat)"
file_path="$(
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('filePath') or d.get('file_path') or '')" <<<"$payload"
)"

if [[ -z "$file_path" ]]; then
  echo '{}'
  exit 0
fi

repo_root="$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null || pwd)"
rel="${file_path#"$repo_root"/}"
rel="${rel#/}"
base="$(basename "$rel")"

context=""

# Gate / threshold config surfaces — fill-before-flip reminder.
case "$rel" in
  pyproject.toml|*/pyproject.toml|Makefile|.github/workflows/ci-cd.yml|\
  docs/adr/ADR-007*|docs/typing-policy.md|\
  scripts/ci/check_per_file_coverage.py|scripts/ci/run_*coverage*.sh|\
  */vitest.config.ts|*/vitest.config.mts|vitest.config.ts)
    context="[coverage-advisory] ADR-007 / EV-080: fill-before-flip — do not raise fail_under / Vitest thresholds / --cov-fail-under / --min-pct until the tip is green at 100%. Legacy asserts of literal 95 flip in T2.5 with the gate. Scripts: make test-coverage-scripts / make test-bats (scaffold until M4)."
    ;;
esac

# Source under coverage measurement.
if [[ -z "$context" ]]; then
  case "$rel" in
    apps/*|packages/*)
      case "$base" in
        *.py|*.ts|*.tsx)
          context="[coverage-advisory] Unit coverage target is 100% line+branch (ADR-007). Prefer tests covering new/changed branches before flipping CI floors. Executable FE coverage excludes are revoked (EV-080); approved omits: vendor, generated xsd/codegen, fixtures only."
          ;;
      esac
      ;;
    scripts/*)
      case "$base" in
        *.py|*.sh)
          context="[coverage-advisory] Scripts surface: Python → make test-coverage-scripts (100%); shell → make test-bats (every .sh). No live secrets in bats (NFR-EV080-006)."
          ;;
      esac
      ;;
    tests/scripts/*|tests/bats/*)
      context="[coverage-advisory] Scripts harness: bats must avoid live network/creds (prefer --help / mocks). Python scripts cov uses make test-coverage-scripts with fail_under 100 once tests exist."
      ;;
  esac
fi

if [[ -z "$context" ]]; then
  echo '{}'
  exit 0
fi

python3 -c "import json,sys; print(json.dumps({'additional_context': sys.argv[1]}))" "$context"
exit 0
