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
_FE_PICKER_FILES = (
    _REPO_ROOT / "apps" / "frontend" / "src" / "app" / "components" / "UserPreferencesDialog.tsx",
    _REPO_ROOT / "apps" / "frontend" / "src" / "app" / "components" / "admin" / "SystemSettingsPanel.tsx",
)
_API_PY = _REPO_ROOT / "apps" / "backend" / "src" / "api.py"


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


def test_fe_picker_option_values_match_sot() -> None:
    """IWXXM version <select> option values must equal SoT version ids."""
    expected_ids = {str(v["id"]) for v in expected_sot_payload()["versions"]}  # type: ignore[index]
    select_ids = ("iwxxm-version", "default-iwxxm-version", "param-iwxxm-version")
    checked = 0
    for path in _FE_PICKER_FILES:
        text = path.read_text(encoding="utf-8")
        for select_id in select_ids:
            match = re.search(
                rf'id="{re.escape(select_id)}"[\s\S]*?</select>',
                text,
            )
            if match is None:
                continue
            found = set(re.findall(r'<option\s+value="([^"]+)"', match.group(0)))
            assert found == expected_ids, f"{path.name}#{select_id}: option values {found} != SoT {expected_ids}"
            checked += 1
    assert checked >= 2, "Expected at least two IWXXM version selects in FE picker files"


def test_api_form_default_matches_sot_default() -> None:
    """Multipart ``iwxxm_version`` Form defaults in api.py must match DEFAULT_VERSION."""
    text = _API_PY.read_text(encoding="utf-8")
    defaults = set(re.findall(r'iwxxm_version:\s*str\s*=\s*Form\(\s*default="([^"]+)"', text))
    assert defaults, "No iwxxm_version Form(default=...) found in api.py"
    assert defaults == {DEFAULT_VERSION}, f"Form defaults {defaults} != DEFAULT_VERSION {DEFAULT_VERSION}"
