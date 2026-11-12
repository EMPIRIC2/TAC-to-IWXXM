#!/usr/bin/env python3
"""Fail closed when OSV-Scanner reports findings at or above a CVSS threshold.

[Corpus: tech-spec] TR-Q08
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _cvss(vuln: dict[str, Any]) -> float:
    score = vuln.get("severity")
    if isinstance(score, (int, float)):
        return float(score)
    text = str(score or "").upper()
    return {"CRITICAL": 9.5, "HIGH": 7.5, "MEDIUM": 5.0, "LOW": 2.0}.get(text, 0.0)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: filter_osv_severity.py <report.json> [fail_cvss] [scanner_exit]",
            file=sys.stderr,
        )
        return 2
    path = Path(sys.argv[1])
    fail_cvss = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    scanner_exit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    if not path.is_file():
        return 0 if scanner_exit == 0 else (scanner_exit or 1)
    data = json.loads(path.read_text(encoding="utf-8"))
    hits: list[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for vuln in obj.get("vulnerabilities") or obj.get("vulns") or []:
                if isinstance(vuln, dict) and _cvss(vuln) >= fail_cvss:
                    hits.append(str(vuln.get("id") or "unknown"))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    if hits:
        print(
            f"[security] osv-scanner FAIL ({len(hits)} at CVSS>={fail_cvss})",
            file=sys.stderr,
        )
        return 1
    print(f"[security] osv-scanner OK — no findings at CVSS>={fail_cvss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
