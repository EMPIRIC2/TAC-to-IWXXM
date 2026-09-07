"""TC-EV071-003 - API pre-convert CA lint wire (EV-071 M1 / FR-L6).

[Corpus: api] [Corpus: tests §TC-EV071]
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

_CA_METAR_SECTOR = "METAR CYUL 231800Z 24010KT 2SM BR BKN008 14/13 A2995 RMK VIS 3/4 NE="
_CA_IWXXM_VERSION = "3.0.0"


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert_files(**fields: tuple[None, str]) -> dict:
    base = {
        "manual_text": (None, _CA_METAR_SECTOR),
        "product": (None, "METAR"),
        "iwxxm_version": (None, _CA_IWXXM_VERSION),
        "lint": (None, "true"),
    }
    base.update(fields)
    return base


def test_tc_ev071_003_convert_echoes_ca_lint_codes(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(semantic_profile=(None, "CA_ECCC")),
    )
    assert response.status_code == 200, response.text[:500]
    assert seen
    assert seen[0].get("profile") == "ca_eccc"

    issue_codes = {row.get("code") for row in response.json().get("issues", [])}
    assert "CA_STATUTE_MILE_VIS" in issue_codes
    assert "CA_REMARK_SECTOR_VIS" in issue_codes


def test_tc_ev071_003_annex3_convert_no_ca_codes(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda tac, **kwargs: ("<iwxxm:METAR/>", None),
    )

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "ICAO_2025"),
            iwxxm_version=(None, "2025-2"),
        ),
    )
    assert response.status_code == 200, response.text[:500]
    issue_codes = {row.get("code") for row in response.json().get("issues", [])}
    assert not any(str(code).startswith("CA_") for code in issue_codes)
