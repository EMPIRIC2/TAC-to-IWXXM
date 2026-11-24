"""Drop-guard: G-AIRMET map layer + national profile HTTP reject (FR-012/013/019..022).

[Corpus: fr] epic #1688
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.routers.live_map import MAP_PRODUCTS, get_live_map_cache, router, set_live_map_cache


def test_gairmet_not_in_map_products() -> None:
    """G-AIRMET is removed from live-map product ids (FR-013)."""
    assert "gairmet" not in MAP_PRODUCTS
    assert "airmet" in MAP_PRODUCTS


def test_gairmet_query_returns_400(monkeypatch: pytest.MonkeyPatch) -> None:
    """Requesting products=gairmet fails closed with 400."""
    monkeypatch.delenv("LIVE_MAP_CACHE_URL", raising=False)
    set_live_map_cache(None)
    _ = get_live_map_cache()
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get(
        "/api/v1/live-map",
        params={
            "west": -80,
            "south": 40,
            "east": -70,
            "north": 41,
            "products": "gairmet",
        },
    )
    assert response.status_code == 400
    set_live_map_cache(None)


@pytest.mark.parametrize(
    "library_id",
    [
        "LIB.CONVERSION.US_FAA_NWS",
        "LIB.CONVERSION.CA_ECCC",
        "LIB.CONVERSION.AU_BOM",
        "LIB.CONVERSION.NZ_CAA_MET",
    ],
)
def test_convert_rejects_national_library_ids_http(library_id: str) -> None:
    """POST /convert rejects dropped national conversion library ids."""
    from src.api import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/convert",
        data={
            "tac": "METAR KJFK 221953Z 18010KT 10SM FEW050 22/12 A3012=",
            "product": "METAR",
            "conversion_library_id": library_id,
        },
    )
    assert response.status_code in {400, 422}, response.text[:500]
    text = response.text.lower()
    assert "library" in text or "profile" in text or "unsupported" in text or "unknown" in text
