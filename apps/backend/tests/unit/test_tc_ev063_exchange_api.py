"""TC-EV063-004 / TC-EV063-005 — exchange packaging (EV-063 / #921)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.exchange_registry import resolve_exchange_profile
from dissemination.handles import default_handle_store
from dissemination.packaging import apply_exchange_packaging, wrap_global_afs_collect
from dissemination.rate_limit import DisseminationRateLimiter
from fastapi.testclient import TestClient

from src import api as api_module
from src.routers import dissemination as diss_router
from src.utilities.abuse_controls import get_limiter
from src.utilities.security import verify_supabase_token

_SAMPLE_METAR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="uuid.test">
  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>
</iwxxm:METAR>"""

_BULLETIN_TEXT = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
"""


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    lim = DisseminationRateLimiter(max_per_minute=1000)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    default_handle_store.clear()

    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()
    default_handle_store.clear()
    get_limiter().reset()


def test_exchange_registry_resolves_global_afs() -> None:
    resolved = resolve_exchange_profile("GLOBAL_AFS")
    assert resolved is not None
    assert resolved.wire_id == "GLOBAL_AFS"
    assert resolved.canonical == "global_afs"


def test_wrap_global_afs_collect_adds_collect_root() -> None:
    packaged = wrap_global_afs_collect(_SAMPLE_METAR_XML, bulletin_identifier="A_TEST.xml")
    assert is_collect_bulletin(packaged)
    assert "collect:bulletinIdentifier" in packaged
    assert "A_TEST.xml" in packaged
    assert "iwxxm:METAR" in packaged


def test_apply_exchange_packaging_idempotent_for_collect() -> None:
    once = wrap_global_afs_collect(_SAMPLE_METAR_XML)
    twice = apply_exchange_packaging(once, exchange_profile="GLOBAL_AFS")
    assert twice == once


def test_tc_ev063_004_convert_bulletin_defaults_global_afs(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Package path without explicit exchange profile uses GLOBAL_AFS COLLECT wrap."""

    def fake_convert(tac: str, **kwargs):
        return _SAMPLE_METAR_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN_TEXT),
            "product": (None, "METAR"),
            "profile": (None, "annex3"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload["exchange_profile"] == "GLOBAL_AFS"
    xml = payload["results"][0]["xml"]
    assert xml
    assert is_collect_bulletin(xml)


def test_tc_ev063_004_explicit_global_afs_matches_default(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _SAMPLE_METAR_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    implicit = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN_TEXT),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    explicit = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN_TEXT),
            "product": (None, "METAR"),
            "exchange_profile": (None, "GLOBAL_AFS"),
            "lint": (None, "false"),
        },
    )
    assert implicit.status_code == 200 and explicit.status_code == 200
    assert implicit.json()["exchange_profile"] == explicit.json()["exchange_profile"] == "GLOBAL_AFS"
    assert is_collect_bulletin(implicit.json()["results"][0]["xml"])
    assert is_collect_bulletin(explicit.json()["results"][0]["xml"])


def test_tc_ev065_003_convert_bulletin_apac_robex(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-EV065-003 — convert-bulletin accepts APAC_ROBEX and COLLECT-wraps output."""

    def fake_convert(tac: str, **kwargs):
        return _SAMPLE_METAR_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN_TEXT),
            "product": (None, "METAR"),
            "exchange_profile": (None, "APAC_ROBEX"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload["exchange_profile"] == "APAC_ROBEX"
    xml = payload["results"][0]["xml"]
    assert xml
    assert is_collect_bulletin(xml)


def test_convert_only_does_not_apply_exchange_packaging(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Convert-only path must not default exchange profile or COLLECT-wrap output."""

    def fake_convert(tac: str, **kwargs):
        return _SAMPLE_METAR_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:400]
    xml = response.json()["results"][0]["content"]
    assert xml
    assert not is_collect_bulletin(xml)


def test_tc_ev063_005_exchange_profile_not_stored_in_dissemination_handle(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exchange profile selection does not persist BYOC credentials or profile ids in handles."""

    def fake_convert(tac: str, **kwargs):
        return _SAMPLE_METAR_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    bulletin = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN_TEXT),
            "product": (None, "METAR"),
            "exchange_profile": (None, "GLOBAL_AFS"),
            "lint": (None, "false"),
        },
    )
    assert bulletin.status_code == 200

    db_path = tmp_path / "dissem.db"
    uri = f"sqlite+aiosqlite:///{db_path}"
    preflight = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": uri,
                "ddl": True,
                "product": "metar",
                "params": {"note": "no exchange profile here"},
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert preflight.status_code == 200, preflight.text
    body = preflight.json()
    handle = body["handle"]
    assert handle
    assert "GLOBAL_AFS" not in json.dumps(body)
    stored = default_handle_store.get(handle, user_id="testclient")
    assert stored is not None
    assert "exchange_profile" not in stored.params
    assert "GLOBAL_AFS" not in json.dumps(stored.params)
