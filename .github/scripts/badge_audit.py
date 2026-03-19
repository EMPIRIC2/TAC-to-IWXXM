#!/usr/bin/env python3
"""Validate that parent and submodule READMEs include at least one badge."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README_PATHS = [
    ROOT / "README.md",
    ROOT / "frontend" / "README.md",
    ROOT / "GIFTs" / "README.md",
    ROOT / "data" / "iwxxm-translation" / "README.md",
    ROOT / "schemas" / "iwxxm" / "README.md",
    ROOT / "schemas" / "iwxxm-codelists" / "README.md",
    ROOT / "schemas" / "iwxxm-modelling" / "README.md",
]

BADGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^\)]*\)")


def main() -> int:
    missing = []
    for readme_path in README_PATHS:
        if not readme_path.exists():
            missing.append(f"Missing README: {readme_path}")
            continue

        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        if not BADGE_PATTERN.search(content):
            missing.append(f"Missing badge markdown in: {readme_path}")

    if missing:
        print("Badge audit failed:")
        for item in missing:
            print(f"- {item}")
        return 1

    print("Badge audit passed for parent and all .gitmodules sub-repos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
