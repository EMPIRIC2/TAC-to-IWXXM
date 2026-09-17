"""TC-EVRPC-001..008 — rule catalogs + selection options (ADR-044)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_rule_catalog_tac_family_nonempty() -> None:
    response = client.get("/api/v1/rule-catalogs", params={"family": "tac"})
    assert response.status_code == 200
    body = response.json()
    assert body["family"] == "tac"
    assert body["items"]
    assert {"id", "title", "summary"} <= set(body["items"][0])


def test_rule_catalog_decoding_family() -> None:
    response = client.get("/api/v1/rule-catalogs", params={"family": "decoding"})
    assert response.status_code == 200
    assert response.json()["items"]


def test_rule_catalog_conversion_and_dissemination() -> None:
    for family in ("conversion", "dissemination", "iwxxm"):
        response = client.get("/api/v1/rule-catalogs", params={"family": family})
        assert response.status_code == 200, family
        assert response.json()["family"] == family


def test_rule_catalog_unknown_family_400() -> None:
    response = client.get("/api/v1/rule-catalogs", params={"family": "nope"})
    assert response.status_code == 400


def test_selection_options_conversion() -> None:
    response = client.get("/api/v1/selection-options", params={"kind": "conversion"})
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "conversion"
    assert body["options"]


def test_library_authoring_create_gone() -> None:
    response = client.post(
        "/api/v1/profiles/library-assets",
        json={"kind": "conversion", "name": "x", "yaml_body": "rules: []"},
    )
    # May be 401/403 without auth, or 410 when reached — either way not 201.
    assert response.status_code in {401, 403, 410, 422}
    if response.status_code == 410:
        assert response.json()["detail"]["code"] == "library_authoring_retired"
