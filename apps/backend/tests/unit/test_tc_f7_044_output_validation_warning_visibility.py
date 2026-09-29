"""TC-F7-044 / #1159 — soft OUTPUT_VALIDATION_WARNING must list details; SIGMET not METAR-linted."""

from __future__ import annotations

from pathlib import Path

import pytest

SIGMET_A6 = Path("apps/frontend/src/fixtures/examples/bodies/sigmet_a6_1a_ts.tac")


@pytest.mark.skipif(not SIGMET_A6.is_file(), reason="frontend SIGMET example fixture missing")
def test_tc_f7_044_sigmet_validate_output_skips_metar_tac_layers(client) -> None:
    """Post-convert soft validation must not apply METAR keyword checks to SIGMET TAC."""
    tac = SIGMET_A6.read_text(encoding="utf-8")
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": tac,
            "product": "SIGMET",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "iwxxm_version": "2025-2",
            "validate_output": "true",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["successful"] >= 1
    codes = {issue.get("code") for issue in payload.get("issues") or []}
    assert "MISSING_KEYWORD" not in codes
    assert "UNKNOWN_ICAO" not in codes
    # Soft warn may still appear for real IWXXM findings; those must be listed.
    if "OUTPUT_VALIDATION_WARNING" in codes:
        detail_codes = {
            issue.get("code")
            for issue in payload.get("issues") or []
            if issue.get("code") not in {None, "OUTPUT_VALIDATION_WARNING"}
        }
        assert detail_codes, "soft warn must include flattened issue details"


def test_tc_f7_044_output_validation_warning_flattens_orchestrator_issues(client, monkeypatch) -> None:
    """Aggregate OUTPUT_VALIDATION_WARNING must not hide underlying issue codes/messages."""
    from src.schemas.validation import ValidationIssue, ValidationLayer, ValidationLevel

    class _FakeOrch:
        def validate_complete(self, **_kwargs):
            return type(
                "R",
                (),
                {
                    "is_valid": False,
                    "all_issues": [
                        ValidationIssue(
                            layer=ValidationLayer.GML_REFERENCES,
                            level=ValidationLevel.ERROR,
                            message="Broken GML href",
                            code="GML_HREF_MISSING",
                            location="line 1",
                            suggestion="Fix the xlink:href target.",
                        ),
                        ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationLevel.WARNING,
                            message="Unknown codelist value",
                            code="CODELIST_UNKNOWN",
                        ),
                    ],
                    "passed": False,
                },
            )()

    monkeypatch.setattr(
        "src.api.get_validation_orchestrator",
        lambda: _FakeOrch(),
    )
    monkeypatch.setattr(
        "src.api._call_iwxxm_validate",
        lambda *_a, **_k: type("P", (), {"ok": True, "issues": []})(),
    )

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013=",
            "product": "METAR",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "validate_output": "true",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    codes = {issue.get("code") for issue in payload.get("issues") or []}
    assert "OUTPUT_VALIDATION_WARNING" in codes
    assert "GML_HREF_MISSING" in codes
    assert "CODELIST_UNKNOWN" in codes
    gml = next(i for i in payload["issues"] if i.get("code") == "GML_HREF_MISSING")
    assert "Broken GML href" in gml["message"]
    assert gml.get("hint") == "Fix the xlink:href target."
