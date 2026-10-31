"""BUG-2026-10-30 — expand F3 aerodrome registry for live-map UNKNOWN_ICAO stations.

[Corpus: product §F3]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api import app  # noqa: E402
from src.schemas import airport as airport_mod  # noqa: E402
from src.schemas.airport import AirportValidator  # noqa: E402

# Representative probe ICAOs: CA AUTO, digit US, major US with empty OurAirports icao_code.
_PROBE_ICAOS = ("CWDQ", "K10U", "KHUF")

_SUPPLEMENTS = BACKEND_ROOT / "src" / "data" / "airport_registry_supplements.json"


def _reload_validator() -> AirportValidator:
    AirportValidator._instance = None
    AirportValidator._loaded = False
    AirportValidator._airports.clear()
    airport_mod._validator_instance = None
    return AirportValidator()


@pytest.fixture
def airport_validator() -> AirportValidator:
    return _reload_validator()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_bug_2026_10_30_supplements_file_lists_probe_icaos() -> None:
    """Supplement registry must list the campaign UNKNOWN_ICAO probe set."""
    assert _SUPPLEMENTS.is_file(), f"missing {_SUPPLEMENTS}"
    payload = json.loads(_SUPPLEMENTS.read_text(encoding="utf-8"))
    stations = payload.get("stations") or []
    by_icao = {row["icao"].upper(): row for row in stations}
    for icao in _PROBE_ICAOS:
        assert icao in by_icao, icao
        coords = by_icao[icao].get("coordinates") or {}
        assert coords.get("latitude") is not None
        assert coords.get("longitude") is not None


@pytest.mark.parametrize("icao", _PROBE_ICAOS)
def test_bug_2026_10_30_probe_icao_known_to_validator(
    airport_validator: AirportValidator, icao: str
) -> None:
    """Probe stations must be known; digit ICAOs must not be rejected as non-alpha."""
    assert airport_validator.validate_icao(icao) is True
    airport = airport_validator.get_airport(icao)
    assert airport is not None
    assert airport.coordinates is not None
    assert airport.coordinates.latitude is not None
    assert airport.coordinates.longitude is not None


@pytest.mark.parametrize(
    ("icao", "tac"),
    [
        ("CWDQ", "METAR CWDQ 302100Z AUTO 34008KT 9999 05/02 Q1013="),
        ("K10U", "METAR K10U 302100Z AUTO 00000KT 10SM CLR 10/M02 A2992="),
        ("KHUF", "METAR KHUF 302100Z 27008KT 10SM FEW050 18/08 A3012="),
    ],
)
def test_bug_2026_10_30_convert_omits_unknown_icao(
    client: TestClient, icao: str, tac: str
) -> None:
    """Convert for supplemented stations must not emit UNKNOWN_ICAO."""
    # Ensure singleton sees supplements (other tests may have loaded earlier).
    _reload_validator()
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": tac,
            "product": "METAR",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "iwxxm_version": "2025-2",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    codes = [i.get("code") for i in payload.get("issues") or []]
    assert "UNKNOWN_ICAO" not in codes, (icao, codes)


def test_bug_2026_10_30_truly_unknown_icao_still_soft_warns(
    client: TestClient,
) -> None:
    """Stations absent from OurAirports + supplements still emit UNKNOWN_ICAO."""
    _reload_validator()
    assert AirportValidator().validate_icao("ZZ99") is False
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR ZZ99 302100Z 27008KT 10SM FEW050 18/08 A3012=",
            "product": "METAR",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "iwxxm_version": "2025-2",
        },
    )
    assert response.status_code == 200, response.text
    codes = [i.get("code") for i in response.json().get("issues") or []]
    assert "UNKNOWN_ICAO" in codes
