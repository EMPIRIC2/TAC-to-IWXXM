"""UJ-069 / TC-EV063-009 — semantic convert → exchange package API path (EV-063 M9).

[Corpus: journeys §UJ-069] [Corpus: tests §TC-EV063] [Corpus: api]
"""

from __future__ import annotations

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.handles import default_handle_store
from dissemination.rate_limit import DisseminationRateLimiter
from fastapi.testclient import TestClient

from src import api as api_module
from src.routers import dissemination as diss_router
from src.utilities.abuse_controls import get_limiter
from src.utilities.security import verify_supabase_token

_SAMPLE_US_XML = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
  xmlns:iwxxm-us="http://nws.noaa.gov/schemas/iwxxm-us/3.0"
  gml:id="uuid.uj069">
  <iwxxm-us:Addendum><iwxxm-us:humanReadableText>RMK slice</iwxxm-us:humanReadableText></iwxxm-us:Addendum>
  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>
</iwxxm:METAR>"""

_TAC = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP149="
_BULLETIN = f"SAUS31 KZNY 121200\n{_TAC}"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    lim = DisseminationRateLimiter(max_per_minute=1000)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    default_handle_store.clear()

    async def override_verify_token():
        return {"sub": "uj069-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()
    default_handle_store.clear()
    get_limiter().reset()


def test_uj069_semantic_convert_then_exchange_package(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Convert with US_FAA_NWS then package bulletin with GLOBAL_AFS (no live sink)."""

    def fake_convert(tac: str, **kwargs):
        profile = kwargs.get("profile") or kwargs.get("semantic_profile")
        assert profile in {"US_FAA_NWS", "us_faa_nws", "iwxxm_us"}
        return _SAMPLE_US_XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    convert_resp = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "semantic_profile": (None, "US_FAA_NWS"),
            "lint": (None, "false"),
        },
    )
    assert convert_resp.status_code == 200, convert_resp.text[:400]
    convert_body = convert_resp.json()
    assert convert_body["results"][0]["content"]
    assert not is_collect_bulletin(convert_body["results"][0]["content"])

    package_resp = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _BULLETIN),
            "product": (None, "METAR"),
            "semantic_profile": (None, "US_FAA_NWS"),
            "exchange_profile": (None, "GLOBAL_AFS"),
            "lint": (None, "false"),
        },
    )
    assert package_resp.status_code == 200, package_resp.text[:400]
    package_body = package_resp.json()
    assert package_body["exchange_profile"] == "GLOBAL_AFS"
    xml = package_body["results"][0]["xml"]
    assert xml and is_collect_bulletin(xml)
    assert "iwxxm-us:Addendum" in xml or "iwxxm:METAR" in xml
