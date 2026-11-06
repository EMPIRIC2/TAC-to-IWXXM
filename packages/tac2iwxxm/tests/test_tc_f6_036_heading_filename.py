"""TC-F6-036 — real heading on translation metadata and the IWXXM filename.

[Corpus: product §F6] [Corpus: api] [Corpus: tests §TC-F6-036]
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from tac2iwxxm.exchange_output import build_ca_eccc_output_spec

from tac2iwxxm import convert, parse_ahl

_BULLETIN = "SAUS31 KZNY 121200\nMETAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013=\n"
_FAILED = "SAUS31 KZNY 121200\nMETAR KJFK 121151Z INVALID 18012KT 9999 FEW020 15/07 Q1013=\n"
_BARE = "METAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013="
_HEADING_ID = "SAUS31KZNY121200"
_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_CENTRE = "CWAO"
_CENTRE_NAME = "Test translation centre"


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'{name}="([^"]*)"', xml)
    return match.group(1) if match else None


def test_tc_f6_036_on_behalf_metar_uses_the_real_heading() -> None:
    """Translation-centre emit copies the parsed heading and stamps both times."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        emit_translation_centre=True,
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "translatedBulletinID") == _HEADING_ID
    issued = _attr(xml, "translationTime")
    received = _attr(xml, "translatedBulletinReceptionTime")
    assert issued is not None
    assert _TIME.fullmatch(issued)
    assert received == issued
    assert _attr(xml, "translationCentreDesignator") == _CENTRE
    assert "TTAAiiCCCYYGGgg" not in xml
    assert "YUZZ" not in xml


def test_tc_f6_036_failed_translation_drops_the_placeholder_heading() -> None:
    """A parsed heading replaces YUZZ and the placeholder bulletin id."""
    result = convert(
        _FAILED,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert "translationFailedTAC" in xml
    assert "INVALID" in (_attr(xml, "translationFailedTAC") or "")
    assert _attr(xml, "translatedBulletinID") == _HEADING_ID
    assert _attr(xml, "translationCentreDesignator") == _CENTRE
    assert "TTAAiiCCCYYGGgg" not in xml
    assert "YUZZ" not in xml


def test_tc_f6_036_bulletin_convert_returns_gzip_filename() -> None:
    """The suggested name uses the IWXXM T1T2 and ends in .xml.gz."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    name = result.suggested_filename or ""
    assert name.startswith("A_LAUS31KZNY121200")
    assert "_C_KZNY_" in name
    assert name.endswith(".xml.gz")
    assert not name.startswith("A_SA")


def test_tc_f6_036_no_heading_is_not_invented_and_canada_stays_xml() -> None:
    """A bare report gets no bulletin id. The Canada datamart name stays .xml."""
    result = convert(
        _BARE,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        emit_translation_centre=True,
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    assert "translatedBulletinID" not in (result.xml or "")
    assert result.suggested_filename is None
    parts = parse_ahl("SAUS31 KZNY 121200")
    spec = build_ca_eccc_output_spec(
        product="METAR",
        parts=parts,
        issued_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
    )
    assert spec.suggested_filename is not None
    assert spec.suggested_filename.endswith(".xml")
    assert not spec.suggested_filename.endswith(".xml.gz")


def test_tc_f6_036_bbb_heading_is_kept_on_the_filename() -> None:
    """BBB stays on the compact id and the guideline name."""
    bulletin = "SAUS31 KZNY 121200 RRA\nMETAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013=\n"
    result = convert(
        bulletin,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        emit_translation_centre=True,
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    assert _attr(result.xml or "", "translatedBulletinID") == "SAUS31KZNY121200RRA"
    name = result.suggested_filename or ""
    assert name.startswith("A_LAUS31KZNY121200RRA")
    assert name.endswith(".xml.gz")


def test_tc_f6_036_canada_convert_does_not_return_the_gzip_name() -> None:
    """The Canada datamart name stays on the output spec; convert does not add .xml.gz."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="ca_eccc",
    )
    assert result.suggested_filename is None


def test_tc_f6_036_failed_heading_without_a_centre_omits_yuzz() -> None:
    """A parsed heading does not fall back to the fictional centre."""
    result = convert(
        _FAILED,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "translatedBulletinID") == _HEADING_ID
    assert _attr(xml, "translationCentreDesignator") == ""
    assert _attr(xml, "translationCentreName") == ""
    assert "YUZZ" not in xml
    assert "TTAAiiCCCYYGGgg" not in xml
