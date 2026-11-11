#!/usr/bin/env bash
# Generate CycloneDX SBOM from the uv lock (third-party pins only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p config/sbom
uv export --frozen --no-hashes --no-emit-workspace -o config/sbom/requirements.raw.txt >/dev/null
python3 - <<'PY'
from pathlib import Path

lines: list[str] = []
for line in Path("config/sbom/requirements.raw.txt").read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if " @ " in stripped or stripped.startswith("-e "):
        continue
    if "/Users/" in stripped or stripped.startswith("."):
        continue
    lines.append(line)
Path("config/sbom/requirements.frozen.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
Path("config/sbom/requirements.raw.txt").unlink(missing_ok=True)
PY
uvx --from cyclonedx-bom cyclonedx-py requirements config/sbom/requirements.frozen.txt \
  --of JSON -o config/sbom/cyclonedx.json --output-reproducible --mc-type application
echo "Wrote config/sbom/cyclonedx.json"
