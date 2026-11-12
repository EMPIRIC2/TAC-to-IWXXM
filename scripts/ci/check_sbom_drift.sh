#!/usr/bin/env bash
# Fail when committed config/sbom/cyclonedx.json drifts from a fresh generate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [[ ! -f config/sbom/cyclonedx.json ]]; then
  echo "Missing config/sbom/cyclonedx.json — run make sbom and commit" >&2
  exit 1
fi
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
uv export --frozen --no-hashes --no-emit-workspace -o "$tmp/requirements.raw.txt" >/dev/null
python3 - "$tmp/requirements.raw.txt" "$tmp/requirements.frozen.txt" <<'PY'
import sys
from pathlib import Path

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
lines: list[str] = []
for line in src.read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if " @ " in stripped or stripped.startswith("-e "):
        continue
    if "/Users/" in stripped or stripped.startswith("."):
        continue
    lines.append(line)
dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
uvx --from cyclonedx-bom cyclonedx-py requirements "$tmp/requirements.frozen.txt" \
  --of JSON -o "$tmp/cyclonedx.json" --output-reproducible --mc-type application >/dev/null
if ! cmp -s "$tmp/cyclonedx.json" config/sbom/cyclonedx.json; then
  echo "SBOM drift: run 'make sbom' and commit config/sbom/cyclonedx.json" >&2
  diff -u config/sbom/cyclonedx.json "$tmp/cyclonedx.json" | head -80 >&2 || true
  exit 1
fi
echo "SBOM OK (config/sbom/cyclonedx.json matches uv export)"
