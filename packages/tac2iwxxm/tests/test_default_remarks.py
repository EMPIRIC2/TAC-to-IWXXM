"""Default profile keeps RMK out of the international body (#1404)."""

from __future__ import annotations

from tac2iwxxm import convert

_VCSH = "METAR MKJP 081200Z 14006KT 9999 FEW020 28/24 Q1013 RMK VCSH S="
_VIS = "METAR MKJP 081200Z 14006KT 9999 FEW020 28/24 Q1013 RMK VIS16KM="
_NOTE = "Remarks after RMK stay out of the international report."


def test_vicinity_showers_remark_stays_out_of_the_international_body() -> None:
    result = convert(_VCSH, product="METAR", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.profile == "annex3"
    assert result.xml is not None
    excluded = next(issue for issue in result.issues if issue.code == "REMARKS_EXCLUDED")
    assert excluded.severity == "info"
    assert excluded.location == "remarks"
    assert excluded.message == _NOTE
    assert "iwxxm_us" not in (excluded.message or "")
    assert excluded.start is not None
    assert excluded.end is not None
    assert _VCSH[excluded.start : excluded.end] == "RMK"
    assert "presentWeather" not in result.xml
    assert "4678/VCSH" not in result.xml
    assert "4678/SH" not in result.xml
    assert "16000" not in result.xml


def test_kilometre_visibility_remark_is_not_written_as_metres() -> None:
    result = convert(_VIS, product="METAR", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    excluded = next(issue for issue in result.issues if issue.code == "REMARKS_EXCLUDED")
    assert excluded.message == _NOTE
    assert "iwxxm_us" not in (excluded.message or "")
    assert "presentWeather" not in result.xml
    assert "4678/VCSH" not in result.xml
    assert "4678/SH" not in result.xml
    assert "16000" not in result.xml
