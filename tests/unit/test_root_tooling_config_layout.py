"""Root tooling configs live under config/tooling and config/sbom."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestRootToolingConfigLayout:
    def test_tooling_files_exist(self) -> None:
        tooling = ROOT / "config" / "tooling"
        assert (tooling / "prettier.json").is_file()
        assert (tooling / "prettierignore").is_file()
        assert (tooling / "eslint.config.js").is_file()
        assert (tooling / "yamllint.yml").is_file()
        assert (tooling / "gitleaks.toml").is_file()

    def test_root_no_longer_hosts_moved_tool_configs(self) -> None:
        assert not (ROOT / ".prettierrc").exists()
        assert not (ROOT / "eslint.config.js").exists()
        assert not (ROOT / ".yamllint.yml").exists()
        assert not (ROOT / ".gitleaks.toml").exists()
        assert not (ROOT / "sbom").exists()
        # Prettier only applies ignore patterns from a cwd-root file; keep a symlink.
        ignore = ROOT / ".prettierignore"
        assert ignore.is_symlink()
        assert ignore.resolve() == (ROOT / "config" / "tooling" / "prettierignore").resolve()

    def test_package_json_points_at_tooling(self) -> None:
        data = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        assert data.get("prettier") == "./config/tooling/prettier.json"
        assert "config/tooling/prettier.json" in data["scripts"]["format:check"]
        assert "config/tooling/eslint.config.js" in data["scripts"]["lint:js"]

    def test_sbom_under_config(self) -> None:
        assert (ROOT / "config" / "sbom" / "cyclonedx.json").is_file()
        assert (ROOT / "config" / "sbom" / "requirements.frozen.txt").is_file()
