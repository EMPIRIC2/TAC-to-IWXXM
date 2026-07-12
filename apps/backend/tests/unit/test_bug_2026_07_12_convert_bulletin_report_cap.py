"""Advisory coverage: convert-bulletin caps report fan-out (PR #711 / PRR-018 A1)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_bulletin_rejects_too_many_reports(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Bulletins above MAX_BULLETIN_REPORTS must 400 before per-report convert."""
    meta = MagicMock()
    meta.ahl = "SAUS31 KZNY 121200"
    meta.report_count = api_module.MAX_BULLETIN_REPORTS + 1
    meta.tt = "SA"
    meta.aa = "US"
    meta.cccc = "KZNY"
    meta.yygggg = "121200"
    meta.bbb = None

    split = MagicMock()
    split.meta = meta
    split.reports = ["METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="] * meta.report_count

    monkeypatch.setattr(api_module, "tac2iwxxm_split_bulletin", lambda *_a, **_k: split)

    called = {"convert": False}

    def boom(*_a, **_k):
        called["convert"] = True
        raise AssertionError("convert must not run when over report cap")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", boom)

    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, "SAUS31 KZNY 121200\nMETAR KJFK 121151Z=\n"),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "too_many_reports"
    assert called["convert"] is False
