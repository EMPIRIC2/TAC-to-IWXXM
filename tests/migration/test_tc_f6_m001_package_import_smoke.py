"""TC-F6-M001 - empty package import smoke for F6 validate workspace members.

Spec: docs/test-plan.md §TC-F6-M001 (UJ-DEV-003b); execution-plan T1.1.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Distribution / directory names use hyphens; import packages use underscores where needed.
_PACKAGE_SPECS: tuple[tuple[str, str, str], ...] = (
    ("tac2iwxxm", "tac2iwxxm", "packages/tac2iwxxm"),
    ("iwxxm_validate", "iwxxm-validate", "packages/iwxxm-validate"),
    ("tac_validate", "tac-validate", "packages/tac-validate"),
)


@pytest.mark.migration
@pytest.mark.unit
class TestF6PackageImportSmoke:
    """Empty packages must import and be declared as uv workspace members."""

    @pytest.mark.parametrize(
        ("import_name", "dist_name", "rel_path"),
        _PACKAGE_SPECS,
        ids=[spec[1] for spec in _PACKAGE_SPECS],
    )
    def test_package_importable(
        self, import_name: str, dist_name: str, rel_path: str
    ) -> None:
        """Each F6 package root module imports and exposes __version__."""
        pkg_root = ROOT / rel_path
        assert pkg_root.is_dir(), f"missing package tree for {dist_name}: {pkg_root}"
        module = importlib.import_module(import_name)
        assert hasattr(module, "__version__")
        assert isinstance(module.__version__, str)
        assert module.__version__

    def test_uv_workspace_declares_three_f6_members(self) -> None:
        """Root pyproject lists all three packages as workspace members."""
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        for _, dist_name, rel_path in _PACKAGE_SPECS:
            assert rel_path in content, f"{rel_path} missing from workspace members"
            assert dist_name in content or dist_name.replace("-", "_") in content
