"""Extended unit tests for schema discovery poller internals."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from src.config import iwxxm_versions
from src.services import schema_discovery_poller as sdp
from src.services.schema_discovery_poller import SchemaDiscoveryPoller


@pytest.mark.asyncio
async def test_emit_new_version_event_continues_on_callback_error(monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller()
    called = {"mirror": 0, "sync": 0, "async": 0}

    def bad_sync(_version, _url):
        called["sync"] += 1
        raise RuntimeError("sync callback fail")

    async def good_async(_version, _url):
        called["async"] += 1

    async def fake_trigger(_version, _url):
        called["mirror"] += 1

    poller.register_new_version_callback(bad_sync)
    poller.register_new_version_callback(good_async)
    poller.mirror_service = object()
    monkeypatch.setattr(poller, "_trigger_auto_mirror", fake_trigger)

    await poller._emit_new_version_event("2025-2", "https://schemas")

    assert called == {"mirror": 1, "sync": 1, "async": 1}


@pytest.mark.asyncio
async def test_trigger_auto_mirror_skips_when_version_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    mirror_service = SimpleNamespace(mirror_version=pytest.fail)
    poller = SchemaDiscoveryPoller(mirror_service=mirror_service)

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {})
    monkeypatch.setattr(iwxxm_versions, "RC_VERSIONS", {})

    await poller._trigger_auto_mirror("2099-1", "https://schemas")


@pytest.mark.asyncio
async def test_trigger_auto_mirror_success_and_analysis_called(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"mirror": 0, "analyze": 0}

    async def mirror_version(**kwargs):
        calls["mirror"] += 1
        assert kwargs["version"] == "2025-2"
        return {"xsd_count": 1, "example_count": 2, "xmi_count": 3}

    mirror_service = SimpleNamespace(mirror_version=mirror_version)
    poller = SchemaDiscoveryPoller(mirror_service=mirror_service)

    async def fake_analyze(_version):
        calls["analyze"] += 1

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": {"schema_url": "https://schemas/iwxxm.xsd"}})
    monkeypatch.setattr(iwxxm_versions, "RC_VERSIONS", {})
    monkeypatch.setattr(poller, "_analyze_breaking_changes", fake_analyze)

    await poller._trigger_auto_mirror("2025-2", "https://schemas")

    assert calls == {"mirror": 1, "analyze": 1}


@pytest.mark.asyncio
async def test_trigger_auto_mirror_skips_when_schema_url_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    mirror_service = SimpleNamespace(mirror_version=pytest.fail)
    poller = SchemaDiscoveryPoller(mirror_service=mirror_service)

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": {"name": "IWXXM 2025-2"}})
    monkeypatch.setattr(iwxxm_versions, "RC_VERSIONS", {})

    await poller._trigger_auto_mirror("2025-2", "https://schemas")


@pytest.mark.asyncio
async def test_trigger_auto_mirror_logs_and_swallows_mirror_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mirror_version(**_kwargs):
        raise RuntimeError("mirror failed")

    poller = SchemaDiscoveryPoller(mirror_service=SimpleNamespace(mirror_version=mirror_version))
    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": {"schema_url": "https://schemas/iwxxm.xsd"}})
    monkeypatch.setattr(iwxxm_versions, "RC_VERSIONS", {})

    await poller._trigger_auto_mirror("2025-2", "https://schemas")


@pytest.mark.asyncio
async def test_analyze_breaking_changes_updates_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller(xmi_analyzer=SimpleNamespace(), base_schema_path=tmp_path)

    old_xmi = tmp_path / "2023-1" / "XMI" / "IWXXM.xmi"
    new_xmi = tmp_path / "2025-2" / "XMI" / "IWXXM.xmi"
    old_xmi.parent.mkdir(parents=True)
    new_xmi.parent.mkdir(parents=True)
    old_xmi.write_text("old", encoding="utf-8")
    new_xmi.write_text("new", encoding="utf-8")

    report = {
        "total_changes": 1,
        "details": [
            SimpleNamespace(
                element="iwxxm:runwayState",
                xpath=".//iwxxm:runwayState",
                change_type="removed",
                reason="removed in new version",
            )
        ],
    }

    analyzer = SimpleNamespace(analyze_xmi_versions=lambda *_args: report)
    poller.xmi_analyzer = analyzer

    monkeypatch.setattr(
        iwxxm_versions,
        "SUPPORTED_VERSIONS",
        {
            "2023-1": {"breaking_changes_from_prior": {}},
            "2025-2": {"breaking_changes_from_prior": {}},
        },
    )

    await poller._analyze_breaking_changes("2025-2")

    changes = iwxxm_versions.SUPPORTED_VERSIONS["2025-2"]["breaking_changes_from_prior"]["2025-2"]
    assert changes[0]["action"] == "remove"


@pytest.mark.asyncio
async def test_analyze_breaking_changes_returns_when_previous_or_xmi_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    poller = SchemaDiscoveryPoller(xmi_analyzer=SimpleNamespace(), base_schema_path=tmp_path)

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": {}})
    await poller._analyze_breaking_changes("2025-2")

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2023-1": {}, "2025-2": {}})
    await poller._analyze_breaking_changes("2025-2")


@pytest.mark.asyncio
async def test_analyze_breaking_changes_returns_when_xmi_analyzer_missing(tmp_path: Path) -> None:
    poller = SchemaDiscoveryPoller(xmi_analyzer=None, base_schema_path=tmp_path)

    await poller._analyze_breaking_changes("2025-2")


@pytest.mark.asyncio
async def test_analyze_breaking_changes_value_error_and_old_xmi_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    poller = SchemaDiscoveryPoller(xmi_analyzer=SimpleNamespace(), base_schema_path=tmp_path)

    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2023-1": {}, "2025-2": {}})

    # Unknown version triggers the index lookup exception branch.
    await poller._analyze_breaking_changes("2099-1")

    # Known version with new XMI present but old XMI missing triggers old_xmi branch.
    new_xmi = tmp_path / "2025-2" / "XMI" / "IWXXM.xmi"
    new_xmi.parent.mkdir(parents=True)
    new_xmi.write_text("new", encoding="utf-8")

    await poller._analyze_breaking_changes("2025-2")


@pytest.mark.asyncio
async def test_analyze_breaking_changes_swallows_analyzer_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_xmi = tmp_path / "2023-1" / "XMI" / "IWXXM.xmi"
    new_xmi = tmp_path / "2025-2" / "XMI" / "IWXXM.xmi"
    old_xmi.parent.mkdir(parents=True)
    new_xmi.parent.mkdir(parents=True)
    old_xmi.write_text("old", encoding="utf-8")
    new_xmi.write_text("new", encoding="utf-8")

    analyzer = SimpleNamespace(analyze_xmi_versions=lambda *_args: (_ for _ in ()).throw(RuntimeError("boom")))
    poller = SchemaDiscoveryPoller(xmi_analyzer=analyzer, base_schema_path=tmp_path)
    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2023-1": {}, "2025-2": {}})

    await poller._analyze_breaking_changes("2025-2")


@pytest.mark.asyncio
async def test_poll_url_success_and_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeResponse:
        def __init__(self, text: str, status_code: int = 200):
            self.text = text
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                req = httpx.Request("GET", "https://example")
                resp = httpx.Response(self.status_code, request=req)
                raise httpx.HTTPStatusError("err", request=req, response=resp)

    class _FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url):
            return _FakeResponse('<a href="2025-2RC1/">2025-2RC1</a>')

    monkeypatch.setattr("src.services.schema_discovery_poller.httpx.AsyncClient", _FakeClient)

    poller = SchemaDiscoveryPoller()
    versions = await poller._poll_url("https://schemas")
    assert "2025-2RC1" in versions

    class _FailingClient(_FakeClient):
        async def get(self, _url):
            return _FakeResponse("", status_code=500)

    monkeypatch.setattr("src.services.schema_discovery_poller.httpx.AsyncClient", _FailingClient)

    with pytest.raises(httpx.HTTPError):
        await poller._poll_url("https://schemas")


def test_update_version_metadata_handles_missing_config(monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller()
    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {})

    poller._update_version_metadata("2025-2", "2023-1", {"details": []})


def test_update_version_metadata_reuses_existing_breaking_changes_map(monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller()
    config = {"breaking_changes_from_prior": {"2023-1": []}}
    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": config})

    report = {
        "details": [
            SimpleNamespace(element="foo", xpath=None, change_type="changed", reason="changed"),
        ]
    }

    poller._update_version_metadata("2025-2", "2024-1", report)

    assert config["breaking_changes_from_prior"]["2024-1"][0]["action"] == "change"
    assert config["breaking_changes_from_prior"]["2024-1"][0]["xpath"] == ".//iwxxm:foo"


def test_update_version_metadata_swallows_report_shape_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller()
    monkeypatch.setattr(iwxxm_versions, "SUPPORTED_VERSIONS", {"2025-2": {"breaking_changes_from_prior": {}}})

    poller._update_version_metadata("2025-2", "2023-1", {"details": [object()]})


def test_extract_versions_from_html_weird_match_shapes(monkeypatch: pytest.MonkeyPatch) -> None:
    poller = SchemaDiscoveryPoller()

    class _FakeVersionPattern:
        def findall(self, _html):
            return ["not-a-tuple", ("2025", "2")]

        def search(self, full_link):
            if "has-no-version" in full_link:
                return None
            return SimpleNamespace(group=lambda _idx=0: "2026-1")

    class _FakeRCPattern:
        def findall(self, _html):
            return ["bad-rc-shape", ("2025", "2", "RC3")]

    class _FakeLinkPattern:
        def finditer(self, _html):
            return [
                SimpleNamespace(group=lambda idx: "has-no-version"),
                SimpleNamespace(group=lambda idx: "path/2026-1/"),
            ]

    monkeypatch.setattr(sdp, "VERSION_PATTERN", _FakeVersionPattern())
    monkeypatch.setattr(sdp, "RC_PATTERN", _FakeRCPattern())
    monkeypatch.setattr(sdp.re, "compile", lambda *_args, **_kwargs: _FakeLinkPattern())

    versions = poller._extract_versions_from_html("irrelevant")

    assert "2025-2RC3" in versions
    assert "2026-1" in versions


@pytest.mark.asyncio
async def test_poll_with_retry_raises_after_all_attempts_fail() -> None:
    poller = SchemaDiscoveryPoller()

    async def always_fail():
        raise RuntimeError("always fails")

    poller.poll_once = always_fail

    with pytest.raises(RuntimeError):
        await poller.poll_with_retry(max_retries=1, retry_delay_seconds=0)


@pytest.mark.asyncio
async def test_poll_with_retry_zero_retries_returns_none() -> None:
    poller = SchemaDiscoveryPoller()

    result = await poller.poll_with_retry(max_retries=0, retry_delay_seconds=0)

    assert result is None


@pytest.mark.asyncio
async def test_discover_schemas_convenience_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_poll_once(self):
        return {"new_stable": ["2025-2"], "new_rc": [], "poll_time": "x", "total_discovered": 1}

    monkeypatch.setattr(sdp.SchemaDiscoveryPoller, "poll_once", fake_poll_once)

    result = await sdp.discover_schemas()

    assert result["new_stable"] == ["2025-2"]


@pytest.mark.asyncio
async def test_discover_schemas_with_retry_convenience_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_poll_with_retry(self, max_retries, retry_delay):
        assert max_retries == 4
        assert retry_delay == 2
        return {"new_stable": [], "new_rc": ["2025-2RC1"], "poll_time": "x", "total_discovered": 1}

    monkeypatch.setattr(sdp.SchemaDiscoveryPoller, "poll_with_retry", fake_poll_with_retry)

    result = await sdp.discover_schemas_with_retry(max_retries=4, retry_delay=2)

    assert result["new_rc"] == ["2025-2RC1"]
