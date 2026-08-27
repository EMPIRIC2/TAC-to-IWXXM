"""
SoT drift CI for IWXXM supported versions (S046 / EV-038 / #851 / TC-EV038-004).

Python ``iwxxm_versions.py`` is the runtime source of truth. A generated committed
JSON artifact must match it; FE picker options and API Form defaults must agree.

Path lock (T2.1): ``apps/frontend/src/generated/iwxxm_versions.json``
Shape: ``{ "default": "<id>", "versions": [{"id", "role": "latest"|"previous"}] }``
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.config.iwxxm_versions import DEFAULT_VERSION, SUPPORTED_VERSIONS

_REPO_ROOT = Path(__file__).resolve().parents[4]
GENERATED_JSON = _REPO_ROOT / "apps" / "frontend" / "src" / "generated" / "iwxxm_versions.json"
# EV-040: UserPreferencesDialog no longer hosts IWXXM version (workbench FileConverter does).
_FE_PICKER_FILES = (
    _REPO_ROOT / "apps" / "frontend" / "src" / "app" / "components" / "admin" / "SystemSettingsPanel.tsx",
    _REPO_ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.tsx",
)
_API_SOURCES = (
    _REPO_ROOT / "apps" / "backend" / "src" / "api.py",
    _REPO_ROOT / "apps" / "backend" / "src" / "routers" / "conversion.py",
    _REPO_ROOT / "apps" / "backend" / "src" / "routers" / "comprehensive_validation.py",
)
_FE_SOT_UTIL = _REPO_ROOT / "apps" / "frontend" / "src" / "utils" / "iwxxmVersions.ts"


def expected_sot_payload() -> dict[str, object]:
    """Build the locked JSON shape from Python SoT ``status`` → ``role``."""
    versions: list[dict[str, str]] = []
    for version_id, meta in SUPPORTED_VERSIONS.items():
        role = str(meta.get("status", ""))
        assert role in {"latest", "previous"}, f"{version_id}: status must be latest|previous"
        versions.append({"id": version_id, "role": role})
    return {"default": DEFAULT_VERSION, "versions": versions}


def test_generated_json_exists_and_matches_python_sot() -> None:
    """Committed JSON must exist and match Python SUPPORTED_VERSIONS + DEFAULT."""
    assert GENERATED_JSON.is_file(), (
        f"Missing {GENERATED_JSON.relative_to(_REPO_ROOT)}; run: make export-iwxxm-versions (T2.2 / #851)"
    )
    loaded = json.loads(GENERATED_JSON.read_text(encoding="utf-8"))
    assert loaded == expected_sot_payload()


def test_fe_pickers_render_options_from_sot_module() -> None:
    """FE pickers must import SoT helpers (not hardcoded version lists)."""
    util = _FE_SOT_UTIL.read_text(encoding="utf-8")
    assert "generated/iwxxm_versions.json" in util
    assert "IWXXM_VERSION_OPTIONS" in util
    assert "iwxxmVersionOptionsForProfile" in util
    assert "Latest" in util and "Previous" in util

    for path in _FE_PICKER_FILES:
        text = path.read_text(encoding="utf-8")
        assert "iwxxmVersions" in text, f"{path.name} must import iwxxmVersions SoT module"
        if path.name == "FileConverter.tsx":
            assert "iwxxmVersionOptionsForProfile" in text, (
                f"{path.name} must use profile-scoped iwxxmVersionOptionsForProfile"
            )
        else:
            assert "IWXXM_VERSION_OPTIONS" in text, f"{path.name} must use IWXXM_VERSION_OPTIONS"


def test_api_form_default_matches_sot_default() -> None:
    """Multipart ``iwxxm_version`` Form defaults in API routes must match DEFAULT_VERSION."""
    defaults: set[str] = set()
    for path in _API_SOURCES:
        text = path.read_text(encoding="utf-8")
        defaults.update(re.findall(r'iwxxm_version:\s*str\s*=\s*Form\(\s*default="([^"]+)"', text))
    assert defaults, "No iwxxm_version Form(default=...) found in API route modules"
    assert defaults == {DEFAULT_VERSION}, f"Form defaults {defaults} != DEFAULT_VERSION {DEFAULT_VERSION}"
