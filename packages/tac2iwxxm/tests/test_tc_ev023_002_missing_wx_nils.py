"""TC-EV023-002 — Missing WX / Guidance nils (S030 / EV-023 T2.1).

Locks ``common/nil`` vs ``iwxxm/nil`` URI families per product vocabulary:
aerodrome METAR/SPECI Guidance nils use ``codes.wmo.int/common/nil/...``;
VONA may use ``codes.wmo.int/iwxxm/nil/...`` when official examples do.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_EV023 = _FIXTURES / "ev023"
_AMD79 = _REPO / "vendor" / "schemas" / "iwxxm-translation" / "Amd79-80-2023"
_VENDOR_METAR_A3 = _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples" / "metar-A3-1.xml"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

COMMON_NIL_PREFIX = "http://codes.wmo.int/common/nil/"
IWXXM_NIL_PREFIX = "http://codes.wmo.int/iwxxm/nil/"

NIL_NSC = f"{COMMON_NIL_PREFIX}nothingOfOperationalSignificance"
NIL_NOT_OBS = f"{COMMON_NIL_PREFIX}notObservable"
NIL_MISSING = f"{COMMON_NIL_PREFIX}missing"

_NIL_REASON = re.compile(r'nilReason="([^"]+)"')
_PRESENT_WX = re.compile(r"<iwxxm:presentWeather\b([^>]*)/?>", re.DOTALL)
_TREND_WEATHER = re.compile(r"<iwxxm:weather\b([^>]*)/?>", re.DOTALL)
_VISIBILITY = re.compile(r"<iwxxm:visibility\b([^>]*)/?>", re.DOTALL)


def nil_reasons(xml: str) -> list[str]:
    """
    Return all ``nilReason`` URI values in document order.

    Parameters
    ----------
    xml : str
        IWXXM document text.

    Returns
    -------
    list[str]
        NilReason attribute values.
    """
    return _NIL_REASON.findall(xml)


def assert_aerodrome_nils_use_common_family(xml: str) -> None:
    """
    Fail when a METAR/SPECI document uses ``iwxxm/nil`` for any nilReason.

    Parameters
    ----------
    xml : str
        Aerodrome METAR or SPECI IWXXM text.
    """
    reasons = nil_reasons(xml)
    assert reasons, "expected at least one nilReason in aerodrome fixture"
    for uri in reasons:
        assert uri.startswith(COMMON_NIL_PREFIX), f"aerodrome METAR/SPECI nilReason must use common/nil, got {uri!r}"
        assert not uri.startswith(IWXXM_NIL_PREFIX), f"aerodrome METAR/SPECI must not use iwxxm/nil, got {uri!r}"


def assert_allows_iwxxm_nil_family(xml: str) -> None:
    """
    Fail when a VONA-style document has no ``iwxxm/nil`` nilReason.

    Parameters
    ----------
    xml : str
        VONA / volcanic IWXXM text that should carry iwxxm/nil.
    """
    reasons = nil_reasons(xml)
    assert any(u.startswith(IWXXM_NIL_PREFIX) for u in reasons), (
        f"expected iwxxm/nil family in VONA fixture, got {reasons!r}"
    )


def _attrs_nil(attrs: str) -> str | None:
    m = re.search(r'nilReason="([^"]+)"', attrs)
    return m.group(1) if m else None


def assert_present_weather_not_observable(xml: str) -> None:
    """Assert observation presentWeather uses common/nil/notObservable."""
    matches = _PRESENT_WX.findall(xml)
    assert matches, "expected iwxxm:presentWeather"
    uris = [_attrs_nil(a) for a in matches]
    assert NIL_NOT_OBS in uris, f"expected presentWeather {NIL_NOT_OBS}, got {uris!r}"
    for uri in uris:
        if uri is not None:
            assert uri.startswith(COMMON_NIL_PREFIX), uri


def assert_trend_weather_nsw(xml: str) -> None:
    """Assert trend forecast weather uses common/nil/nothingOfOperationalSignificance."""
    matches = _TREND_WEATHER.findall(xml)
    assert matches, "expected iwxxm:weather in trend"
    uris = [_attrs_nil(a) for a in matches]
    assert NIL_NSC in uris, f"expected trend weather {NIL_NSC}, got {uris!r}"


def assert_visibility_not_observable(xml: str) -> None:
    """Assert visibility association uses common/nil/notObservable."""
    matches = _VISIBILITY.findall(xml)
    assert matches, "expected iwxxm:visibility"
    uris = [_attrs_nil(a) for a in matches]
    assert NIL_NOT_OBS in uris, f"expected visibility {NIL_NOT_OBS}, got {uris!r}"


@pytest.mark.parametrize(
    ("tac_path", "product"),
    [
        (_AMD79 / "metar" / "EDDH-290020Z.tac", "SPECI"),
        (_AMD79 / "metar" / "LTCN-282350Z.tac", "SPECI"),
    ],
    ids=["amd79_eddh_nsw", "amd79_ltcn_nsw"],
)
def test_tc_ev023_002_nsw_trend_uses_common_nil(tac_path: Path, product: str) -> None:
    from tac2iwxxm import convert

    assert tac_path.is_file(), tac_path
    tac = tac_path.read_text(encoding="utf-8")
    assert "NSW" in tac
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert_trend_weather_nsw(result.xml)
    assert_aerodrome_nils_use_common_family(result.xml)


def test_tc_ev023_002_auto_wx_slash_uses_common_nil_not_observable() -> None:
    """Guidance: present weather '//' → common/nil/notObservable."""
    from tac2iwxxm import convert

    tac = "METAR KJFK 231751Z AUTO 18012KT 9999 // SCT020 15/07 Q1013="
    result = convert(
        tac,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert_present_weather_not_observable(result.xml)
    assert_aerodrome_nils_use_common_family(result.xml)


@pytest.mark.xfail(
    reason="T2.2: parse AUTO ////SM visibility + emit Guidance common/nil notObservable",
    strict=True,
)
def test_tc_ev023_002_cwfd_auto_missing_wx_and_vis_common_nil() -> None:
    """Amd79 CWFD: AUTO ////SM // → visibility + presentWeather common/nil/notObservable."""
    from tac2iwxxm import convert

    tac_path = _AMD79 / "metar" / "CWFD-290000Z.tac"
    assert tac_path.is_file(), tac_path
    result = convert(
        tac_path.read_text(encoding="utf-8"),
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert_present_weather_not_observable(result.xml)
    assert_visibility_not_observable(result.xml)
    assert_aerodrome_nils_use_common_family(result.xml)
    # Official suite also emits rvr missing when sensors absent / inapplicable path.
    assert NIL_MISSING in nil_reasons(result.xml) or "rvr" in result.xml.lower()


@pytest.mark.xfail(
    reason="T2.2: parse AUTO //// visibility + emit Guidance common/nil notObservable",
    strict=True,
)
def test_tc_ev023_002_enfb_auto_vis_slash_uses_common_nil() -> None:
    """Amd79 ENFB: AUTO //// visibility → common/nil/notObservable."""
    from tac2iwxxm import convert

    tac_path = _AMD79 / "metar" / "ENFB-282350Z.tac"
    assert tac_path.is_file(), tac_path
    result = convert(
        tac_path.read_text(encoding="utf-8"),
        product="SPECI",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert_visibility_not_observable(result.xml)
    assert_aerodrome_nils_use_common_family(result.xml)


def test_tc_ev023_002_vendor_metar_a3_nsw_common_nil() -> None:
    """Pin 2025-2 metar-A3-1 NSW weather uses common/nil (not iwxxm/nil)."""
    xml = _VENDOR_METAR_A3.read_text(encoding="utf-8")
    assert_trend_weather_nsw(xml)
    assert_aerodrome_nils_use_common_family(xml)


def test_tc_ev023_002_negative_aerodrome_iwxxm_nil_rejected() -> None:
    """Hand-built METAR with iwxxm/nil weather fails aerodrome family assert."""
    path = _EV023 / "metar_weather_iwxxm_nil.negative.xml"
    xml = path.read_text(encoding="utf-8")
    assert any(u.startswith(IWXXM_NIL_PREFIX) for u in nil_reasons(xml))
    with pytest.raises(AssertionError, match="common/nil"):
        assert_aerodrome_nils_use_common_family(xml)


def test_tc_ev023_002_vona_allows_iwxxm_nil_family() -> None:
    """VONA vocabulary may encode iwxxm/nil (official vona-A7-1 pattern)."""
    path = _EV023 / "vona_iwxxm_nil.positive.xml"
    xml = path.read_text(encoding="utf-8")
    assert_allows_iwxxm_nil_family(xml)
