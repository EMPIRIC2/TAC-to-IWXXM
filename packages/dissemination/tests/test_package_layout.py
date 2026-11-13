"""Package layout and boundary smoke tests for packages/dissemination (T1.1 / ADR-030)."""

from __future__ import annotations

import ast
import tomllib
from importlib import metadata
from pathlib import Path

from dissemination.models import PreflightRequest

import dissemination
from dissemination import (
    load_allowlist_from_env,
    parse_allowlist,
    validate_egress_host,
    writer_contract_ddl,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SRC = PACKAGE_ROOT / "src" / "dissemination"
PYPI_NAME = "iwxxm-dissemination"


def test_package_importable_and_versioned() -> None:
    assert dissemination.__version__
    assert isinstance(dissemination.__version__, str)
    dist = metadata.version(PYPI_NAME)
    assert dist == dissemination.__version__


def test_pyproject_pypi_identity() -> None:
    data = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    assert project["name"] == PYPI_NAME
    assert project["version"] == dissemination.__version__
    assert project["requires-python"] == ">=3.12"
    assert "src/dissemination" in data["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]


def test_public_imports_for_library_consumers() -> None:
    allow = parse_allowlist("example.org")
    validate_egress_host("example.org", allowlist=allow)
    assert writer_contract_ddl("sqlite")
    assert callable(load_allowlist_from_env)
    assert PreflightRequest is not None


def test_package_src_layout_exists() -> None:
    assert PACKAGE_SRC.is_dir()
    assert (PACKAGE_SRC / "__init__.py").is_file()
    assert (PACKAGE_ROOT / "pyproject.toml").is_file()
    assert (PACKAGE_ROOT / "README.md").is_file()
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    assert "pip install iwxxm-dissemination" in readme
    assert "import path" in readme.lower() or "`dissemination`" in readme


def test_package_has_no_fastapi_or_supabase_imports() -> None:
    """ADR-030 - sinks live in the package; FastAPI/Supabase stay in apps/backend."""
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
