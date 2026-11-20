"""Unit + regression coverage for scripts/iwxxm/probe_msc_datamart_drift.py (#1036).

Matrix: offline/live success, committed validation failures, live drift failures,
HTTP listing faults. [Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

import json
import runpy
import sys
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import scripts.iwxxm.probe_msc_datamart_drift as mod

ROOT = Path(__file__).resolve().parents[2]
_COMMITTED = (
    ROOT / "packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/ops_datamart_probe.json"
)


def _probe_payload(**overrides: object) -> dict[str, object]:
    base = json.loads(_COMMITTED.read_text(encoding="utf-8"))
    base.update(overrides)
    return base


def test_offline_main_success(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Read/query happy path: committed probe validates offline."""
    assert mod.main([]) == 0
    out = capsys.readouterr().out
    assert "MSC datamart drift OK (offline)" in out
    assert "ops_datamart_probe.json" in out


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (
            lambda p: p["products"].__setitem__(
                "taf", {"http_status": 500, "children": ["cwao"]}
            ),
            "taf expected HTTP 200",
        ),
        (
            lambda p: p["products"].__setitem__(
                "airmet", {"http_status": 200, "children": []}
            ),
            "airmet missing children",
        ),
        (
            lambda p: p["products"].__setitem__(
                "metar", {"http_status": 200, "children": []}
            ),
            "metar expected documented HTTP 404",
        ),
        (
            lambda p: p["schema"].__setitem__("children", ["common-ca.xsd"]),
            "schema missing",
        ),
        (lambda p: p.__setitem__("blocker_note", "   "), "missing blocker_note"),
    ],
    ids=[
        "live-product-status",
        "missing-issuers",
        "blocker-lifted-on-disk",
        "schema-gap",
        "blank-blocker-note",
    ],
)
def test_validate_committed_failure_modes(
    mutate: object,
    needle: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation failure: each committed-probe invariant rejects independently."""
    probe = _probe_payload()
    mutate(probe)  # type: ignore[operator]
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(probe), encoding="utf-8")
    assert mod.main(["--probe-json", str(path)]) == 1
    err = capsys.readouterr().err
    assert "MSC datamart drift FAIL" in err
    assert needle in err


def test_fetch_listing_success_and_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Listing parse success + HTTPError status return."""
    html = '<html><a href="taf/">taf</a><a href="?q=1">q</a><a href="/abs">a</a></html>'
    resp = MagicMock()
    resp.read.return_value = html.encode("utf-8")
    resp.status = 200
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda *_a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)
    status, hrefs = mod._fetch_listing("https://example.test/")
    assert status == 200
    assert hrefs == ["taf"]

    def _boom(*_a: object, **_k: object) -> None:
        raise urllib.error.HTTPError(
            "https://example.test/x", 404, "missing", hdrs=None, fp=None
        )

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    status404, empty = mod._fetch_listing("https://example.test/x")
    assert status404 == 404
    assert empty == []


def test_live_main_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Live success: expected trees present, blocked products stay 404."""
    probe_path = tmp_path / "probe.json"
    probe_path.write_text(_COMMITTED.read_text(encoding="utf-8"), encoding="utf-8")

    def _fake_fetch(url: str, *, timeout: float = 30.0) -> tuple[int, list[str]]:
        _ = timeout
        if url.endswith("/iwxxm/"):
            return 200, ["airmet", "schema", "sigmet", "taf"]
        if url.endswith("/taf/"):
            return 200, ["cwao"]
        if url.endswith("/airmet/"):
            return 200, ["czeg"]
        if url.endswith("/sigmet/"):
            return 200, ["czeg"]
        if url.endswith("/schema/"):
            return 200, sorted(mod._EXPECTED_SCHEMA)
        if any(url.endswith(f"/{name}/") for name in mod._BLOCKED_PRODUCTS):
            return 404, []
        return 500, []

    monkeypatch.setattr(mod, "_fetch_listing", _fake_fetch)
    assert mod.main(["--probe-json", str(probe_path), "--live"]) == 0
    assert "MSC datamart drift OK (live)" in capsys.readouterr().out


def _live_listing_map(scenario: str) -> dict[str, tuple[int, list[str]]]:
    """URL-suffix -> (status, children) for one live failure scenario."""
    schema = sorted(mod._EXPECTED_SCHEMA)
    root = ["airmet", "schema", "sigmet", "taf"]
    if scenario == "missing-product":
        root = ["airmet", "schema", "sigmet"]
    listings: dict[str, tuple[int, list[str]]] = {
        "/iwxxm/": (200, root),
        "/taf/": (200, ["cwao"]),
        "/airmet/": (200, ["czeg"]),
        "/sigmet/": (200, ["czeg"]),
        "/metar/": (404, []),
        "/speci/": (404, []),
        "/vaa/": (404, []),
        "/schema/": (200, schema),
    }
    overrides: dict[str, dict[str, tuple[int, list[str]]]] = {
        "root-down": {"/iwxxm/": (503, [])},
        "product-http": {"/taf/": (500, [])},
        "product-empty": {"/taf/": (200, [])},
        "blocker-lifted": {"/metar/": (200, ["cwao"])},
        "blocker-odd-status": {"/metar/": (418, [])},
        "schema-down": {"/schema/": (503, [])},
        "schema-missing": {"/schema/": (200, ["common-ca.xsd"])},
        "schema-extra": {"/schema/": (200, [*schema, "extra-ca.xsd"])},
    }
    listings.update(overrides.get(scenario, {}))
    return listings


@pytest.mark.parametrize(
    ("scenario", "needle"),
    [
        ("root-down", "live datamart root HTTP 503"),
        ("missing-product", "expected product tree 'taf'"),
        ("product-http", "taf/ HTTP 500"),
        ("product-empty", "taf/ empty issuer listing"),
        ("blocker-lifted", "metar/ now HTTP 200"),
        ("blocker-odd-status", "metar/ unexpected HTTP 418"),
        ("schema-down", "schema/ HTTP 503"),
        ("schema-missing", "schema missing"),
        ("schema-extra", "schema unexpected files"),
    ],
)
def test_live_failure_modes(
    scenario: str,
    needle: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Live failure / drift permutations."""
    probe_path = tmp_path / "probe.json"
    probe_path.write_text(_COMMITTED.read_text(encoding="utf-8"), encoding="utf-8")
    listings = _live_listing_map(scenario)

    def _fake_fetch(url: str, *, timeout: float = 30.0) -> tuple[int, list[str]]:
        _ = timeout
        for suffix, payload in listings.items():
            if url.endswith(suffix):
                return payload
        return 404, []

    monkeypatch.setattr(mod, "_fetch_listing", _fake_fetch)
    assert mod.main(["--probe-json", str(probe_path), "--live"]) == 1
    assert needle in capsys.readouterr().err


def test_validate_committed_direct_success() -> None:
    """Validation success helper on the committed fixture."""
    probe = json.loads(_COMMITTED.read_text(encoding="utf-8"))
    assert mod._validate_committed(probe) == []


def test_main_entrypoint_runpy(monkeypatch: pytest.MonkeyPatch) -> None:
    """__main__ offline success via runpy."""
    script = ROOT / "scripts/iwxxm/probe_msc_datamart_drift.py"
    monkeypatch.setattr(sys, "argv", [str(script)])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(script), run_name="__main__")
    assert exc.value.code == 0
