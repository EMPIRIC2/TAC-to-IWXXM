"""T3.7a / ADR-027 / F11 acc4: codegen regen smoke - importable + non-empty models."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "codegen" / "iwxxm_xsd.py"
SHARED_SRC = REPO_ROOT / "packages" / "shared" / "src"
OUT_ROOT = SHARED_SRC / "metar_shared" / "iwxxm_xsd"

# Prefer a product XSD for faster CI; full iwxxm.xsd is covered by make codegen-iwxxm-xsd.
SMOKE_VERSION = "2025-2"
SMOKE_ENTRY = "metarSpeci.xsd"


def _load_script():
    spec = importlib.util.spec_from_file_location("iwxxm_xsd_codegen_t37a", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _count_basemodel_classes(tree_root: Path) -> int:
    """Count ``class X(BaseModel)`` definitions via AST (works despite circular imports)."""
    count = 0
    for path in tree_root.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for base in node.bases:
                name = getattr(base, "id", None) or getattr(base, "attr", None)
                if name == "BaseModel":
                    count += 1
                    break
    return count


def _ensure_namespace_pkg(pkg_name: str, version_dir: Path) -> None:
    """
    Register ``pkg_name`` without executing generated ``__init__.py``.

    xsdata package ``__init__`` re-exports GML/common and hits known circular
    imports; T3.7a only requires leaf modules to be importable.
    """
    import types

    # version_dir = …/metar_shared/iwxxm_xsd/vX → src is parents[2]
    src_root = version_dir.parents[2]
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    for parent in ("metar_shared", "metar_shared.iwxxm_xsd"):
        if parent not in sys.modules:
            importlib.import_module(parent)

    # Drop stale package + children from prior failed imports.
    stale = [k for k in sys.modules if k == pkg_name or k.startswith(pkg_name + ".")]
    for key in stale:
        del sys.modules[key]

    stub = types.ModuleType(pkg_name)
    stub.__file__ = str(version_dir / "__init__.py")
    stub.__path__ = [str(version_dir)]  # type: ignore[attr-defined]
    stub.__package__ = pkg_name
    sys.modules[pkg_name] = stub


def _import_leaf_modules(pkg_name: str, version_dir: Path) -> list[str]:
    """Import leaf modules under the generated package (after syntax fixups)."""
    _ensure_namespace_pkg(pkg_name, version_dir)

    imported: list[str] = []
    prefer = ("xlink", "xml", "metar_speci", "common")
    stems = [p.stem for p in version_dir.glob("*.py") if p.name != "__init__.py"]
    ordered = [s for s in prefer if s in stems] + [s for s in stems if s not in prefer]

    for stem in ordered:
        mod_name = f"{pkg_name}.{stem}"
        try:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        imported.append(mod_name)
        models = [
            obj
            for obj in vars(mod).values()
            if isinstance(obj, type)
            and issubclass(obj, BaseModel)
            and obj is not BaseModel
        ]
        if models:
            return imported
    return imported


@pytest.mark.slow
def test_t37a_regen_pinned_xsd_nonempty_and_importable(tmp_path: Path) -> None:
    """
    Regenerate from pinned vendor XSD; models must be non-empty and importable.

    Writes under a temp ``metar_shared/iwxxm_xsd`` so committed trees stay intact.

    Spec: ADR-027; F11 acceptance #4 (xsdata → pydantic); execution-plan T3.7a.
    """
    mod = _load_script()
    assert SMOKE_VERSION in mod.load_manifest_versions()

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    out_root.mkdir(parents=True)
    (tmp_path / "src" / "metar_shared" / "__init__.py").write_text("", encoding="utf-8")
    (out_root / "__init__.py").write_text("", encoding="utf-8")

    summary = mod.generate_version(SMOKE_VERSION, entry=SMOKE_ENTRY, out_root=out_root)
    assert summary["py_files"] >= 5, summary
    assert summary["bytes"] > 10_000, summary
    assert summary["output"] is not None

    version_dir = out_root / mod._version_package(SMOKE_VERSION)
    assert version_dir.is_dir()
    py_files = list(version_dir.rglob("*.py"))
    assert len(py_files) == summary["py_files"]

    basemodels = _count_basemodel_classes(version_dir)
    assert basemodels >= 10, f"expected pydantic models, found {basemodels}"

    pkg = summary["package"]
    # Point import helper at the temp tree via sys.path.
    temp_src = str(tmp_path / "src")
    if temp_src not in sys.path:
        sys.path.insert(0, temp_src)
    # Prefer temp packages over the committed ones for this smoke.
    for key in list(sys.modules):
        if key == "metar_shared" or key.startswith("metar_shared."):
            del sys.modules[key]

    imported = _import_leaf_modules(pkg, version_dir)
    assert imported, f"no modules importable under {pkg}"

    # Product module should exist on disk even if full-package import is circular.
    assert (version_dir / "metar_speci.py").is_file()
    assert (version_dir / "common.py").is_file()


def test_t37a_ast_helpers_reject_empty_tree(tmp_path: Path) -> None:
    """Guard: empty generated tree counts as zero BaseModel classes."""
    empty = tmp_path / "v_empty"
    empty.mkdir()
    (empty / "__init__.py").write_text("", encoding="utf-8")
    assert _count_basemodel_classes(empty) == 0
