"""TC-EVRPC-001..008 — rule catalogs + selection options (ADR-044)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.services import rule_catalogs as rule_catalogs_service

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


def test_rule_catalog_service_value_error_maps_to_400() -> None:
    with patch(
        "src.routers.rule_catalogs.catalog_for_family",
        side_effect=ValueError("boom"),
    ):
        response = client.get("/api/v1/rule-catalogs", params={"family": "tac"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_catalog_family"


def test_catalog_for_family_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown catalog family"):
        rule_catalogs_service.catalog_for_family("nope")


def test_selection_options_all_kinds() -> None:
    for kind in (
        "conversion",
        "tac_validation",
        "iwxxm_validation",
        "decoding",
        "dissemination",
    ):
        response = client.get("/api/v1/selection-options", params={"kind": kind})
        assert response.status_code == 200, kind
        body = response.json()
        assert body["kind"] == kind
        assert body["options"]
        prefix = f"LIB.{kind.upper()}."
        assert all(opt["id"].startswith(prefix) for opt in body["options"]), kind


def test_selection_options_unknown_kind_400() -> None:
    response = client.get("/api/v1/selection-options", params={"kind": "nope"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_selection_kind"


def test_library_authoring_create_gone() -> None:
    response = client.post(
        "/api/v1/profiles/library-assets",
        json={"kind": "conversion", "name": "x", "yaml_body": "rules: []"},
    )
    # May be 401/403 without auth, or 410 when reached — either way not 201.
    assert response.status_code in {401, 403, 410, 422}
    if response.status_code == 410:
        assert response.json()["detail"]["code"] == "library_authoring_retired"
