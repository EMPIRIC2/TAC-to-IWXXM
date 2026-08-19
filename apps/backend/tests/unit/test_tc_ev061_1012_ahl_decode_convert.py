"""TC-EV061-1012 — AHL decode + convert-bulletin (#1012).

[Corpus: product §F6] [Corpus: api] [Corpus: tests §TC-EV061-1012] UJ-065
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

REPO = Path(__file__).resolve().parents[4]
GOLDEN = (REPO / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "metar_multi_ahl.txt").read_text(encoding="utf-8")

_INTERNAL_DOC_REF = (
    "[Corpus:",
    "docs/sessions/",
    "docs/feature-list",
    "ADR-",
    "EV-0",
    "S0",
    "TC-",
    "#101",
    "F6",
    "F7",
    "F9",
)


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def _assert_no_internal_doc_refs(text: str) -> None:
    for token in _INTERNAL_DOC_REF:
        assert token not in text, f"operator copy must not contain {token!r}: {text!r}"


def test_tc_ev061_1012_001_decode_tac_golden_ahl_rows(client: TestClient) -> None:
    """POST /decode-tac: bulletin framing + per-report F9 rows."""
    response = _multipart(
        client,
        "/api/v1/decode-tac",
        {"manual_text": GOLDEN, "product": "METAR"},
    )
    assert response.status_code == 200, response.text[:400]
    payload = response.json()
    codes = [s["code"] for s in payload["segments"]]
    explanations = " ".join(s["explanation"] for s in payload["segments"])
    residual_text = " ".join(r["text"] for r in payload["residuals"])
    summary = payload.get("summary") or ""

    assert any("SAUS31" in s["code"] or "SAUS31" in s["explanation"] for s in payload["segments"])
    assert "KJFK" in codes
    assert "KLGA" in codes
    assert "SAUS31 KZNY 121200" not in residual_text
    assert "METAR KLGA" not in residual_text
    assert "KJFK" in summary
    assert "KLGA" in summary
    _assert_no_internal_doc_refs(summary)
    _assert_no_internal_doc_refs(explanations)


def test_tc_ev061_1012_002_convert_bulletin_golden(client: TestClient) -> None:
    """POST /convert-bulletin succeeds with per-report IWXXM (not 5xx)."""
    response = _multipart(
        client,
        "/api/v1/convert-bulletin",
        {
            "manual_text": GOLDEN,
            "product": "METAR",
            "profile": "annex3",
            "lint": "false",
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["ahl"] == "SAUS31 KZNY 121200"
    assert meta["cccc"] == "KZNY"
    assert meta["report_count"] == 2
    results = payload["results"]
    assert len(results) == 2
    assert results[0]["ok"] is True
    assert results[1]["ok"] is True
    assert results[0]["tac_input"].startswith("METAR KJFK")
    assert results[1]["tac_input"].startswith("METAR KLGA")
    assert results[0]["xml"] and "iwxxm" in results[0]["xml"].lower()
    assert results[1]["xml"] and "iwxxm" in results[1]["xml"].lower()


def test_tc_ev061_1012_004_malformed_ahl_invalid_ahl(client: TestClient) -> None:
    """Malformed heading → INVALID_AHL; heading-only → empty_bulletin; no silent 200."""
    malformed = _multipart(
        client,
        "/api/v1/convert-bulletin",
        {
            "manual_text": "NOTANAHL XXXX 999999\nMETAR KJFK 121151Z 18008KT=\n",
            "product": "METAR",
            "lint": "false",
        },
    )
    assert malformed.status_code in {400, 422}
    detail = malformed.json()["detail"]
    assert detail["code"] == "INVALID_AHL"
    message = detail.get("message") or ""
    assert message
    _assert_no_internal_doc_refs(message)
    assert "heading" in message.lower() or "abbreviated" in message.lower()

    heading_only = _multipart(
        client,
        "/api/v1/convert-bulletin",
        {"manual_text": "SAUS31 KZNY 121200\n", "product": "METAR", "lint": "false"},
    )
    assert heading_only.status_code == 400
    empty = heading_only.json()["detail"]
    assert empty["code"] == "empty_bulletin"
    _assert_no_internal_doc_refs(empty.get("message") or "")
