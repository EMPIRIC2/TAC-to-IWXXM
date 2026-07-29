"""T6.1 / TC-F24-005 + TC-F25-004 — AIRMET + WMO METAR/SPECI/TAF lint/convert/decode smoke.

Spec: docs/test-plan.md TC-F24-005 / TC-F25-004; execution-plan T6.1 (S026 / EV-020).
In-process client (CI); live H3/H4–H5 reuse paths at 13-deploy-smoke.
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
    ("airmet_a6_1a_ts.tac", "AIRMET", "airmet", "isolated"),
    ("metar_a3_1.tac", "METAR", "metar", "yudo"),
    ("speci_a3_2.tac", "SPECI", "speci", "yudo"),
    ("taf_a5_1.tac", "TAF", "taf", "yudo"),
    ("taf_a5_2.tac", "TAF", "taf", "cnl"),
)


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    async def _auth_user() -> dict[str, str]:
        return {"sub": "f24-f25-smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _multipart_post(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


@pytest.mark.parametrize(
    ("tac_file", "product", "root_hint", "_decode_hint"),
    WMO_CASES,
    ids=[c[0].removesuffix(".tac") for c in WMO_CASES],
)
def test_tc_f24_005_f25_004_lint_convert_decode_smoke(
    smoke_client: TestClient,
    tac_file: str,
    product: str,
    root_hint: str,
    _decode_hint: str,
) -> None:
    tac = _tac(tac_file)

    lint = _multipart_post(
        smoke_client,
        "/api/v1/lint-tac",
        {"manual_text": tac, "product": product},
    )
    assert lint.status_code == 200, lint.text[:500]
    lint_body = lint.json()
    # Registry-shaped issues always; WMO vendor TAC may still trip research rows
    # (e.g. INVALID_RVR on R12/1000U) so ok=False is allowed for METAR/SPECI smoke.
    for issue in lint_body.get("issues", []):
        assert issue["code"] in {spec.code for spec in ISSUES}
    if product in {"AIRMET", "TAF"}:
        assert lint_body["ok"] is True

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

    decode = _multipart_post(
        smoke_client,
        "/api/v1/decode-tac",
        {"manual_text": tac, "product": product},
    )
    assert decode.status_code == 200, decode.text[:500]
    decode_body = decode.json()
    assert "summary" in decode_body
    assert isinstance(decode_body.get("segments"), list)
    # Glossary deepen: AIRMET ISOL → isolated; others keep non-empty summary.
    if product == "AIRMET":
        joined = " ".join(s.get("explanation", "") for s in decode_body["segments"]).lower()
        assert "isolated" in joined or "thunderstorm" in joined
    assert decode_body["summary"].strip()


def test_tc_f24_005_airmet_catalog_get_smoke(smoke_client: TestClient) -> None:
    response = smoke_client.get("/api/v1/lint-issue-catalog", params={"product": "airmet"})
    assert response.status_code == 200, response.text[:400]
    issues = response.json()["issues"]
    assert len(issues) >= 1
    codes = {row["code"] for row in issues}
    registry = {spec.code for spec in ISSUES}
    assert codes <= registry
