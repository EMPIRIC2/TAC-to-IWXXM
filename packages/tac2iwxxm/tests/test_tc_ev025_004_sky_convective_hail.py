"""TC-EV025-004 / M4.2 — Sky / convective / hail (UJ-040).

Asserts ``CharacterOfTheSky`` (FMH-1 ``8/CLCMCH``), ``ConvectiveCloudLocation``
(CB/TS/TCU remarks), and ``HailstoneSize`` (``GR`` size) under ``iwxxm_us``.

XML pins follow iwxxm-us 3.0 PDF sample instances
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm import convert
from tac2iwxxm.products.metar_speci import parse_metar_speci

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# PDF CharacterOfTheSky sample 1: Cu humilis / no mid / Cs → BUFR 31/20/17 via 8/107.
_TAC_SKY = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 8/107="

# PDF CharacterOfTheSky sample 2: St + mid/high notObservable → 8/7//.
_TAC_SKY_NIL = "METAR KJFK 231751Z 18008KT 10SM OVC008 25/18 A2992 RMK AO2 8/7//="

# PDF ConvectiveCloudLocation: distant CB west moving NE.
_TAC_CB = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 CB DSNT W MOV NE="

# PDF: thunderstorm vicinity S–SW moving SE.
_TAC_TS = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 TS VC S-SW MOV SE="

# PDF HailstoneSize: 1 3/4 inch.
_TAC_HAIL = "METAR KJFK 231751Z 18008KT 3SM -GR SCT020 15/10 A2992 RMK AO2 GR 1 3/4="

# PDF HailstoneSize BELOW: less than 1/4 inch.
_TAC_HAIL_LT = "METAR KJFK 231751Z 18008KT 5SM SCT020 15/10 A2992 RMK AO2 GR LT 1/4="

_BUFR_CLOUD = "http://codes.wmo.int/bufr4/codeflag/0-20-012/{code}"
_CB_HREF = "https://codes.nws.noaa.gov/FMH-1/ConvectiveCloudType/CUMULONIMBUS"
_TS_HREF = "https://codes.nws.noaa.gov/FMH-1/ConvectiveCloudType/THUNDERSTORM"
_DISTANT = "https://codes.nws.noaa.gov/FMH-1/QualitativeDistance/DISTANT"
_VICINITY = "https://codes.nws.noaa.gov/FMH-1/QualitativeDistance/VICINITY"
_NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"


def test_tc_ev025_004_sky_character_parses_bufr_codes() -> None:
    """Parse 8/CLCMCH into CharacterOfTheSky BUFR hrefs."""
    ir = parse_metar_speci(_TAC_SKY, product="METAR")
    sky = ir.get("character_of_the_sky")
    assert isinstance(sky, dict)
    assert sky.get("low_href") == _BUFR_CLOUD.format(code=31)
    assert sky.get("middle_href") == _BUFR_CLOUD.format(code=20)
    assert sky.get("high_href") == _BUFR_CLOUD.format(code=17)


def test_tc_ev025_004_sky_character_emits_character_of_the_sky() -> None:
    """Convert must emit CharacterOfTheSky inside VOP."""
    result = convert(
        _TAC_SKY,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:CharacterOfTheSky" in xml
    assert _BUFR_CLOUD.format(code=31) in xml
    assert _BUFR_CLOUD.format(code=20) in xml
    assert _BUFR_CLOUD.format(code=17) in xml


def test_tc_ev025_004_sky_character_nil_reason_for_slash() -> None:
    """Solidus layers above overcast map to notObservable nilReason."""
    result = convert(
        _TAC_SKY_NIL,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:CharacterOfTheSky" in xml
    assert _BUFR_CLOUD.format(code=37) in xml
    assert _NIL_NOT_OBS in xml


def test_tc_ev025_004_cb_emits_convective_cloud_location() -> None:
    """CB DSNT W MOV NE → ConvectiveCloudLocation with DISTANT + motion."""
    result = convert(
        _TAC_CB,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:ConvectiveCloudLocation" in xml
    assert _CB_HREF in xml
    assert _DISTANT in xml
    assert 'directionOfMotion uom="deg">45</iwxxm-us:directionOfMotion>' in xml
    assert ">247.5<" in xml
    assert ">292.5<" in xml


def test_tc_ev025_004_ts_vicinity_emits_thunderstorm_convection() -> None:
    """TS VC S-SW MOV SE → THUNDERSTORM + VICINITY + motion 135."""
    result = convert(
        _TAC_TS,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:ConvectiveCloudLocation" in xml
    assert _TS_HREF in xml
    assert _VICINITY in xml
    assert 'directionOfMotion uom="deg">135</iwxxm-us:directionOfMotion>' in xml


def test_tc_ev025_004_hail_emits_hailstone_size() -> None:
    """GR 1 3/4 → HailstoneSize maximumDiameter 1.75 in."""
    result = convert(
        _TAC_HAIL,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:HailstoneSize" in xml
    assert 'maximumDiameter uom="[in_i]">1.75</iwxxm-us:maximumDiameter>' in xml


def test_tc_ev025_004_hail_below_emits_size_operator() -> None:
    """GR LT 1/4 → diameter 0.25 with sizeOperator BELOW."""
    result = convert(
        _TAC_HAIL_LT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:HailstoneSize" in xml
    assert 'maximumDiameter uom="[in_i]">0.25</iwxxm-us:maximumDiameter>' in xml
    assert "<iwxxm-us:sizeOperator>BELOW</iwxxm-us:sizeOperator>" in xml
