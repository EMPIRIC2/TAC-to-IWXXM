"""TC-F6-035 — lock emitted nilReason hrefs (EV-1278 / #1278).

Does not change emitters. Annex 3 ``2025-2`` and ``2023-1`` keep the same
nilReason values. Space-weather intensity stays on ``common/nil``. VONA stays
on ``iwxxm/nil``. Canada 3.0.0 does not use ``iwxxm/nil``.
[Corpus: product §F6] [Corpus: tests §TC-F6-035]
"""

from __future__ import annotations

import re
from pathlib import Path

from tac2iwxxm import convert

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_ANNEX3 = _FIXTURES / "annex3_golden"
_CA_METAR = _FIXTURES / "profiles" / "CA_ECCC" / "METAR" / "valid" / "metar_basic.tac"

_COMMON = "http://codes.wmo.int/common/nil/"
_IWXXM = "http://codes.wmo.int/iwxxm/nil/"
_NIL = re.compile(r'nilReason="([^"]+)"')
_PINS = ("2025-2", "2023-1")

_METAR_NIL = "METAR KJFK 231751Z AUTO 18012KT 9999 // SCT020 15/07 Q1013="


def _reasons(xml: str) -> list[str]:
    return _NIL.findall(xml)


def _convert(tac: str, *, product: str, profile: str, iwxxm_version: str) -> str:
    result = convert(tac, product=product, profile=profile, iwxxm_version=iwxxm_version)
    assert result.ok is True, result.issues
    return result.xml


def test_tc_f6_035_metar_nil_hrefs_match_on_both_global_lines() -> None:
    """Aerodrome nils stay on common/nil, and 2023-1 matches 2025-2."""
    documents = {pin: _convert(_METAR_NIL, product="METAR", profile="annex3", iwxxm_version=pin) for pin in _PINS}
    reasons = {pin: _reasons(xml) for pin, xml in documents.items()}
    assert reasons["2025-2"]
    assert reasons["2025-2"] == reasons["2023-1"]
    assert all(uri.startswith(_COMMON) for uri in reasons["2025-2"])
    assert _IWXXM not in documents["2025-2"]


def test_tc_f6_035_space_weather_intensity_stays_on_common_nil() -> None:
    """intensityAndRegion uses common/nil. locationIndicator is an xlink:href."""
    tac = (_ANNEX3 / "swxa_a7_3.tac").read_text(encoding="utf-8")
    documents = {pin: _convert(tac, product="SWXA", profile="annex3", iwxxm_version=pin) for pin in _PINS}
    expected = f"{_COMMON}nothingOfOperationalSignificance"
    for xml in documents.values():
        assert f'intensityAndRegion nilReason="{expected}"' in xml
        assert "iwxxm/nil" not in xml
        assert "locationIndicator" in xml
        assert "locationIndicator nilReason=" not in xml
    assert _reasons(documents["2025-2"]) == _reasons(documents["2023-1"])


def test_tc_f6_035_vona_stays_on_iwxxm_nil() -> None:
    """2025-2 VONA keeps iwxxm/nil. 2023-1 VONA keeps its current empty nil set."""
    tac = (_ANNEX3 / "vona_a7_1.tac").read_text(encoding="utf-8")
    current = _convert(tac, product="VONA", profile="annex3", iwxxm_version="2025-2")
    previous = _convert(tac, product="VONA", profile="annex3", iwxxm_version="2023-1")
    assert f"{_IWXXM}inapplicable" in current
    assert "common/nil" not in current
    assert _reasons(previous) == []
    assert "common/nil" not in previous
    assert "iwxxm/nil" not in previous


def test_tc_f6_035_canada_metar_does_not_use_iwxxm_nil() -> None:
    """Canada 3.0.0 is unchanged and does not pick up the IWXXM nil list."""
    tac = _CA_METAR.read_text(encoding="utf-8")
    xml = _convert(tac, product="METAR", profile="ca_eccc", iwxxm_version="3.0.0")
    assert "iwxxm/nil" not in xml
    for uri in _reasons(xml):
        assert not uri.startswith(_IWXXM)
