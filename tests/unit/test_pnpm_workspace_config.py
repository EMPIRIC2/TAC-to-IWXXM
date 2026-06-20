"""Unit tests for pnpm workspace configuration (T1.3)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestPnpmWorkspaceConfig:
    """pnpm-workspace.yaml satisfies spec.md §Repository and ADR-005."""

    def test_pnpm_workspace_file_exists(self) -> None:
        assert (ROOT / "pnpm-workspace.yaml").exists()

    def test_pnpm_workspace_includes_packages_and_apps_globs(self) -> None:
        content = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
        assert "packages/*" in content
        assert "apps/*" in content

    def test_root_package_json_pins_node_22(self) -> None:
        import json

        data = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        node_engine = data.get("engines", {}).get("node", "")
        assert "22" in node_engine

    def test_root_package_json_declares_pnpm_package_manager(self) -> None:
        import json

        data = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        assert data.get("packageManager", "").startswith("pnpm@")
