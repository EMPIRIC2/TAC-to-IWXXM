"""T3.1 / TC-F7-003: soft-preview via preview=true on POST /api/v1/convert (S011 / EV-008).

Spec: docs/adr/ADR-022-convert-preview-flag.md; docs/api-contract.md Soft-preview;
docs/test-plan.md TC-F7-003; UJ-016.
Expected red until T3.2 implements the preview form flag + soft-preview path.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"

# Injectably invalid TAC: hard convert fails parse; soft-preview must still 200.
BAD_METAR_TAC = "METAR XXXX NOT_A_REAL_REPORT GARBAGE="


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_convert(
    client: TestClient,
    *,
    manual_text: str,
    product: str = "METAR",
    preview: str | None = None,
    lint: str = "false",
):
    """POST /api/v1/convert as multipart/form-data."""
    files: dict[str, tuple[None, str]] = {
        "manual_text": (None, manual_text),
        "product": (None, product),
        "profile": (None, "annex3"),
        "lint": (None, lint),
    }
    if preview is not None:
        files["preview"] = (None, preview)
    return client.post("/api/v1/convert", files=files)


def _assert_failed_spans(payload: dict) -> None:
    assert "failed_spans" in payload
    spans = payload["failed_spans"]
    assert isinstance(spans, list)
    assert len(spans) >= 1
    for span in spans:
        assert isinstance(span["start"], int)
        assert isinstance(span["end"], int)
        assert 0 <= span["start"] <= span["end"]
        # code / message optional per api-contract


def test_convert_preview_partial_failure_returns_200_failed_spans_and_xml(
    client: TestClient,
) -> None:
    """ADR-022: preview=true → HTTP 200, ok=false, failed_spans, best-effort IWXXM."""
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    _assert_failed_spans(payload)

    results = payload.get("results") or []
    assert results, "soft-preview must return best-effort XML in results"
    xml = results[0].get("content") or ""
    assert "<" in xml and "iwxxm" in xml.lower(), "best-effort body must look like IWXXM XML"


def test_convert_without_preview_keeps_hard_fail(client: TestClient) -> None:
    """TC-F7-003: hard convert failure semantics unchanged when preview not selected."""
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview=None)
    assert response.status_code in {400, 422}, response.text[:500]
    # Must not look like soft-preview success envelope
    if response.headers.get("content-type", "").startswith("application/json"):
        body = response.json()
        assert body.get("ok") is not True
        # Soft-preview fields should not redefine hard-fail into 200
        assert "failed_spans" not in body or response.status_code != 200


def test_convert_preview_false_keeps_hard_fail(client: TestClient) -> None:
    """Explicit preview=false retains hard-fail HTTP semantics."""
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="false")
    assert response.status_code in {400, 422}, response.text[:500]


def test_convert_preview_success_ok_true(client: TestClient) -> None:
    """Valid TAC with preview=true still succeeds (ok true or empty failed_spans)."""
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = _multipart_convert(client, manual_text=tac, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is True
    assert payload.get("successful", 0) >= 1
    spans = payload.get("failed_spans") or []
    assert spans == []
    assert payload["results"]
    assert "<" in payload["results"][0]["content"]
