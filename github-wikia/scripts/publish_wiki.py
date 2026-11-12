#!/usr/bin/env python3
"""Copy github-wikia pages into a GitHub Wiki working tree with mapped titles.

Usage:
  python3 github-wikia/scripts/publish_wiki.py --wiki-dir /tmp/TAC-to-IWXXM.wiki

Does not push. After review:
  cd /tmp/TAC-to-IWXXM.wiki && git add -A && git commit && git push
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SIDEBAR = ROOT / "wiki" / "_Sidebar.md"

# Source relative to DOCS -> Wiki filename (GitHub Wiki page title + .md)
PAGE_MAP: dict[str, str] = {
    "index.md": "Home.md",
    "getting-started.md": "Getting-started.md",
    "examples/index.md": "Examples.md",
    "api/index.md": "HTTP-API.md",
    "api/first-convert-call.md": "HTTP-API-First-convert-call.md",
    "api/authentication.md": "HTTP-API-Authentication.md",
    "api/example.md": "HTTP-API-Example.md",
    "web-app/index.md": "Web-app.md",
    "web-app/convert-and-validate.md": "Web-app-Convert-and-validate.md",
    "web-app/work-history.md": "Web-app-Work-history.md",
    "web-app/example.md": "Web-app-Example.md",
    "python-packages/index.md": "Python-packages.md",
    "python-packages/example.md": "Python-packages-Example.md",
    "python-packages/tac2iwxxm.md": "Package-tac2iwxxm.md",
    "python-packages/tac-validate.md": "Package-tac-validate.md",
    "python-packages/iwxxm-validate.md": "Package-iwxxm-validate.md",
    "python-packages/tac-decoding.md": "Package-tac-decoding.md",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        required=True,
        help="Path to a clone of EMPIRIC2/TAC-to-IWXXM.wiki.git",
    )
    args = parser.parse_args()
    wiki: Path = args.wiki_dir
    wiki.mkdir(parents=True, exist_ok=True)

    for src_rel, dest_name in PAGE_MAP.items():
        src = DOCS / src_rel
        if not src.is_file():
            raise SystemExit(f"missing source page: {src}")
        dest = wiki / dest_name
        shutil.copyfile(src, dest)
        print(f"copied {src_rel} -> {dest_name}")

    if SIDEBAR.is_file():
        shutil.copyfile(SIDEBAR, wiki / "_Sidebar.md")
        print("copied wiki/_Sidebar.md -> _Sidebar.md")
    else:
        raise SystemExit(f"missing sidebar: {SIDEBAR}")

    print(f"Wiki working tree ready at {wiki}")
    print("Review, then git add/commit/push in that directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
