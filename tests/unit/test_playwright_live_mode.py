"""Playwright live-mode config checks (TC-LIVE-004)."""

from __future__ import annotations

from pathlib import Path


def test_playwright_config_disables_webserver_for_remote_base_url() -> None:
    """Remote HTTPS base URL must skip local webServer (H6 live harness)."""
    config_path = (
        Path(__file__).resolve().parents[2] / "apps" / "e2e" / "playwright.config.ts"
    )
    content = config_path.read_text(encoding="utf-8")

    assert "function isRemoteBaseUrl" in content
    assert "const remotePlaywright = isRemoteBaseUrl(configuredBaseUrl)" in content
    assert "...(remotePlaywright" in content or "remotePlaywright\n    ? {}" in content
    assert "webServer:" in content
