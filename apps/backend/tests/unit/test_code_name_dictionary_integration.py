"""GET /api/v1/code-name-dictionary via TestClient.

[Corpus: api] Code name dictionary — real glossary export, not a stub payload.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

_PATH = "/api/v1/code-name-dictionary"
_ITEM_KEYS = frozenset({"id", "code", "meaning", "products", "countries", "wmo_amendment"})
_FACET_KEYS = frozenset({"products", "countries", "wmo_amendments"})


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _get(client: TestClient, params: dict[str, str] | None = None) -> dict[str, Any]:
    response = client.get(_PATH, params=params)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    return body


def _assert_item_shape(row: dict[str, Any]) -> None:
    assert set(row) >= _ITEM_KEYS
    assert isinstance(row["id"], str)
    assert row["id"]
    assert isinstance(row["code"], str)
    assert row["code"]
    assert isinstance(row["meaning"], str)
    assert isinstance(row["products"], list)
    assert all(isinstance(tag, str) for tag in row["products"])
    assert isinstance(row["countries"], list)
    assert all(isinstance(tag, str) for tag in row["countries"])
    assert row["wmo_amendment"] is None or isinstance(row["wmo_amendment"], str)


def _assert_facets(facets: object) -> None:
    assert isinstance(facets, dict)
    assert set(facets) >= _FACET_KEYS
    assert facets["products"]
    assert facets["countries"]
    assert facets["wmo_amendments"]
    assert all(isinstance(tag, str) and tag for tag in facets["products"])
    assert all(isinstance(tag, str) and tag for tag in facets["countries"])
    assert all(isinstance(tag, str) and tag for tag in facets["wmo_amendments"])


def test_code_name_dictionary_lists_items_and_facets(client: TestClient) -> None:
    body = _get(client)
    items = body["items"]
    assert isinstance(items, list)
    assert items
    for row in items:
        _assert_item_shape(row)
    _assert_facets(body["facets"])
    assert "VAA" in body["facets"]["products"]
    assert "INTL" in body["facets"]["countries"]
    assert "Amd 77" in body["facets"]["wmo_amendments"]


def test_code_name_dictionary_query_ts(client: TestClient) -> None:
    full = _get(client)
    body = _get(client, {"q": "TS"})
    items = body["items"]
    assert items
    assert len(items) < len(full["items"])
    assert any(row["code"] == "TS" for row in items)
    for row in items:
        _assert_item_shape(row)
        blob = f"{row['code']} {row['meaning']}".lower()
        assert "ts" in blob
    assert body["facets"] == full["facets"]


def test_code_name_dictionary_product_vaa(client: TestClient) -> None:
    full = _get(client)
    body = _get(client, {"product": "VAA"})
    items = body["items"]
    assert items
    assert len(items) < len(full["items"])
    assert any(row["code"] == "VAA" for row in items)
    for row in items:
        _assert_item_shape(row)
        assert "VAA" in row["products"]
    assert body["facets"] == full["facets"]


def test_code_name_dictionary_country_intl(client: TestClient) -> None:
    full = _get(client)
    body = _get(client, {"country": "INTL"})
    items = body["items"]
    assert items
    assert any(row["code"] == "TS" for row in items)
    for row in items:
        _assert_item_shape(row)
        assert "INTL" in row["countries"]
    intl_ids = {row["id"] for row in full["items"] if "INTL" in row["countries"]}
    assert {row["id"] for row in items} == intl_ids
    assert body["facets"] == full["facets"]


def test_code_name_dictionary_wmo_amendment_amd_77(client: TestClient) -> None:
    full = _get(client)
    body = _get(client, {"wmo_amendment": "Amd 77"})
    items = body["items"]
    assert items
    assert len(items) < len(full["items"])
    assert any(row["code"] == "VAA" for row in items)
    for row in items:
        _assert_item_shape(row)
        assert row["wmo_amendment"] == "Amd 77"
    assert body["facets"] == full["facets"]
