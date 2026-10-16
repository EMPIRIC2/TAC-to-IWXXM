"""TC-F6-053: mixed statute miles and the shared 10 km visibility convention."""

from __future__ import annotations

from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.visibility_measure import (
    METAR_STATUTE_MILE_GROUP,
    TAF_STATUTE_MILE_GROUP,
    prevailing_from_metre_group,
    prevailing_from_statute_miles,
)

from tac2iwxxm import convert

_MIXED = "METAR TJSJ 081200Z 14006KT 1 1/2SM FEW020 28/24 A2992="
_HALF = "METAR TJSJ 081200Z 14006KT 1/2SM FEW020 28/24 A2992="
_METAR_10SM = "METAR TJSJ 081200Z 14006KT 10SM FEW020 28/24 A2992="
_METAR_9999 = "METAR TJSJ 081200Z 14006KT 9999 FEW020 28/24 Q1013="
_TAF_10SM = "TAF TJSJ 081200Z 0812/0912 14006KT 10SM FEW020="
_TAF_9999 = "TAF TJSJ 081200Z 0812/0912 14006KT 9999 FEW020="
_TAF_6SM = "TAF TJSJ 081200Z 0812/0912 14006KT 6SM FEW020="
_TAF_P6SM = "TAF TJSJ 081200Z 0812/0912 14006KT P6SM FEW020="
_ABOVE = "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
_TEN_KM = '<iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>'


def test_ten_statute_miles_and_the_neighbours() -> None:
    assert prevailing_from_statute_miles(9) == (14484, False)
    assert prevailing_from_statute_miles(10) == (10000, True)
    assert prevailing_from_statute_miles(11) == (10000, True)
    assert prevailing_from_statute_miles(1.5) == (2414, False)


def test_9999_matches_ten_kilometres_and_9998_stays() -> None:
    assert prevailing_from_metre_group(9998) == (9998, False)
    assert prevailing_from_metre_group(9999) == (10000, True)
    assert prevailing_from_metre_group(10000) == (10000, True)


def test_statute_mile_group_keeps_the_mixed_fraction() -> None:
    mixed = METAR_STATUTE_MILE_GROUP.search("1 1/2SM")
    half = METAR_STATUTE_MILE_GROUP.search("1/2SM")
    ten = METAR_STATUTE_MILE_GROUP.search("10SM")
    assert mixed is not None
    assert mixed.group("vis") == "1 1/2"
    assert half is not None
    assert half.group("vis") == "1/2"
    assert ten is not None
    assert ten.group("vis") == "10"
    assert METAR_STATUTE_MILE_GROUP.search("P6SM") is None
    taf_greater = TAF_STATUTE_MILE_GROUP.search("P6SM")
    assert taf_greater is not None
    assert taf_greater.group("mod") == "P"
    assert taf_greater.group("vis") == "6"


def test_mixed_statute_miles_are_about_2400_m() -> None:
    ir = parse_metar_speci(_MIXED, product="METAR")
    assert ir["visibility_m"] == 2414
    assert ir["visibility_m"] != 3219
    assert ir["visibility_above"] is False
    assert ir["visibility_sm"] == 1.5
    result = convert(_MIXED, product="METAR")
    assert result.ok is True
    assert result.xml is not None
    assert '<iwxxm:prevailingVisibility uom="m">2414</iwxxm:prevailingVisibility>' in result.xml
    assert _ABOVE not in result.xml

    half = parse_metar_speci(_HALF, product="METAR")
    assert half["visibility_m"] == 805
    assert half["visibility_sm"] == 0.5


def test_10sm_and_9999_emit_10000_m_above_on_metar_and_taf() -> None:
    for tac, product in (
        (_METAR_10SM, "METAR"),
        (_METAR_9999, "METAR"),
        (_TAF_10SM, "TAF"),
        (_TAF_9999, "TAF"),
    ):
        result = convert(tac, product=product)
        assert result.ok is True
        assert result.xml is not None
        assert _TEN_KM in result.xml
        assert _ABOVE in result.xml

    metar_sm = parse_metar_speci(_METAR_10SM, product="METAR")
    metar_m = parse_metar_speci(_METAR_9999, product="METAR")
    assert metar_sm["visibility_m"] == metar_m["visibility_m"] == 10000
    assert metar_sm["visibility_above"] is True
    assert metar_m["visibility_above"] is True
    assert metar_sm["visibility_sm"] == 10

    taf_sm = parse_taf(_TAF_10SM, product="TAF")
    taf_m = parse_taf(_TAF_9999, product="TAF")
    assert taf_sm["visibility_m"] == taf_m["visibility_m"] == 10000
    assert taf_sm["visibility_above"] is True
    assert taf_m["visibility_above"] is True
    assert taf_sm["visibility_sm"] == 10


def test_taf_miles_below_ten_keep_the_existing_statute_mile_record() -> None:
    six = parse_taf(_TAF_6SM, product="TAF")
    assert six["visibility_sm"] == 6
    assert six["visibility_above"] is False
    assert "visibility_m" not in six

    greater = parse_taf(_TAF_P6SM, product="TAF")
    assert greater["visibility_sm"] == 6
    assert greater["visibility_above"] is True
    assert "visibility_m" not in greater
