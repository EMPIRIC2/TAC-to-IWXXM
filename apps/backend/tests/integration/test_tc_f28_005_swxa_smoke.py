"""T11.7 / TC-F28-005 — SWXA lint/convert + catalog GET smoke (UJ-043).

Spec: docs/test-plan.md TC-F28-005; execution-plan T11.7 (S036 / EV-029).
In-process client (CI); live H3/H4–H5 at 13 when FE Examples unlock ships.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tac_validate.issue_registry import ISSUES

from src.api import app
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration, pytest.mark.smoke]

ANNEX3 = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden"


def _tac(name: str) -> str:
    return (ANNEX3 / name).read_text(encoding="utf-8").strip()


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "f28-swxa-smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def test_tc_f28_005_lint_and_convert_smoke(smoke_client: TestClient) -> None:
    tac = _tac("swxa_a7_3.tac")

    lint = _multipart_post(
        smoke_client,
        "/api/v1/lint-tac",
        {"manual_text": tac, "product": "swxa"},
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
            "product": "swxa",
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
    xml_compact = xml.lower().replace(":", "").replace("_", "")
    assert "spaceweatheradvisory" in xml_compact
    # Adjacency: SWXA path must not emit SIGMET / VAA / TCA sibling roots.
    assert "volcanicashsigmet" not in xml_compact
    assert "tropicalcyclonesigmet" not in xml_compact
    assert "volcanicashadvisory" not in xml_compact
    assert "tropicalcycloneadvisory" not in xml_compact


def test_tc_f28_005_catalog_get_smoke(smoke_client: TestClient) -> None:
    response = smoke_client.get("/api/v1/lint-issue-catalog", params={"product": "swxa"})
    assert response.status_code == 200, response.text[:400]
    issues = response.json()["issues"]
    assert len(issues) >= 1
    codes = {row["code"] for row in issues}
    assert "MISSING_SWXC" in codes
    registry = {spec.code for spec in ISSUES}
    assert codes <= registry
