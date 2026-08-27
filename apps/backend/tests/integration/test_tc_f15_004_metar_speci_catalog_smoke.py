"""T5.5 / TC-F15-004 - METAR + SPECI lint/convert + catalog GET smoke (H3-shaped).

Spec: docs/test-plan.md TC-F15-004; docs/api-contract.md §lint-issue-catalog;
execution-plan T5.5. In-process authenticated client (CI); live H3 reuses same paths.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.utilities.security import verify_supabase_token
from tac_validate.issue_registry import ISSUES

pytestmark = [pytest.mark.integration, pytest.mark.smoke]

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac-validate" / "tests" / "fixtures" / "accept"
METAR_TAC = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
SPECI_TAC = (FIXTURES / "speci_basic.tac").read_text(encoding="utf-8").strip()


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "f15-smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


@pytest.mark.parametrize(
    ("product", "tac"),
    [
        ("METAR", METAR_TAC),
        ("SPECI", SPECI_TAC),
    ],
)
def test_tc_f15_004_lint_and_convert_smoke(
    smoke_client: TestClient,
    product: str,
    tac: str,
) -> None:
    lint = _multipart_post(
        smoke_client,
        "/api/v1/lint-tac",
        {"manual_text": tac, "product": product},
    )
    assert lint.status_code == 200, lint.text[:500]
    lint_body = lint.json()
    assert lint_body["ok"] is True
    for issue in lint_body.get("issues", []):
        assert issue["code"] in {spec.code for spec in ISSUES}

    convert = _multipart_post(
        smoke_client,
        "/api/v1/convert",
        {
            "manual_text": tac,
            "product": product,
            "profile": "annex3",
            "lint": "false",
        },
    )
    assert convert.status_code == 200, convert.text[:800]
    convert_body = convert.json()
    assert convert_body.get("successful", 0) >= 1 or convert_body.get("ok") is True
    results = convert_body.get("results") or []
    assert results, "convert must return at least one result"
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "iwxxm" in xml.lower() or "<" in xml


@pytest.mark.parametrize("product", ["metar", "speci"])
def test_tc_f15_004_catalog_get_smoke(smoke_client: TestClient, product: str) -> None:
    response = smoke_client.get("/api/v1/lint-issue-catalog", params={"product": product})
    assert response.status_code == 200, response.text[:400]
    issues = response.json()["issues"]
    assert len(issues) >= 1
    codes = {row["code"] for row in issues}
    assert "MISSING_OBS_TIME" in codes or "MISSING_CCCC" in codes
    registry = {spec.code for spec in ISSUES}
    assert codes <= registry
