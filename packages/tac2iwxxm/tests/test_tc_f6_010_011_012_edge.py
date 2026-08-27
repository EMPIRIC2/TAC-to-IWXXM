"""TC-F6-010 / 011 / 012 edge cases (T5.6 / UJ-008-010).

Spec: docs/test-plan.md TC-F6-010-012; docs/user-journeys.md UJ-008-010.
"""

from __future__ import annotations

import pytest


def test_tc_f6_010_unknown_product_structured_error() -> None:
    """UJ-008: unknown product → structured UNSUPPORTED_PRODUCT; no silent success."""
    from tac2iwxxm import convert

    result = convert("METAR KJFK 231751Z NIL=", product="NOTAPRODUCT")
    assert result.ok is False
    assert result.xml is None
    assert any(i.code == "UNSUPPORTED_PRODUCT" for i in result.issues)
    assert "gifts" not in (result.issues[0].message or "").lower()


def test_tc_f6_011_iwxxm_us_pin_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """UJ-009: profile=iwxxm_us without vendor catalog → fail closed (no annex3 downgrade)."""
    import iwxxm_validate.api as validate_api
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    result = convert(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2=",
        product="METAR",
        profile="iwxxm_us",
    )
    assert result.ok is True
    assert result.xml
    # Convert itself still emits US XML; fail-closed is on validate path.
    monkeypatch.setattr(validate_api, "us_catalog_path", lambda: None)
    report = validate(result.xml, iwxxm_version="2025-2", profile="iwxxm_us")
    assert report.ok is False
    assert any("iwxxm-us" in i.message.lower() or "catalog" in i.message.lower() for i in report.issues)
    # Must not silently validate as annex3 when profile was iwxxm_us.
    assert "www.weather.gov/iwxxm-us" in result.xml


def test_tc_f6_012_malformed_us_remarks_diagnostics() -> None:
    """UJ-010: malformed US REMARKS under iwxxm_us yield structured issues (not silent drop)."""
    from tac2iwxxm import convert

    # AOX / SLPZZZ / PK WND without valid groups - should surface REMARKS diagnostics.
    result = convert(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AOX SLPZZZ PK WND XXX=",
        product="METAR",
        profile="iwxxm_us",
    )
    # Convert may still succeed with partial IR, but must attach diagnostics.
    codes = {i.code for i in result.issues}
    assert "MALFORMED_REMARKS" in codes or any("remark" in (i.message or "").lower() for i in result.issues), (
        f"expected REMARKS diagnostics, got {result.issues!r}"
    )
