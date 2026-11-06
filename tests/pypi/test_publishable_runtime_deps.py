"""Publishable package Requires-Dist must resolve on PyPI (F12-F14).

Wheels that declare unpublished workspace-only packages fail clean-venv smoke
and leave consumers unable to ``pip install``. Keep every direct runtime dep
either on the known third-party allowlist or in the publish matrix.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Packages built by .github/workflows/pypi-publish.yml (tag / dispatch matrix).
PUBLISH_MATRIX: frozenset[str] = frozenset(
    {
        "tac-validate",
        "iwxxm-validate",
        "tac2iwxxm",
        "tac-decoding",
        "metar-shared",
        "reference-lookup",
    }
)

# Direct deps that already exist on public indexes (not monorepo members).
THIRD_PARTY: frozenset[str] = frozenset(
    {
        "hydra-core",
        "httpx",
        "lxml",
        "msgspec",
        "pyyaml",
    }
)

_DEP_NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")

_PUBLISHABLE_PYPROJECTS: dict[str, Path] = {
    "tac-validate": REPO_ROOT / "packages" / "tac-validate" / "pyproject.toml",
    "iwxxm-validate": REPO_ROOT / "packages" / "iwxxm-validate" / "pyproject.toml",
    "tac2iwxxm": REPO_ROOT / "packages" / "tac2iwxxm" / "pyproject.toml",
    "tac-decoding": REPO_ROOT / "packages" / "tac-decoding" / "pyproject.toml",
    "metar-shared": REPO_ROOT / "packages" / "shared" / "pyproject.toml",
    "reference-lookup": REPO_ROOT / "packages" / "reference-lookup" / "pyproject.toml",
}


def _dep_name(req: str) -> str:
    match = _DEP_NAME_RE.match(req.strip())
    assert match is not None, f"unparseable requirement: {req!r}"
    return match.group(1).lower().replace("_", "-")


@pytest.mark.parametrize("package", sorted(PUBLISH_MATRIX))
def test_publishable_runtime_deps_are_public(package: str) -> None:
    """Every Required-Dist name is third-party or itself publishable."""
    path = _PUBLISHABLE_PYPROJECTS[package]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps = data.get("project", {}).get("dependencies", [])
    assert data["project"]["name"] == package
    for req in deps:
        name = _dep_name(req)
        assert name in THIRD_PARTY or name in PUBLISH_MATRIX, (
            f"{package} depends on {name!r} which is neither a known third-party "
            f"package nor in the PyPI publish matrix {sorted(PUBLISH_MATRIX)}"
        )
