#!/usr/bin/env python3
"""Fail if declared direct dependencies use range operators (^ ~ >= > *) except allowlist.

Scans:
  - **/package.json dependencies + devDependencies + optionalDependencies
  - **/pyproject.toml project.dependencies + project.optional-dependencies
    + dependency-groups (PEP 735 / uv)

Workspace path deps listed under ``tool.uv.sources`` with ``workspace = true``
may be bare names (no version). Allowlist:
``scripts/ci/policy/exact-pins-allowlist.txt`` (one path:name or glob per line;
``#`` comments).
[Corpus: ] [Corpus: deps] [Corpus: tech-spec] TR-E04
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / "scripts" / "ci" / "policy" / "exact-pins-allowlist.txt"

RANGE_RE = re.compile(r"[\^~]|>=|>|<=|\*|^\s*$")
# PEP 508 markers / extras ok; flag version specs with ranges
PY_RANGE_RE = re.compile(r"(>=|<=|~=|\^|>[^|=]|<[^|=]|\*)")


def load_allowlist() -> set[str]:
    """Load allowlisted path:name keys for non-exact pins."""
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
    """Return True when a dependency is allowlisted."""
    key = f"{rel}:{name}"
    if key in allow or name in allow or rel in allow:
        return True
    for pattern in allow:
        if pattern.endswith(":*") and key.startswith(pattern[:-1]):
            return True
        if pattern.startswith("*:") and name == pattern[2:]:
            return True
    return False


def workspace_source_names(data: dict[str, Any]) -> set[str]:
    """Return package names declared as uv workspace path sources."""
    sources = (data.get("tool") or {}).get("uv", {}).get("sources") or {}
    names: set[str] = set()
    for name, spec in sources.items():
        if isinstance(spec, dict) and spec.get("workspace") is True:
            names.add(name)
    return names


def check_package_json(path: Path, allow: set[str], violations: list[str]) -> None:
    """Collect non-exact pins from a package.json."""
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
            if (
                s.startswith("file:")
                or s.startswith("workspace:")
                or s.startswith("link:")
            ):
                continue
            if RANGE_RE.search(s) or s.startswith(">") or s.startswith("<"):
                # exact: "1.2.3" or "1.2.3+meta" — reject ^1.2.3
                if s[0].isdigit() and not any(c in s for c in "^~*><"):
                    continue
                violations.append(f"{rel} {section} {name}={ver!r}")


def _check_py_req(
    rel: str,
    group: str,
    req: str,
    allow: set[str],
    workspace_names: set[str],
    violations: list[str],
) -> None:
    # strip markers
    base = req.split(";")[0].strip()
    # name[extras]==ver
    m = re.match(r"^([A-Za-z0-9_.-]+)(\[[^\]]+\])?(.*)$", base)
    if not m:
        return
    name, _extras, rest = m.group(1), m.group(2), m.group(3).strip()
    if allowed(allow, rel, name):
        return
    if name in workspace_names and not rest:
        return
    if not rest:
        violations.append(f"{rel} {group} {name} (unpinned)")
        return
    if PY_RANGE_RE.search(rest) or "," in rest:
        # allow exact == only
        if re.fullmatch(r"==[^,<=>~\^\*]+", rest):
            return
        violations.append(f"{rel} {group} {name}{rest!r}")


def check_pyproject(path: Path, allow: set[str], violations: list[str]) -> None:
    """Collect non-exact pins from a pyproject.toml."""
    rel = str(path.relative_to(ROOT))
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib # type: ignore

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    workspace_names = workspace_source_names(data)
    project = data.get("project") or {}
    deps = list(project.get("dependencies") or [])
    opt = project.get("optional-dependencies") or {}
    dep_groups = data.get("dependency-groups") or {}
    for group, items in [
        ("dependencies", deps),
        *[(f"optional-dependencies.{k}", v) for k, v in opt.items()],
        *[(f"dependency-groups.{k}", v) for k, v in dep_groups.items()],
    ]:
        for req in items:
            _check_py_req(rel, group, req, allow, workspace_names, violations)


def main() -> int:
    """Run the exact-pin check across the workspace."""
    allow = load_allowlist()
    violations: list[str] = []
    skip_dirs = {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        ".tools",
        ".security-reports",
        "dist",
        "build",
        # Local opt-in / gitignored trees (not part of the product pin surface)
        "third_party",
    }
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
            print(f" {v}", file=sys.stderr)
        print(
            "Use exact versions (== / no ^~>=). Allowlist: scripts/ci/policy/exact-pins-allowlist.txt",
            file=sys.stderr,
        )
        return 1
    print("exact-pin check PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
