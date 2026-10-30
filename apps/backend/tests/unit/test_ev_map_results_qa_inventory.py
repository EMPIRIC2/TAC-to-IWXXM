"""TC-F37-013 inventory locks for EV-map-results-qa.

[Corpus: product §F37] [Corpus: product §F28] [Corpus: adr/ADR-052] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.routers.live_map import MAP_PRODUCTS, get_live_map_cache, router, set_live_map_cache

# Keep in sync with apps/frontend LIVE_MAP_VIEWS product ids (TC-F37-013).
_EXPECTED_PIN_PRODUCTS = frozenset({"metar", "speci", "taf", "airmet", "gairmet", "sigmet", "vaa", "tca", "vona"})

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SWXA_FIXTURES = (
    _REPO_ROOT / "apps/frontend/src/fixtures/examples/bodies/swxa_a7_3.tac",
    _REPO_ROOT / "apps/frontend/src/fixtures/examples/bodies/swxa_a7_4.tac",
    _REPO_ROOT / "apps/frontend/src/fixtures/examples/bodies/swxa_a7_5.tac",
    _REPO_ROOT / "packages/tac2iwxxm/tests/fixtures/annex3_golden/swxa_a7_3.tac",
)


def test_map_pin_products_match_f37_inventory() -> None:
    """Live-map pin ids stay the nine geographically located products."""
    assert MAP_PRODUCTS == _EXPECTED_PIN_PRODUCTS
    assert "swxa" not in MAP_PRODUCTS
    assert "wafs" not in MAP_PRODUCTS
    assert "qvaci" not in MAP_PRODUCTS


def test_swxa_fixtures_exist_for_offline_map_qa() -> None:
    """Space-weather samples stay available for offline evaluation (choice a)."""
    missing = [str(path) for path in _SWXA_FIXTURES if not path.is_file()]
    assert missing == [], f"missing SWXA fixtures: {missing}"
    sample = _SWXA_FIXTURES[0].read_text(encoding="utf-8")
    assert "SWX ADVISORY" in sample


def test_live_map_space_weather_key_present_and_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Response keeps space_weather as an empty list until a feed ships."""
    monkeypatch.delenv("LIVE_MAP_CACHE_URL", raising=False)
    set_live_map_cache(None)
    _ = get_live_map_cache()
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get(
        "/api/v1/live-map",
        params={"west": -180, "south": -90, "east": 180, "north": 90},
    )
    assert response.status_code == 200
    body = response.json()
    assert "places" in body
    assert body["space_weather"] == []
    set_live_map_cache(None)


def test_swxa_rejected_as_map_layer(monkeypatch: pytest.MonkeyPatch) -> None:
    """SWXA is convert-only; requesting it as a pin layer is a 400."""
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
            "products": "swxa",
        },
    )
    assert response.status_code == 400
    assert "map layers" in response.json()["detail"].lower()
    set_live_map_cache(None)
