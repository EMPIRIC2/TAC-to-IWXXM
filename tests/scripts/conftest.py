# EV-080 M4 — scripts Python unit harness helpers.
"""Load script modules (incl. hyphen path files) for coverage."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_INVENTORY_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures"

_STUB_ROOTS = (
    "tac_validate",
    "wmo_official_tac_inventory",
    "tests.migration",
)


def load_script(rel_path: str, module_name: str | None = None) -> ModuleType:
    """Import ``scripts/<rel_path>`` by file path (works for hyphen dirs)."""
    path = REPO_ROOT / "scripts" / rel_path
    if not path.is_file():
        raise FileNotFoundError(path)
    name = (
        module_name
        or f"ev080_scripts_{path.stem}_{abs(hash(path.as_posix())) & 0xFFFF}"
    )
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _ensure_real_wmo_inventory() -> None:
    """Rebind the fixture inventory module after stub teardown.

    ``OfficialTacPeer`` remains alive after ``sys.modules`` stubs are removed.
    xsdata's dataclass context then KeyErrors on ``wmo_official_tac_inventory``
    during real codegen (``test_generate_version_success``).
    """
    name = "wmo_official_tac_inventory"
    existing = sys.modules.get(name)
    if existing is not None and getattr(existing, "__file__", None):
        return
    path = _INVENTORY_FIXTURES / f"{name}.py"
    if not path.is_file():
        return
    fixtures = str(_INVENTORY_FIXTURES)
    if fixtures not in sys.path:
        sys.path.insert(0, fixtures)
    sys.modules.pop(name, None)
    importlib.import_module(name)


def _purge_stub_modules() -> None:
    """Drop in-memory stub modules so later tests can import real packages."""
    for name in list(sys.modules):
        if not (
            name in _STUB_ROOTS
            or any(name.startswith(f"{root}.") for root in _STUB_ROOTS)
            or name == "iwxxm_validate"
            or name.startswith("iwxxm_validate.")
        ):
            continue
        mod = sys.modules[name]
        path = getattr(mod, "__file__", None)
        # Real packages have a filesystem path; bare ModuleType / SimpleNamespace stubs do not.
        if path is None:
            del sys.modules[name]
            continue
        # Empty-path namespace stubs (``__path__ = []``) used by quality-metrics tests.
        pkg_path = getattr(mod, "__path__", None)
        if pkg_path == []:
            del sys.modules[name]
    _ensure_real_wmo_inventory()


@pytest.fixture(autouse=True)
def _ev080_scripts_stub_cleanup() -> None:
    _purge_stub_modules()
    yield
    _purge_stub_modules()
