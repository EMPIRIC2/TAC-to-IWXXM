"""TC-EV025-004 / M4.3 - Sector / Obscurations / SecondLocation / Tower (UJ-040).

Asserts ``SectorVisibility``, ``Obscurations`` (VOP), ``ObservedAtSecondLocation``
(+ ``SensorLocation``), and ``TowerVisibility`` under ``iwxxm_us``.

XML pins follow iwxxm-us 3.0 PDF sample shapes
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm.products.metar_speci import parse_metar_speci

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# PDF SectorVisibility: 1200 m NE → mid-point 45° (use 3/4 SM ≈ 1207 m).
_TAC_SECTOR = "METAR KJFK 231751Z 18008KT 2SM BR BKN008 14/13 A2995 RMK AO2 VIS 3/4 NE="

# PDF Obscurations: broken smoke at 500 ft.
_TAC_OBSC = "METAR KJFK 231751Z 18008KT 3SM FU BKN020 18/12 A2990 RMK AO2 FU BKN005="

# PDF ObservedAtSecondLocation: CIG 200 ft at RUNWAY 11.
_TAC_SECOND = "METAR KJFK 231751Z 18008KT 2SM BR BKN008 14/13 A2995 RMK AO2 CIG 002 RWY11="

# PDF ObservedAtSecondLocation: vis below sensor + RUNWAY 01L.
_TAC_SECOND_VIS = "METAR KJFK 231751Z 18008KT 1SM FG BKN001 10/10 A2988 RMK AO2 VIS M1/4 RWY01L="

# PDF TowerVisibility: ~400 m (1/4 SM) from tower.
_TAC_TOWER = "METAR KJFK 231751Z 18008KT 2SM BR BKN008 14/13 A2995 RMK AO2 TWR VIS 1/4="

# PDF TowerVisibility lessThan.
_TAC_TOWER_LT = "METAR KJFK 231751Z 18008KT 1/2SM FG BKN002 10/10 A2988 RMK AO2 TWR VIS M1/4="

_CLOUD_BKN = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/BKN"
_WX_FU = "http://codes.wmo.int/306/4678/FU"


def test_tc_ev025_004_sector_vis_parses_direction() -> None:
    """Parse VIS n/n DIR into sector_visibility IR."""
    ir = parse_metar_speci(_TAC_SECTOR, product="METAR")
    sector = ir.get("sector_visibility")
    assert isinstance(sector, dict)
    assert sector.get("direction_deg") == 45.0
    assert sector.get("visibility_m") == 1207  # round(0.75 * 1609.344)


def test_tc_ev025_004_sector_vis_emits_sector_visibility() -> None:
    """Convert must emit SectorVisibility on AerodromeHorizontalVisibility."""
    result = convert(
        _TAC_SECTOR,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:SectorVisibility" in xml
    assert 'visibility uom="m">1207</iwxxm-us:visibility>' in xml
    assert 'direction uom="deg">45</iwxxm-us:direction>' in xml


def test_tc_ev025_004_obscuration_emits_in_vop() -> None:
    """FU BKN005 remark → Obscurations inside VisuallyObservablePhenomena."""
    result = convert(
        _TAC_OBSC,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:Obscurations" in xml
    assert 'heightOfWeatherPhenomenon uom="[ft_i]">500</iwxxm-us:heightOfWeatherPhenomenon>' in xml
    assert _CLOUD_BKN in xml
    assert _WX_FU in xml


def test_tc_ev025_004_second_location_ceiling_emits() -> None:
    """CIG 002 RWY11 → ObservedAtSecondLocation + SensorLocation description."""
    result = convert(
        _TAC_SECOND,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:ObservedAtSecondLocation" in xml
    assert 'ceilingHeight uom="[ft_i]">200</iwxxm-us:ceilingHeight>' in xml
    assert "<iwxxm-us:description>RUNWAY 11</iwxxm-us:description>" in xml


def test_tc_ev025_004_second_location_vis_below_sensor() -> None:
    """VIS M1/4 RWY01L → visibilityBelowSensorMinimum + RUNWAY 01L."""
    result = convert(
        _TAC_SECOND_VIS,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert 'ObservedAtSecondLocation visibilityBelowSensorMinimum="true"' in xml
    assert "iwxxm-us:visibility" in xml
    assert "<iwxxm-us:description>RUNWAY 01L</iwxxm-us:description>" in xml


def test_tc_ev025_004_tower_vis_emits() -> None:
    """TWR VIS 1/4 → TowerVisibility ~402 m."""
    result = convert(
        _TAC_TOWER,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:TowerVisibility" in xml
    assert 'towerVisibility uom="m">402</iwxxm-us:towerVisibility>' in xml


def test_tc_ev025_004_tower_vis_less_than() -> None:
    """TWR VIS M1/4 → lessThan true."""
    result = convert(
        _TAC_TOWER_LT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:TowerVisibility" in xml
    assert "<iwxxm-us:lessThan>true</iwxxm-us:lessThan>" in xml
