"""Package layout and boundary smoke tests for packages/dissemination (T1.1 / ADR-030)."""

from __future__ import annotations

import ast
from importlib import metadata
from pathlib import Path

import dissemination

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SRC = PACKAGE_ROOT / "src" / "dissemination"


def test_package_importable_and_versioned() -> None:
    assert dissemination.__version__
    assert isinstance(dissemination.__version__, str)
    dist = metadata.version("dissemination")
    assert dist == dissemination.__version__


def test_package_src_layout_exists() -> None:
    assert PACKAGE_SRC.is_dir()
    assert (PACKAGE_SRC / "__init__.py").is_file()
    assert (PACKAGE_ROOT / "pyproject.toml").is_file()
    assert (PACKAGE_ROOT / "README.md").is_file()


def test_package_has_no_fastapi_or_supabase_imports() -> None:
    """ADR-030 — sinks live in the package; FastAPI/Supabase stay in apps/backend."""
    forbidden = {"fastapi", "supabase"}
    py_files = list(PACKAGE_SRC.rglob("*.py"))
    assert py_files, "expected dissemination package sources"
    for path in py_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".", 1)[0] not in forbidden, path
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".", 1)[0] not in forbidden, path
