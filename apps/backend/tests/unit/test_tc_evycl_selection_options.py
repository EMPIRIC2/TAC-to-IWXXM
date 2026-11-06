"""TC-EVYCL — selection-options return first-party LIB.* ids (#1251 / TP-YCL-01)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.services import rule_catalogs as rule_catalogs_service

client = TestClient(app)

_CONVERT_KINDS = (
    "conversion",
    "tac_validation",
    "iwxxm_validation",
    "decoding",
)

_ALL_KINDS = (*_CONVERT_KINDS, "dissemination")


@pytest.mark.parametrize("kind", _ALL_KINDS)
def test_tc_evycl_selection_options_lib_ids(kind: str) -> None:
    """Each kind returns non-empty LIB.{KIND}.* options."""
    response = client.get("/api/v1/selection-options", params={"kind": kind})
    assert response.status_code == 200, kind
    body = response.json()
    assert body["kind"] == kind
    assert body["options"]
    prefix = f"LIB.{kind.upper()}."
    for opt in body["options"]:
        assert opt["id"].startswith(prefix), opt
        assert opt["label"]


def test_tc_evycl_selection_options_service_unit() -> None:
    """Service helper filters first-party assets by kind."""
    rows = rule_catalogs_service.selection_options("tac_validation")
    assert rows
    assert all(r["id"].startswith("LIB.TAC_VALIDATION.") for r in rows)


def test_tc_evycl_selection_options_unknown_still_400() -> None:
    response = client.get("/api/v1/selection-options", params={"kind": "nope"})
    assert response.status_code == 400
