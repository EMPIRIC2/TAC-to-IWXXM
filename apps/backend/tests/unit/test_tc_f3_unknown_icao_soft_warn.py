"""TC-F3-UNK-001..004 — unknown aerodrome ICAO converts with UNKNOWN_ICAO warning.

[Corpus: product §F3] Unknown designators soft-warn; they do not hard-gate convert
or alone block publish/download (severity=warning).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

_KNOWN_METAR = "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013="
_UNKNOWN_ABCD = "METAR ABCD 010000Z 00000KT CAVOK 10/08 Q1013="
_UNKNOWN_SWWW = "METAR SWWW 291400Z 01004KT 330V090 9999 VCSH FEW019CB SCT090 32/27 Q1012 NOSIG="
_UNKNOWN_SPECI = "SPECI ABCD 010000Z 00000KT CAVOK 10/08 Q1013="
_UNKNOWN_TAF = "TAF ABCD 010000Z 0100/0206 00000KT CAVOK="


def _convert(client: TestClient, *, tac: str, product: str, preview: str | None = None) -> dict:
    data = {
        "manual_text": tac,
        "product": product,
        "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
        "iwxxm_version": "2025-2",
    }
    if preview is not None:
        data["preview"] = preview
    response = client.post("/api/v1/convert", data=data)
    assert response.status_code == 200, response.text
    return response.json()


def _issue_by_code(payload: dict, code: str) -> dict | None:
    for issue in payload.get("issues") or []:
        if issue.get("code") == code:
            return issue
    return None


def test_tc_f3_unk_001_known_icao_converts_without_unknown_warning(client: TestClient) -> None:
    """Known aerodrome (KJFK) converts with no UNKNOWN_ICAO issue."""
    payload = _convert(client, tac=_KNOWN_METAR, product="METAR")
    assert payload.get("successful", 0) >= 1
    assert _issue_by_code(payload, "UNKNOWN_ICAO") is None


@pytest.mark.parametrize(
    ("tac", "product", "designator"),
    [
        (_UNKNOWN_ABCD, "METAR", "ABCD"),
        (_UNKNOWN_SWWW, "METAR", "SWWW"),
        (_UNKNOWN_SPECI, "SPECI", "ABCD"),
        (_UNKNOWN_TAF, "TAF", "ABCD"),
    ],
    ids=["metar-ABCD", "metar-SWWW", "speci-ABCD", "taf-ABCD"],
)
def test_tc_f3_unk_002_unknown_icao_converts_with_warning(
    client: TestClient, tac: str, product: str, designator: str
) -> None:
    """Unknown ICAO still converts and surfaces UNKNOWN_ICAO as warning."""
    payload = _convert(client, tac=tac, product=product)
    assert payload.get("successful", 0) >= 1
    issue = _issue_by_code(payload, "UNKNOWN_ICAO")
    assert issue is not None, payload.get("issues")
    assert issue.get("severity") == "warning"
    assert designator in (issue.get("message") or "")
    assert "aerodrome registry" in (issue.get("message") or "").lower()
    # Warning alone must not appear as a hard validation failure.
    assert _issue_by_code(payload, "VALIDATION_FAILED") is None


def test_tc_f3_unk_003_soft_preview_unknown_icao_keeps_envelope_ok(client: TestClient) -> None:
    """Soft-preview with only UNKNOWN_ICAO still converts; warning is listed."""
    payload = _convert(client, tac=_UNKNOWN_ABCD, product="METAR", preview="true")
    assert payload.get("successful", 0) >= 1
    issue = _issue_by_code(payload, "UNKNOWN_ICAO")
    assert issue is not None
    assert issue.get("severity") == "warning"
    # Layer-1 soft warn must not mark soft-preview as layer12 hard soft-fail alone.
    assert _issue_by_code(payload, "LAYER12_SOFT_FAIL") is None


def test_tc_f3_unk_004_json_metars_unknown_icao_surfaces_warning(client: TestClient) -> None:
    """JSON metars[] path also surfaces UNKNOWN_ICAO without aborting."""
    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [_UNKNOWN_ABCD],
            "product": "METAR",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "iwxxm_version": "2025-2",
            "validation_level": "basic",
            "stop_on_error": False,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("successful", 0) >= 1
    issue = _issue_by_code(payload, "UNKNOWN_ICAO")
    assert issue is not None
    assert issue.get("severity") == "warning"
