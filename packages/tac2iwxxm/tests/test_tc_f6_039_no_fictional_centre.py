"""TC-F6-039 — no fictional translation centre (EV-1290 / #1290).

[Corpus: product §F6] [Corpus: tests §TC-F6-039]
"""

from __future__ import annotations

import re

from tac2iwxxm import convert

_FAILED_BARE = "METAR KJFK 121151Z INVALID 18012KT 9999 FEW020 15/07 Q1013="
_FAILED_BULLETIN = "SAUS31 KZNY 121200\nMETAR KJFK 121151Z INVALID 18012KT 9999 FEW020 15/07 Q1013=\n"
_HEADING_ID = "SAUS31KZNY121200"
_CENTRE = "CWAO"
_CENTRE_NAME = "Test translation centre"


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'{name}="([^"]*)"', xml)
    return match.group(1) if match else None


def test_tc_f6_039_failed_metar_without_a_heading_omits_the_centre() -> None:
    """A failed paste with no heading does not invent a centre or a bulletin id."""
    result = convert(
        _FAILED_BARE,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert "translationFailedTAC" in xml
    assert "INVALID" in (_attr(xml, "translationFailedTAC") or "")
    assert 'permissibleUsage="OPERATIONAL"' in xml
    assert "YUZZ" not in xml
    assert "Fictional translation centre" not in xml
    assert "TTAAiiCCCYYGGgg" not in xml
    assert "translationCentreDesignator" not in xml
    assert "translationCentreName" not in xml
    assert "translatedBulletinID" not in xml


def test_tc_f6_039_failed_bulletin_keeps_the_heading_and_centre() -> None:
    """A parsed heading and a caller centre stay on the failed shell."""
    result = convert(
        _FAILED_BULLETIN,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "translatedBulletinID") == _HEADING_ID
    assert _attr(xml, "translationCentreDesignator") == _CENTRE
    assert _attr(xml, "translationCentreName") == _CENTRE_NAME
    assert "YUZZ" not in xml


def test_tc_f6_039_supplied_centre_without_a_heading_is_kept() -> None:
    """A caller centre is written even when the paste has no heading."""
    result = convert(
        _FAILED_BARE,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        translation_centre_designator=_CENTRE,
        translation_centre_name=_CENTRE_NAME,
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "translationCentreDesignator") == _CENTRE
    assert _attr(xml, "translationCentreName") == _CENTRE_NAME
    assert "translatedBulletinID" not in xml
    assert "YUZZ" not in xml
    assert "TTAAiiCCCYYGGgg" not in xml
