"""H5 runtime config gate — validates /config.json contract (ADR-010, S003)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_config_profile(name: str) -> dict[str, object]:
    path = ROOT / "config" / f"{name}.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.parametrize("profile", ["local", "prod", "e2e"])
def test_config_profiles_have_required_runtime_keys(profile: str) -> None:
    """Each committed config profile must satisfy the runtime /config.json contract."""
    cfg = _load_config_profile(profile)
    for key in ("environment", "api", "supabase"):
        assert key in cfg, f"{profile}.json missing top-level key {key!r}"

    api = cfg["api"]
    assert isinstance(api, dict)
    assert api.get("baseUrl")
    assert api.get("frontendUrl")
    assert isinstance(api.get("corsOrigins"), list)

    supabase = cfg["supabase"]
    assert isinstance(supabase, dict)
    assert supabase.get("url")


def test_e2e_profile_enables_auth_for_playwright() -> None:
    """Playwright UJ-003 UI specs require auth-enabled runtime config."""
    cfg = _load_config_profile("e2e")
    api = cfg["api"]
    assert isinstance(api, dict)
    assert api.get("disableAuth") is False


def test_prod_profile_disables_auth_bypass() -> None:
    """Production runtime config must not bypass authentication."""
    cfg = _load_config_profile("prod")
    api = cfg["api"]
    assert isinstance(api, dict)
    assert api.get("disableAuth") is False


def test_h5_api_base_url_matches_live_e2e() -> None:
    """prod.json api.baseUrl must match liveE2e.apiUrl for H5 staging checks."""
    cfg = _load_config_profile("prod")
    api = cfg["api"]
    live = cfg.get("liveE2e")
    assert isinstance(api, dict)
    assert isinstance(live, dict)
    assert str(api.get("baseUrl", "")).rstrip("/") == str(
        live.get("apiUrl", "")
    ).rstrip("/")
