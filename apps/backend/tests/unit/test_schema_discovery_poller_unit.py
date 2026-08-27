"""Unit tests for schema discovery poller branches."""

from __future__ import annotations

import pytest
from src.services import schema_discovery_poller as sdp
from src.services.schema_discovery_poller import SchemaDiscoveryPoller


@pytest.mark.asyncio
async def test_poll_once_detects_stable_and_rc(monkeypatch):
    poller = SchemaDiscoveryPoller(poll_urls=["u1", "u2"])

    async def fake_poll_url(url):
        return ["2025-2RC1"] if url == "u1" else ["2025-2", "2025-2RC1"]

    seen = []

    async def fake_emit(version, source_url):
        seen.append((version, source_url))

    monkeypatch.setattr(poller, "_poll_url", fake_poll_url)
    monkeypatch.setattr(poller, "_emit_new_version_event", fake_emit)

    result = await poller.poll_once()

    assert result["new_stable"] == ["2025-2"]
    assert result["new_rc"] == ["2025-2RC1"]
    assert poller.last_poll_time is not None
    assert len(seen) == 2


@pytest.mark.asyncio
async def test_poll_once_continues_on_url_error(monkeypatch):
    poller = SchemaDiscoveryPoller(poll_urls=["bad", "good"])

    async def fake_poll_url(url):
        if url == "bad":
            raise RuntimeError("boom")
        return ["2023-1"]

    monkeypatch.setattr(poller, "_poll_url", fake_poll_url)
    monkeypatch.setattr(poller, "_emit_new_version_event", lambda *_args, **_kwargs: None)

    result = await poller.poll_once()

    assert result["new_stable"] == ["2023-1"]


@pytest.mark.asyncio
async def test_emit_new_version_invokes_sync_and_async_callbacks(monkeypatch):
    poller = SchemaDiscoveryPoller()
    calls = []

    async def async_cb(version, source):
        calls.append(("async", version, source))

    def sync_cb(version, source):
        calls.append(("sync", version, source))

    poller.register_new_version_callback(async_cb)
    poller.register_new_version_callback(sync_cb)
    monkeypatch.setattr(poller, "_trigger_auto_mirror", lambda *_args, **_kwargs: None)

    await poller._emit_new_version_event("2025-2", "https://schemas")

    assert ("async", "2025-2", "https://schemas") in calls
    assert ("sync", "2025-2", "https://schemas") in calls


@pytest.mark.asyncio
async def test_poll_with_retry_succeeds_after_retry(monkeypatch):
    poller = SchemaDiscoveryPoller()
    calls = {"count": 0}

    async def fake_poll_once():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("first fail")
        return {"new_stable": [], "new_rc": [], "poll_time": "", "total_discovered": 0}

    async def fake_sleep(_seconds):
        return None

    monkeypatch.setattr(poller, "poll_once", fake_poll_once)
    monkeypatch.setattr(sdp.asyncio, "sleep", fake_sleep)

    result = await poller.poll_with_retry(max_retries=2, retry_delay_seconds=0)

    assert calls["count"] == 2
    assert result["total_discovered"] == 0


def test_extract_versions_from_html_and_helpers():
    poller = SchemaDiscoveryPoller()
    html = """
    <a href=\"2025-2/\">2025-2</a>
    <a href=\"2025-2RC1/\">2025-2RC1</a>
    <a href=\"2023-1/\">2023-1</a>
    """

    versions = poller._extract_versions_from_html(html)

    assert "2025-2" in versions
    assert "2025-2RC1" in versions
    assert poller._is_rc_version("2025-2RC1") is True
    assert poller._is_rc_version("2025-2") is False
    assert sdp.extract_version_from_url("https://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd") == "2025-2RC1"


def test_get_discovered_versions_channel_filters():
    poller = SchemaDiscoveryPoller()
    poller.discovered_versions = {"2025-2", "2025-2RC1", "2023-1"}

    stable = poller.get_discovered_versions("stable")
    rc = poller.get_discovered_versions("rc")
    all_versions = poller.get_discovered_versions(None)

    assert "2025-2RC1" not in stable
    assert rc == ["2025-2RC1"]
    assert set(all_versions) == poller.discovered_versions
