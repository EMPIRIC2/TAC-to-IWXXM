"""T2.7 / TC-F32-005 — VONA lint/convert + catalog GET smoke (UJ-045)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

_ANNEX3 = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden"


def _tac(name: str) -> str:
    return (_ANNEX3 / name).read_text(encoding="utf-8")


@pytest.fixture
def smoke_client():
    async def override_verify_token():
        return {"sub": "f32-vona-smoke-user", "aud": "test"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(api_module.app)
    yield client
    api_module.app.dependency_overrides.clear()


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def test_tc_f32_005_vona_lint_convert_smoke(smoke_client: TestClient) -> None:
    tac = _tac("vona_a7_1.tac")
    lint = _multipart(
        smoke_client,
        "/api/v1/lint-tac",
        {"manual_text": tac, "product": "vona"},
    )
    assert lint.status_code == 200, lint.text[:400]
    assert lint.json()["ok"] is True

    convert = _multipart(
        smoke_client,
        "/api/v1/convert",
        {
            "manual_text": tac,
            "product": "vona",
            "profile": "annex3",
            "lint": "false",
        },
    )
    assert convert.status_code == 200, convert.text[:800]
    results = convert.json().get("results") or []
    assert results
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "VolcanoObservatoryNoticeForAviation" in xml
    # Adjacency: VONA path must not emit SIGMET / VAA / SWXA sibling roots.
    assert "VolcanicAshAdvisory" not in xml
    assert "SpaceWeatherAdvisory" not in xml
    assert "iwxxm:SIGMET" not in xml


def test_tc_f32_005_lint_issue_catalog_vona(smoke_client: TestClient) -> None:
    response = smoke_client.get("/api/v1/lint-issue-catalog", params={"product": "vona"})
    assert response.status_code == 200, response.text[:400]
    body = response.json()
    assert isinstance(body.get("issues") or body.get("items") or body, (list, dict))
