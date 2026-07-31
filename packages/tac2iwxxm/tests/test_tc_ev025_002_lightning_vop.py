"""TC-EV025-002 / #811 — Lightning / VisuallyObservablePhenomena (UJ-040).

Asserts ``iwxxm-us:VisuallyObservablePhenomena`` wrapping ``ObservedLightning``
(frequency / type / qualitativeDistance) under ``profile=iwxxm_us``.

TAC shapes follow FMH-1 lightning REMARKS; XML shape pins follow iwxxm-us 3.0
PDF sample instances (local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# PDF sample 1 analogue: distant lightning N–NE of the aerodrome.
_TAC_LTG_DSNT = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 LTG DSNT N-NE="

# PDF sample 3 analogue: continuous IC/CC/CG lightning NE–E–SE (CCCGIC type).
_TAC_LTG_CONS = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 CONS LTGICCCCG NE-E-SE="

_DISTANT_HREF = "https://codes.nws.noaa.gov/FMH-1/QualitativeDistance/DISTANT"
_FREQ_CONTINUOUS_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningFrequency/CONTINUOUS"
_TYPE_CCCGIC_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningType/CCCGIC"


def test_tc_ev025_002_distant_lightning_emits_vop_observed_lightning() -> None:
    """Convert iwxxm_us must emit VOP + ObservedLightning with DISTANT distance."""
    result = convert(
        _TAC_LTG_DSNT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:VisuallyObservablePhenomena" in xml
    assert "iwxxm-us:ObservedLightning" in xml
    assert _DISTANT_HREF in xml
    assert "iwxxm-us:qualitativeDistance" in xml
    assert "iwxxm-us:Sector" in xml


def test_tc_ev025_002_continuous_lightning_emits_frequency_and_type() -> None:
    """Convert iwxxm_us must emit CONTINUOUS frequency + CCCGIC type (PDF sample 3)."""
    result = convert(
        _TAC_LTG_CONS,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:VisuallyObservablePhenomena" in xml
    assert "iwxxm-us:ObservedLightning" in xml
    assert _FREQ_CONTINUOUS_HREF in xml
    assert _TYPE_CCCGIC_HREF in xml
    assert "iwxxm-us:frequency" in xml
    assert "iwxxm-us:type" in xml
