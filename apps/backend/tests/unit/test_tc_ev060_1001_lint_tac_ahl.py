"""TC-EV060-1001 / UJ-059: POST /lint-tac splits AHL; malformed AHL is not 5xx.

Spec: docs/test-plan.md TC-EV060-1001-001..002; [Corpus: api] [Corpus: tests].
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

WELL_FORMED = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
"""

MALFORMED = """\
QQUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
"""


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _lint(client: TestClient, text: str, product: str = "METAR"):
    return client.post(
        "/api/v1/lint-tac",
        files={
            "manual_text": (None, text),
            "product": (None, product),
        },
    )


def test_lint_tac_well_formed_ahl_no_heading_flood(client: TestClient) -> None:
    response = _lint(client, WELL_FORMED)
    assert response.status_code == 200
    payload = response.json()
    codes = [i["code"] for i in payload["issues"]]
    assert "MULTI_REPORT_BULLETIN" not in codes
    assert "MISSING_PRODUCT_KEYWORD" not in codes


def test_lint_tac_malformed_ahl_structured_not_5xx(client: TestClient) -> None:
    response = _lint(client, MALFORMED)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    bulletin = [i for i in payload["issues"] if i.get("location") == "bulletin" and i["severity"] == "error"]
    assert len(bulletin) == 1
    assert bulletin[0]["code"] == "INVALID_AHL"


def test_lint_tac_convert_bulletin_ahl_issue_parity(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-EV060-1001-003: lint-tac and convert-bulletin see the same contained-report issues."""
    bulletin = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z ZZZ00KT 10SM SCT040 21/13 A3010=
"""

    def fake_convert(tac: str, **kwargs: object) -> tuple[str, None]:
        return f"<iwxxm:METAR>{tac[:20]}</iwxxm:METAR>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    lint_payload = _lint(client, bulletin).json()
    convert_resp = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "profile": (None, "annex3"),
            "lint": (None, "true"),
        },
    )
    assert convert_resp.status_code == 200
    convert_codes = sorted(i["code"] for r in convert_resp.json()["results"] for i in r.get("issues") or [])
    lint_codes = sorted(i["code"] for i in lint_payload["issues"] if i.get("location") != "bulletin")
    assert "INVALID_WIND" in convert_codes
    assert lint_codes == convert_codes
