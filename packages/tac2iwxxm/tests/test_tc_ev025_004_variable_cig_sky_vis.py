"""TC-EV025-004 / M4.4 — Variable CIG / SKY / VIS (UJ-040).

Asserts ``VariableCeilingHeight``, ``VariableSkyCondition``, and
``VariableVisibility`` under ``iwxxm_us``.

XML pins follow iwxxm-us 3.0 PDF sample shapes
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm import convert
from tac2iwxxm.products.metar_speci import parse_metar_speci

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# PDF VariableCeilingHeight: 300–800 ft.
_TAC_CIG = "METAR KJFK 231751Z 18008KT 2SM BR BKN005 14/13 A2995 RMK AO2 CIG 003V008="

# PDF VariableSkyCondition: BKN ↔ OVC.
_TAC_SKY = "METAR KJFK 231751Z 18008KT 2SM BR BKN014 14/13 A2995 RMK AO2 BKN V OVC="

# PDF VariableVisibility: 1–3 SM → ~1609–4828 m (PDF uses 1600/4800).
_TAC_VIS = "METAR KJFK 231751Z 18008KT 2SM BR BKN008 14/13 A2995 RMK AO2 VIS 1V3="

# PDF VariableVisibility belowMinimum.
_TAC_VIS_LT = "METAR KJFK 231751Z 18008KT 1SM FG BKN002 10/10 A2988 RMK AO2 VIS M1/4V1="

_CLOUD_BKN = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/BKN"
_CLOUD_OVC = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/OVC"


def test_tc_ev025_004_var_cig_parses() -> None:
    """Parse CIG minVmax into variable_ceiling IR."""
    ir = parse_metar_speci(_TAC_CIG, product="METAR")
    cig = ir.get("variable_ceiling")
    assert isinstance(cig, dict)
    assert cig.get("minimum_ft") == 300
    assert cig.get("maximum_ft") == 800


def test_tc_ev025_004_var_cig_emits() -> None:
    """Convert must emit VariableCeilingHeight on CloudLayer."""
    result = convert(
        _TAC_CIG,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:VariableCeilingHeight" in xml
    assert 'minimumHeight uom="[ft_i]">300</iwxxm-us:minimumHeight>' in xml
    assert 'maximumHeight uom="[ft_i]">800</iwxxm-us:maximumHeight>' in xml


def test_tc_ev025_004_var_sky_emits() -> None:
    """BKN V OVC → VariableSkyCondition first/second amounts."""
    result = convert(
        _TAC_SKY,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:VariableSkyCondition" in xml
    assert _CLOUD_BKN in xml
    assert _CLOUD_OVC in xml


def test_tc_ev025_004_var_vis_emits() -> None:
    """VIS 1V3 → VariableVisibility min/max metres."""
    result = convert(
        _TAC_VIS,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:VariableVisibility" in xml
    assert 'minimumVisibility uom="m">1609</iwxxm-us:minimumVisibility>' in xml
    assert 'maximumVisibility uom="m">4828</iwxxm-us:maximumVisibility>' in xml


def test_tc_ev025_004_var_vis_below_minimum() -> None:
    """VIS M1/4V1 → belowMinimum attribute."""
    result = convert(
        _TAC_VIS_LT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert 'VariableVisibility belowMinimum="true"' in xml
