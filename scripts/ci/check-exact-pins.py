#!/usr/bin/env python3
"""Fail if declared direct dependencies use range operators (^ ~ >= > *) except allowlist.

Scans:
  - **/package.json  dependencies + devDependencies + optionalDependencies
  - **/pyproject.toml project.dependencies + project.optional-dependencies

Allowlist: config/exact-pins-allowlist.txt (one path:name or glob per line; # comments).
[Corpus: adr-037] [Corpus: deps]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / "config" / "exact-pins-allowlist.txt"

RANGE_RE = re.compile(r"[\^~]|>=|>|<=|\*|^\s*$")
# PEP 508 markers / extras ok; flag version specs with ranges
PY_RANGE_RE = re.compile(r"(>=|<=|~=|\^|>[^|=]|<[^|=]|\*)")


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.is_file():
        return set()
    out: set[str] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line)
    return out


def allowed(allow: set[str], rel: str, name: str) -> bool:
    key = f"{rel}:{name}"
    if key in allow or name in allow or rel in allow:
        return True
    for pattern in allow:
        if pattern.endswith(":*") and key.startswith(pattern[:-1]):
            return True
        if pattern.startswith("*:") and name == pattern[2:]:
            return True
    return False


def check_package_json(path: Path, allow: set[str], violations: list[str]) -> None:
    rel = str(path.relative_to(ROOT))
    data = json.loads(path.read_text(encoding="utf-8"))
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = data.get(section) or {}
        if not isinstance(deps, dict):
            continue
        for name, ver in deps.items():
            if allowed(allow, rel, name):
                continue
            s = str(ver).strip()
            if s.startswith("file:") or s.startswith("workspace:") or s.startswith("link:"):
                continue
            if RANGE_RE.search(s) or s.startswith(">") or s.startswith("<"):
                # exact: "1.2.3" or "1.2.3+meta" — reject ^1.2.3
                if s[0].isdigit() and not any(c in s for c in "^~*><"):
                    continue
                violations.append(f"{rel} {section} {name}={ver!r}")


def check_pyproject(path: Path, allow: set[str], violations: list[str]) -> None:
    rel = str(path.relative_to(ROOT))
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project") or {}
    deps = list(project.get("dependencies") or [])
    opt = project.get("optional-dependencies") or {}
    for group, items in [("dependencies", deps), *[(f"optional-dependencies.{k}", v) for k, v in opt.items()]]:
        for req in items:
            # strip markers
            base = req.split(";")[0].strip()
            # name[extras]==ver
            m = re.match(r"^([A-Za-z0-9_.-]+)(\[[^\]]+\])?(.*)$", base)
            if not m:
                continue
            name, _extras, rest = m.group(1), m.group(2), m.group(3).strip()
            if allowed(allow, rel, name):
                continue
            if not rest:
                violations.append(f"{rel} {group} {name} (unpinned)")
                continue
            if PY_RANGE_RE.search(rest) or "," in rest:
                # allow exact == only
                if re.fullmatch(r"==[^,<=>~\^\*]+", rest):
                    continue
                violations.append(f"{rel} {group} {name}{rest!r}")


def main() -> int:
    allow = load_allowlist()
    violations: list[str] = []
    skip_dirs = {".git", "node_modules", ".venv", "venv", ".tools", ".security-reports", "dist", "build"}
    for path in ROOT.rglob("package.json"):
        if any(p in skip_dirs for p in path.parts):
            continue
        check_package_json(path, allow, violations)
    for path in ROOT.rglob("pyproject.toml"):
        if any(p in skip_dirs for p in path.parts):
            continue
        check_pyproject(path, allow, violations)
    if violations:
        print("exact-pin check FAILED:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(
            "Use exact versions (== / no ^~>=). Allowlist: config/exact-pins-allowlist.txt",
            file=sys.stderr,
        )
        return 1
    print("exact-pin check PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
