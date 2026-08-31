#!/usr/bin/env python3
"""Fail if OpenGrep JSON has findings not listed in the baseline file.

Baseline format (tab-separated): check_id\\tpath  (repo-relative path)
[Corpus: adr-037]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _rel(path: str, root: Path) -> str:
    raw = path or ""
    try:
        return str(Path(raw).resolve().relative_to(root.resolve()))
    except Exception:
        return raw[2:] if raw.startswith("./") else raw


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "usage: filter-opengrep-baseline.py <report.json> <baseline.txt> [opengrep_exit] [repo_root]",
            file=sys.stderr,
        )
        return 2
    report = Path(sys.argv[1])
    baseline_path = Path(sys.argv[2])
    og_rc = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    root = Path(sys.argv[4]) if len(sys.argv) > 4 else Path(
        os.environ.get("GITHUB_WORKSPACE") or Path.cwd()
    )

    data: dict = {}
    if report.is_file():
        data = json.loads(report.read_text(encoding="utf-8"))
    results = data.get("results") or []

    allow: set[tuple[str, str]] = set()
    if baseline_path.is_file():
        for line in baseline_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                allow.add((parts[0], parts[1]))

    new = {
        (r.get("check_id") or "", _rel(r.get("path") or "", root))
        for r in results
        if (r.get("check_id") or "", _rel(r.get("path") or "", root)) not in allow
    }
    if new:
        print(f"[security] OpenGrep NEW findings ({len(new)}):", file=sys.stderr)
        for cid, path in sorted(new):
            print(f"  {cid}  {path}", file=sys.stderr)
        return 1

    print(f"[security] OpenGrep OK — {len(results)} finding(s), all baselined or none")
    if not results and og_rc not in (0, 1):
        return og_rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
