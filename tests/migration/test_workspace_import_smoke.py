"""TC-M001 workspace import smoke — test-plan.md TC-M001 step 2 subset."""

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

    def test_gifts_workspace_member_importable(self) -> None:
        module = importlib.import_module("gifts")
        assert hasattr(module, "metarEncoder")
        assert hasattr(module, "metarDecoder")

    def test_auth_workspace_member_importable(self) -> None:
        module = importlib.import_module("auth.security")
        assert hasattr(module, "create_access_token")
        assert hasattr(module, "decode_access_token")

    def test_uv_workspace_member_declared_in_root_pyproject(self) -> None:
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "packages/shared" in content
        assert "packages/gifts" in content
        assert "packages/auth" in content
        assert "metar-shared" in content
        assert "gifts = { workspace = true }" in content
        assert "metar-auth = { workspace = true }" in content

    def test_pnpm_workspace_discovers_shared_package(self) -> None:
        content = (ROOT / "pnpm-workspace.yaml").read_text(encoding="utf-8")
        assert "packages/*" in content
        shared_pkg = ROOT / "packages/shared/package.json"
        assert shared_pkg.exists()
        pkg = json.loads(shared_pkg.read_text(encoding="utf-8"))
        assert pkg["name"] == "@metar/shared"
