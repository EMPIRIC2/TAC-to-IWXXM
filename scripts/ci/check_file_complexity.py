#!/usr/bin/env python3
"""Run Ruff C901 gate via dedicated config (ADR-056).

Uses ``scripts/ci/policy/ruff-complexity.toml`` so nested package ``pyproject.toml``
``per-file-ignores`` cannot drop the complexity rule.

[Corpus: adr/ADR-056] [Corpus: product §M5]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "scripts" / "ci" / "policy" / "ruff-complexity.toml"


def main() -> int:
    """Invoke ``ruff check --config scripts/ci/policy/ruff-complexity.toml``."""
    if not CONFIG.is_file():
        print(f"missing {CONFIG}", file=sys.stderr)
        return 2
    cmd = [
        "uv",
        "run",
        "ruff",
        "check",
        "--config",
        str(CONFIG),
        "--force-exclude",
        "apps",
        "packages",
        "tests",
    ]
    print(" ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
