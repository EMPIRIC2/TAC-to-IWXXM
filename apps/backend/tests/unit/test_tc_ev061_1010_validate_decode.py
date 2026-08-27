"""TC-EV061-1010 - Validate IWXXM item-by-item readable decode (#1010).

[Corpus: product §F2] [Corpus: product §F9] [Corpus: api] [Corpus: tests §TC-EV061-1010]
UJ-064
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

REPO = Path(__file__).resolve().parents[4]
GOLDEN_XML = (
    REPO / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden" / "metar_basic.golden.xml"
).read_text(encoding="utf-8")

TAC_SAMPLE = "METAR KJFK 231751Z 18012KT 9999 FEW040 15/07 Q1017="

_INTERNAL_DOC_REF = (
    "[Corpus:",
    "docs/sessions/",
    "docs/feature-list",
    "ADR-",
    "EV-0",
    "S0",
    "TC-",
    "#101",
    "F2",
    "F7",
    "F9",
)


def _assert_no_internal_doc_refs(text: str) -> None:
    for token in _INTERNAL_DOC_REF:
        assert token not in text, f"operator copy must not contain {token!r}: {text!r}"


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def _client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    return TestClient(api_module.app)


def test_tc_ev061_1010_001_validate_iwxxm_item_by_item_decode() -> None:
    """POST /validate on golden IWXXM returns F9-shaped rows, not a raw XML dump."""
    client = _client()
    try:
        response = _multipart(
            client,
            "/api/v1/validate",
            {
                "xml_content": GOLDEN_XML,
                "iwxxm_version": "2025-2",
                "profile": "annex3",
                "stop_on_error": "false",
            },
        )
        assert response.status_code == 200, response.text[:400]
        payload = response.json()
        segments = payload.get("segments") or []
        assert segments, "validate IWXXM must expose item-by-item decode rows"
        joined_code = " ".join(str(s.get("code") or "") for s in segments)
        explanations = " ".join(str(s.get("explanation") or "") for s in segments)
        summary = payload.get("summary") or ""

        assert "<?xml" not in joined_code
        assert GOLDEN_XML[:120] not in joined_code
        assert "<iwxxm:METAR" not in joined_code
        assert "KJFK" in joined_code or "KJFK" in explanations or "KJFK" in summary
        lowered = explanations.lower()
        assert any(token in lowered for token in ("wind", "temperature", "aerodrome", "visibility")), explanations
        assert summary.strip()
        assert "<iwxxm" not in summary
        _assert_no_internal_doc_refs(summary)
        _assert_no_internal_doc_refs(explanations)
        for seg in segments:
            assert {"start", "end", "code", "explanation"} <= set(seg)
    finally:
        api_module.app.dependency_overrides.clear()


def test_tc_ev061_1010_002_additive_decode_fields_backward_compatible() -> None:
    """Existing ValidateResponse keys remain; OpenAPI documents optional segments/summary."""
    client = _client()
    try:
        response = _multipart(
            client,
            "/api/v1/validate",
            {
                "xml_content": GOLDEN_XML,
                "iwxxm_version": "2025-2",
                "profile": "annex3",
                "stop_on_error": "false",
            },
        )
        assert response.status_code == 200, response.text[:400]
        payload = response.json()
        for key in (
            "is_valid",
            "version",
            "layers_run",
            "layers_passed",
            "package_ok",
            "package_issues",
        ):
            assert key in payload, f"existing client field {key} must remain"

        schema = api_module.app.openapi()
        props = schema["components"]["schemas"]["ValidateResponse"]["properties"]
        assert "segments" in props
        assert "summary" in props
        required = set(schema["components"]["schemas"]["ValidateResponse"].get("required") or [])
        assert "segments" not in required
        assert "summary" not in required
        desc = " ".join(
            [
                str(props["segments"].get("description") or ""),
                str(props["summary"].get("description") or ""),
            ]
        )
        _assert_no_internal_doc_refs(desc)
    finally:
        api_module.app.dependency_overrides.clear()


def test_tc_ev061_1010_002_omits_decode_when_xml_has_no_fields() -> None:
    """Minimal well-formed XML without meteorological fields omits decode extras."""
    client = _client()
    try:
        response = _multipart(
            client,
            "/api/v1/validate",
            {
                "xml_content": "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>",
                "iwxxm_version": "2025-2",
                "stop_on_error": "false",
            },
        )
        assert response.status_code == 200, response.text[:400]
        payload = response.json()
        assert "is_valid" in payload
        segments = payload.get("segments")
        assert segments in (None, [])
        summary = payload.get("summary")
        assert summary in (None, "")
    finally:
        api_module.app.dependency_overrides.clear()


def test_tc_ev061_1010_003_validate_only_and_iwxxm_pass_through_still_work() -> None:
    """F7.s validate-only and F7.t product=iwxxm lint still succeed after decode fields."""
    client = _client()
    try:
        validate = _multipart(
            client,
            "/api/v1/validate",
            {
                "xml_content": GOLDEN_XML,
                "iwxxm_version": "2025-2",
                "profile": "annex3",
                "stop_on_error": "false",
            },
        )
        assert validate.status_code == 200, validate.text[:400]
        assert "is_valid" in validate.json()

        lint = _multipart(
            client,
            "/api/v1/lint-tac",
            {"manual_text": GOLDEN_XML, "product": "iwxxm"},
        )
        assert lint.status_code == 200, lint.text[:400]
        assert lint.json()["ok"] is True

        convert = _multipart(
            client,
            "/api/v1/convert",
            {
                "manual_text": GOLDEN_XML,
                "product": "iwxxm",
                "profile": "annex3",
                "lint": "false",
            },
        )
        assert convert.status_code == 200, convert.text[:400]
        body = convert.json()
        assert body.get("successful", 0) >= 1 or body.get("ok") is True
    finally:
        api_module.app.dependency_overrides.clear()


def test_readable_decode_helper_edges() -> None:
    """Direct helper coverage: empty, malformed, TAC fallback, CAVOK, nil skip."""
    from src.utilities.iwxxm_readable_decode import decode_for_validate, readable_decode_from_iwxxm

    assert readable_decode_from_iwxxm("").segments == []
    assert readable_decode_from_iwxxm("not xml").segments == []
    assert readable_decode_from_iwxxm("<not-closed").segments == []

    cavok = (
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">'
        "<iwxxm:observation>"
        '<iwxxm:MeteorologicalAerodromeObservation cloudAndVisibilityOK="true">'
        '<iwxxm:airTemperature uom="Cel" xsi:nil="true"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>'
        "</iwxxm:MeteorologicalAerodromeObservation>"
        "</iwxxm:observation>"
        "</iwxxm:METAR>"
    )
    cavok_rows = readable_decode_from_iwxxm(cavok)
    assert any(s.code == "CAVOK" for s in cavok_rows.segments)

    tac = decode_for_validate(manual_text=TAC_SAMPLE)
    assert tac.segments
    assert "KJFK" in " ".join(s.code for s in tac.segments)

    xml_then_tac = decode_for_validate(
        xml_content="<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>",
        manual_text=TAC_SAMPLE,
    )
    assert xml_then_tac.segments
    assert "KJFK" in " ".join(s.code for s in xml_then_tac.segments)

    from src.utilities.iwxxm_readable_decode import (
        _format_measure,
        _href_code,
        _local_name,
        _offsets,
    )

    assert _local_name("foo:bar") == "bar"
    assert _local_name("plain") == "plain"
    assert _href_code("RA") == "RA"
    assert _format_measure("  ", None) == ""
    assert _format_measure("12", "kt") == "12 kt"
    assert _offsets("<a>z</a>", "missing") == (0, 0)
    assert _offsets("abc", "") == (0, 0)

    weather = (
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"'
        ' xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml/3.2">'
        "<gml:timePosition>2023-01-01T00:00:00Z</gml:timePosition>"
        '<iwxxm:presentWeather xlink:href="http://codes.wmo.int/49-2/WeatherCausingObscuration/RA"/>'
        '<iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SCT"/>'
        '<iwxxm:base uom="[ft_i]">2000</iwxxm:base>'
        '<iwxxm:meanWindDirection uom="deg">090</iwxxm:meanWindDirection>'
        "<iwxxm:designator>&lt;?xml</iwxxm:designator>"
        "</iwxxm:METAR>"
    )
    extra = readable_decode_from_iwxxm(weather)
    codes = [s.code for s in extra.segments]
    assert "RA" in codes
    assert "SCT" in codes or any(c.startswith("SCT") for c in codes)
    assert any("090" in c for c in codes)
    assert "<?xml" not in codes
    assert "Wind 090 deg." in extra.summary or "090" in extra.summary

    amount_only = (
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"'
        ' xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/FEW"/>'
        '<iwxxm:weird xlink:href="http://codes.wmo.int/ZZ"/>'
        "</iwxxm:METAR>"
    )
    amount_rows = readable_decode_from_iwxxm(amount_only)
    amount_codes = [s.code for s in amount_rows.segments]
    assert "FEW" in amount_codes
    assert "ZZ" in amount_codes
