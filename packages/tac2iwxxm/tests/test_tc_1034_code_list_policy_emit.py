"""TC-1034: tac2iwxxm emit uses CA code-list policy URIs.

[Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.code_list_policy import resolve_national_href


def test_tc_1034_004_emit_resolve_ic_not_wmo() -> None:
    """IC resolves to code-ca, never WMO 4678."""
    href = resolve_national_href(area="forecast_weather", token="IC")
    assert href is not None
    assert "code-ca/present_and_forecast_weather/IC" in href
    assert "codes.wmo.int" not in href


def test_tc_1034_005_emit_resolve_gfa_compound() -> None:
    """GFA compound phenomena resolve to code-ca airmet_weather_phenomena."""
    href = resolve_national_href(area="airmet_phenomena", token="SFC_VIS_and_BKN_CLD")
    assert href is not None
    assert "airmet_weather_phenomena/SFC_VIS_and_BKN_CLD" in href
