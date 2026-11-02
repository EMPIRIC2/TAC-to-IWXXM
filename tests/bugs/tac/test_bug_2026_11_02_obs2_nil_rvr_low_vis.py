"""BUG-2026-11-02 — emit nil RVR when vis &lt; 1500 m and TAC has no RVR.

Schematron METAR_SPECI.MeteorologicalAerodromeObservation-2 requires
``exists(iwxxm:rvr)`` when prevailing visibility is below 1500 m. Live-eval
showed 42 fails (CYBR 3/4SM, KBVX+RVRNO, …) because annex3 only nilled RVR for
``visibility_not_observable``, not for reported low vis without an RVR group.

[Corpus: product §F6] [Corpus: product §F2]
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_bug_2026_11_02_low_vis_without_rvr_emits_nil_rvr() -> None:
    """CYBR-style 3/4SM without RVR must emit nil iwxxm:rvr (Observation-2)."""
    from tac2iwxxm import convert

    result = convert(
        "METAR CYBR 021400Z 04010KT 3/4SM BR OVC002 10/10 A2979 RMK FG4ST4 SLP100",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml is not None
    assert 'iwxxm:rvr xsi:nil="true"' in result.xml or "<iwxxm:rvr" in result.xml
    assert "nilReason=" in result.xml


@pytest.mark.unit
def test_bug_2026_11_02_low_vis_without_rvr_passes_observation2() -> None:
    """Native Schematron must not raise Observation-2 after nil RVR emit."""
    from iwxxm_validate import rust_available, validate_iwxxm

    from tac2iwxxm import convert

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(
        "METAR CYBR 021400Z 04010KT 3/4SM BR OVC002 10/10 A2979 RMK FG4ST4 SLP100",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    hard = [
        i
        for i in report.issues
        if i.severity == "error"
        and i.code == "METAR_SPECI.MeteorologicalAerodromeObservation-2"
    ]
    assert hard == [], f"Observation-2 still firing: {hard}"


@pytest.mark.unit
def test_bug_2026_11_02_rvrno_low_vis_emits_nil_rvr() -> None:
    """RVRNO with sub-1500 SM vis still needs an iwxxm:rvr element."""
    from tac2iwxxm import convert

    result = convert(
        "METAR KBVX 021456Z AUTO 13005KT 3/4SM BR OVC003 18/18 A3010 RMK AO2 RVRNO",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml is not None
    assert "iwxxm:rvr" in result.xml
