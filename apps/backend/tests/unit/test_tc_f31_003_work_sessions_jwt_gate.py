"""T2.4 / TC-F31-003 - work-sessions JWT gate + convert stays public."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_work_sessions_without_bearer_is_unauthorized() -> None:
    from src.api import app

    client = TestClient(app)
    assert client.get("/api/v1/work-sessions").status_code in (401, 403)
    assert client.post("/api/v1/work-sessions", json={"product": "metar"}).status_code in (
        401,
        403,
    )


@pytest.mark.unit
def test_convert_still_works_without_authorization() -> None:
    from src import api as api_module

    api_module.app.dependency_overrides.clear()
    client = TestClient(api_module.app)
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 121851Z 09014KT 10SM FEW250 22/14 A3015=",
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "validate_output": "false",
        },
    )
    assert response.status_code == 200
