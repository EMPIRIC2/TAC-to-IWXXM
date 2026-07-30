"""T6.1 / TC-F26-005 + TC-F27-005 — VAA + TCA lint/convert + catalog GET smoke.

Spec: docs/test-plan.md TC-F26-005 / TC-F27-005; UJ-037 / UJ-038;
execution-plan T6.1 (S027 / EV-021). In-process client (CI); live H3/H4–H5 at 13.
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


WMO_CASES = (
    ("vaa_a7_2.tac", "VAA", "volcanicashadvisory", "MISSING_VAAC"),
    ("tca_a2_2.tac", "TCA", "tropicalcycloneadvisory", "MISSING_TC"),
)


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "f26-f27-smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


@pytest.mark.parametrize(
    ("tac_file", "product", "root_hint", "_catalog_code"),
    WMO_CASES,
    ids=[c[0].removesuffix(".tac") for c in WMO_CASES],
)
def test_tc_f26_005_f27_005_lint_and_convert_smoke(
    smoke_client: TestClient,
    tac_file: str,
    product: str,
    root_hint: str,
    _catalog_code: str,
) -> None:
    tac = _tac(tac_file)

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
    xml_compact = xml.lower().replace(":", "").replace("_", "")
    assert root_hint in xml_compact, f"expected root hint {root_hint!r} in convert XML"
    # Adjacency: advisory path must not emit the SIGMET sibling root.
    if product == "VAA":
        assert "volcanicashsigmet" not in xml_compact
    else:
        assert "tropicalcyclonesigmet" not in xml_compact


@pytest.mark.parametrize(
    ("product", "expected_code"),
    [
        ("vaa", "MISSING_VAAC"),
        ("tca", "MISSING_TC"),
    ],
)
def test_tc_f26_005_f27_005_catalog_get_smoke(
    smoke_client: TestClient,
    product: str,
    expected_code: str,
) -> None:
    response = smoke_client.get("/api/v1/lint-issue-catalog", params={"product": product})
    assert response.status_code == 200, response.text[:400]
    issues = response.json()["issues"]
    assert len(issues) >= 1
    codes = {row["code"] for row in issues}
    assert expected_code in codes
    registry = {spec.code for spec in ISSUES}
    assert codes <= registry
