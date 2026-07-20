#!/usr/bin/env python3
"""Hard-fail (when strict) on ad-hoc severity literals in tac-validate rule modules.

Pre-commit / CI helper for F15 (ADR-028). Set ``ISSUE_REGISTRY_GUARD_STRICT=1``
(T2.2a) to exit non-zero on hits; without it, prints WARN and exits 0.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_SEVERITY_LIT = re.compile(
    r"""severity\s*=\s*['"](?:error|warning|info)['"]"""
    r"""|severity\s*:\s*['"](?:error|warning|info)['"]""",
    re.IGNORECASE,
)

_SKIP = ("issue_registry", "registry.py", "models.py", "conftest.py", "/tests/")


def _should_scan(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    if "packages/tac-validate/" not in s or not s.endswith(".py"):
        return False
    lower = s.lower()
    return not any(p in lower for p in _SKIP)


def main(argv: list[str]) -> int:
    strict = os.environ.get("ISSUE_REGISTRY_GUARD_STRICT", "").strip() in {
        "1",
        "true",
        "yes",
    }
    files = [Path(a) for a in argv[1:]] or []
    findings: list[str] = []
    for path in files:
        if not _should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _SEVERITY_LIT.search(line):
                findings.append(
                    f"{path}:{i}: severity literal — use issue registry (F15/ADR-028)"
                )

    if findings:
        mode = "ERROR" if strict else "WARN"
        print(f"[issue-registry-guard:{mode}] {len(findings)} hit(s):")
        for f in findings[:20]:
            print(f"  {f}")
        if len(findings) > 20:
            print(f"  … +{len(findings) - 20} more")
        if strict:
            return 1
        print("  (advisory — set ISSUE_REGISTRY_GUARD_STRICT=1 for hard-fail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
