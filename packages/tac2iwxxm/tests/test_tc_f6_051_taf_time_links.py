"""TC-F6-051: TAF forecast time links stay inside the document.

[Corpus: product §F6] [Corpus: tests §TC-F6-051]
"""

from __future__ import annotations

from tac2iwxxm.taf_time_links import (
    base_forecast_phenomenon_href,
    failed_preview_nil_element,
    forecast_time_href,
    unresolved_internal_hrefs,
)

from tac2iwxxm import convert

_VRB = "TAF TNCM 081200Z 0812/0912 VRB03KT 9999 FEW020="
_PROB = "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB40 TEMPO 0818/0822 4000 TSRA="
_NIL = "http://codes.wmo.int/common/nil/missing"


def test_forecast_time_href_uses_the_id_or_stays_empty() -> None:
    """A forecast time link is a fragment of an id in the same document."""
    assert forecast_time_href("t.valid") == "#t.valid"
    assert forecast_time_href("t.chg.1") == "#t.chg.1"
    assert forecast_time_href("") == ""
    assert base_forecast_phenomenon_href() == "#t.valid"


def test_unresolved_internal_hrefs_reports_only_missing_targets() -> None:
    """Hash links resolve when the target gml:id is present."""
    linked = '<gml:TimePeriod gml:id="t.valid"/><iwxxm:phenomenonTime xlink:href="#t.valid"/>'
    assert unresolved_internal_hrefs(linked) == ()
    assert unresolved_internal_hrefs('<gml:TimePeriod gml:id="t.valid"/>') == ()
    broken = '<iwxxm:phenomenonTime xlink:href="#missing"/>'
    assert unresolved_internal_hrefs(broken) == ("missing",)


def test_failed_preview_nil_element_is_a_forecast_for_taf() -> None:
    """A failed TAF shell names the forecast element. Other products keep observation."""
    assert failed_preview_nil_element("TAF") == "baseForecast"
    assert failed_preview_nil_element("taf") == "baseForecast"
    assert failed_preview_nil_element("METAR") == "observation"
    assert failed_preview_nil_element("SPECI") == "observation"
    assert failed_preview_nil_element("") == "observation"


def _convert(tac: str) -> str:
    result = convert(tac, product="TAF", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    assert result.xml is not None
    return result.xml


def test_tc_f6_051_vrb_and_prob_taf_time_links_resolve() -> None:
    """A one-line VRB TAF and a one-line PROB TAF keep every time link in-document."""
    for tac in (_VRB, _PROB):
        xml = _convert(tac)
        assert unresolved_internal_hrefs(xml) == ()
        assert 'xlink:href="#t.valid"' in xml
        assert 'gml:id="t.valid"' in xml
        assert "00000000-0000-4000-8000-000000000001" not in xml
    prob = _convert(_PROB)
    assert 'gml:id="t.chg.1"' in prob
    assert "PROBABILITY_40_TEMPORARY_FLUCTUATIONS" in prob


def test_tc_f6_051_failed_taf_preview_uses_a_base_forecast() -> None:
    """A failed TAF preview does not emit a METAR observation element."""
    result = convert(
        "TAF YUDO 151800Z 1600/1618 INVALID",
        product="TAF",
        profile="annex3",
        iwxxm_version="2025-2",
        preview=True,
    )
    assert result.ok is False
    assert result.xml is not None
    xml = result.xml
    assert "iwxxm:TAF" in xml
    assert f'<iwxxm:baseForecast nilReason="{_NIL}"/>' in xml
    assert "iwxxm:observation" not in xml
    assert "MeteorologicalAerodromeObservation" not in xml


def test_tc_f6_051_failed_metar_preview_keeps_the_observation() -> None:
    """A failed METAR preview still uses the observation element."""
    result = convert(
        "METAR KJFK 121151Z INVALID",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        preview=True,
    )
    assert result.xml is not None
    assert f'<iwxxm:observation nilReason="{_NIL}"/>' in result.xml
