"""TC-EVBRIDGE-008/009 API — transforms on send, not convert-only; decoding seed."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token
from tac2iwxxm.library_assets import get_first_party_library_asset

_TAC = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="
_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="m1">'
    "<iwxxm:observation/></iwxxm:METAR>"
)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_tc_evbridge_008_convert_only_skips_dissemination_transforms(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:400]
    content = response.json()["results"][0]["content"]
    assert "MeteorologicalBulletin" not in content
    assert "dissemination-checksum" not in content


def test_tc_evbridge_008_convert_bulletin_applies_dissemination_library(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    xml = response.json()["results"][0]["xml"]
    assert xml is not None
    assert "MeteorologicalBulletin" in xml
    assert "dissemination-checksum" in xml


def test_tc_evbridge_009_decoding_library_seeded_from_decode_tac() -> None:
    asset = get_first_party_library_asset("LIB.DECODING.ICAO_2025")
    assert asset is not None
    assert asset.kind == "decoding"
    assert asset.body.get("seed") == "decode_tac"
    entries = asset.body.get("entries") or []
    assert len(entries) >= 10
    tokens = {row["token"] for row in entries}
    assert "TS" in tokens
    assert all(row.get("source") == "decode_tac" for row in entries)
