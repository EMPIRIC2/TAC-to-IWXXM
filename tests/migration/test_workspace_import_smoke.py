"""TC-M001 workspace import smoke — post gifts cutover + Auth restore (F31)."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.migration
class TestWorkspaceImportSmoke:
    """Verify uv and pnpm workspace members resolve from repo root."""

    def test_uv_workspace_member_importable(self) -> None:
        module = importlib.import_module("metar_shared")
        assert hasattr(module, "METAR_CORS_ORIGINS_ENV")
        assert module.METAR_CORS_ORIGINS_ENV == "METAR_CORS_ORIGINS"

    def test_tac2iwxxm_workspace_member_importable(self) -> None:
        module = importlib.import_module("tac2iwxxm")
        assert callable(getattr(module, "convert", None))

    def test_auth_package_importable_as_metar_auth(self) -> None:
        module = importlib.import_module("metar_auth")
        assert callable(getattr(module, "verify_access_token", None))
        assert callable(getattr(module, "create_auth_router", None))

    def test_uv_workspace_member_declared_in_root_pyproject(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/shared" in content
        assert "packages/tac2iwxxm" in content
        assert "packages/auth" in content
        assert "packages/gifts" not in content
        assert "metar-shared" in content
        assert "tac2iwxxm = { workspace = true }" in content
        assert "metar-auth" in content

    def test_pnpm_workspace_discovers_shared_package(self) -> None:
        content = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
        assert "packages/*" in content
        shared_pkg = ROOT / "packages/shared/package.json"
        assert shared_pkg.exists()
        pkg = json.loads(shared_pkg.read_text(encoding="utf-8"))
        assert pkg["name"] == "@metar/shared"
