"""TC-EV1308-001 (partial M1) — rule-catalog additive fields pass through DTO.

Full decoding metadata lands in M2; this locks RuleCatalogItem additive keys.
[Corpus: api] [Corpus: tests] #1308
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from src.api import app
from src.routers.rule_catalogs import RuleCatalogItem

client = TestClient(app)

_ADDITIVE_ROW = {
    "id": "TS",
    "title": "TS",
    "summary": "thunderstorm",
    "severity": "info",
    "tags": ["decoding", "glossary"],
    "issue_type": "content",
    "source_url": "https://example.invalid/codes",
    "source_attribution": "WMO code list (cite-only)",
    "source_access": "public",
    "source_locator": "weather phenomena",
    "conform_note": "TAC hazard abbreviation",
}


def test_rule_catalog_item_preserves_additive_optional_fields() -> None:
    item = RuleCatalogItem.model_validate(_ADDITIVE_ROW)
    assert item.issue_type == "content"
    assert item.source_url == "https://example.invalid/codes"
    assert item.source_attribution == "WMO code list (cite-only)"
    assert item.source_access == "public"
    assert item.source_locator == "weather phenomena"
    assert item.conform_note == "TAC hazard abbreviation"
    assert item.severity == "info"


def test_rule_catalog_item_additive_fields_default_null() -> None:
    item = RuleCatalogItem.model_validate(
        {"id": "X", "title": "X", "summary": "y", "tags": []},
    )
    assert item.issue_type is None
    assert item.source_url is None
    assert item.source_attribution is None
    assert item.source_access is None
    assert item.source_locator is None
    assert item.conform_note is None


def test_rule_catalog_http_passes_additive_fields() -> None:
    with patch(
        "src.routers.rule_catalogs.catalog_for_family",
        return_value=[_ADDITIVE_ROW],
    ):
        response = client.get("/api/v1/rule-catalogs", params={"family": "decoding"})
    assert response.status_code == 200
    row = response.json()["items"][0]
    assert row["issue_type"] == "content"
    assert row["source_url"] == "https://example.invalid/codes"
    assert row["source_attribution"] == "WMO code list (cite-only)"
    assert row["source_access"] == "public"
    assert row["source_locator"] == "weather phenomena"
    assert row["conform_note"] == "TAC hazard abbreviation"
    assert row["severity"] == "info"
