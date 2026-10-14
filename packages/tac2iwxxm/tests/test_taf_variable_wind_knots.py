"""#1400: a TAF VRB group keeps its speed and gust in the TAC unit."""

from __future__ import annotations

from tac2iwxxm.profiles.annex3_emit.taf import _taf_wind_block

from tac2iwxxm import convert

_VRB = "TAF TNCM 081200Z 0812/0912 VRB03KT 9999 FEW020="
_GUST = "TAF TNCM 081200Z 0812/0912 VRB10G20KT 9999 FEW020="
_MPS = "TAF TNCM 081200Z 0812/0912 VRB03MPS 9999 FEW020="
_TEMPO = "TAF TNCM 081200Z 0812/0912 18012KT 9999 FEW020 TEMPO 0814/0818 VRB10G20KT 5000="
_TEMPO_MPS = "TAF TNCM 081200Z 0812/0912 18005MPS 9999 FEW020 TEMPO 0814/0818 VRB05G10MPS 5000="
_CAVOK = "TAF TNCM 081200Z 0812/0912 VRB03KT CAVOK="
_NUMBERED = "TAF TNCM 081200Z 0812/0912 18012G22KT 9999 FEW020="


def _blocks(xml: str) -> list[str]:
    marker = "<iwxxm:surfaceWind>"
    close = "</iwxxm:surfaceWind>"
    blocks: list[str] = []
    start = 0
    while True:
        found = xml.find(marker, start)
        if found < 0:
            break
        end = xml.find(close, found)
        assert end > found
        blocks.append(xml[found : end + len(close)])
        start = end + len(close)
    return blocks


def _convert(tac: str) -> str:
    result = convert(tac, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    return result.xml


def test_taf_vrb_speed_stays_in_knots() -> None:
    wind = _blocks(_convert(_VRB))
    assert len(wind) == 1
    assert 'variableWindDirection="true"' in wind[0]
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">3</iwxxm:meanWindSpeed>' in wind[0]
    assert "m/s" not in wind[0]
    assert "meanWindDirection" not in wind[0]


def test_taf_vrb_gust_keeps_speed_and_gust() -> None:
    wind = _blocks(_convert(_GUST))
    assert len(wind) == 1
    assert 'variableWindDirection="true"' in wind[0]
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">10</iwxxm:meanWindSpeed>' in wind[0]
    assert '<iwxxm:windGustSpeed uom="[kn_i]">20</iwxxm:windGustSpeed>' in wind[0]


def test_taf_vrb_metres_per_second_keeps_that_unit_and_one_decimal() -> None:
    wind = _blocks(_convert(_MPS))
    assert len(wind) == 1
    assert 'variableWindDirection="true"' in wind[0]
    assert '<iwxxm:meanWindSpeed uom="m/s">3.0</iwxxm:meanWindSpeed>' in wind[0]
    assert "[kn_i]" not in wind[0]


def test_tempo_vrb_gust_stays_in_knots_beside_the_base_wind() -> None:
    blocks = _blocks(_convert(_TEMPO))
    assert len(blocks) == 2
    assert 'variableWindDirection="false"' in blocks[0]
    assert '<iwxxm:meanWindDirection uom="deg">180</iwxxm:meanWindDirection>' in blocks[0]
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">12</iwxxm:meanWindSpeed>' in blocks[0]
    assert 'variableWindDirection="true"' in blocks[1]
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">10</iwxxm:meanWindSpeed>' in blocks[1]
    assert '<iwxxm:windGustSpeed uom="[kn_i]">20</iwxxm:windGustSpeed>' in blocks[1]
    assert "meanWindDirection" not in blocks[1]


def test_tempo_vrb_metres_per_second_uses_a_bare_integer() -> None:
    blocks = _blocks(_convert(_TEMPO_MPS))
    assert len(blocks) == 2
    assert '<iwxxm:meanWindSpeed uom="m/s">5.0</iwxxm:meanWindSpeed>' in blocks[0]
    assert '<iwxxm:meanWindSpeed uom="m/s">5</iwxxm:meanWindSpeed>' in blocks[1]
    assert '<iwxxm:windGustSpeed uom="m/s">10</iwxxm:windGustSpeed>' in blocks[1]
    assert "5.0" not in blocks[1]


def test_numbered_wind_keeps_direction_speed_and_gust() -> None:
    wind = _blocks(_convert(_NUMBERED))
    assert len(wind) == 1
    assert 'variableWindDirection="false"' in wind[0]
    assert '<iwxxm:meanWindDirection uom="deg">180</iwxxm:meanWindDirection>' in wind[0]
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">12</iwxxm:meanWindSpeed>' in wind[0]
    assert '<iwxxm:windGustSpeed uom="[kn_i]">22</iwxxm:windGustSpeed>' in wind[0]


def test_cavok_omits_the_variable_wind_block() -> None:
    xml = _convert(_CAVOK)
    assert 'cloudAndVisibilityOK="true"' in xml
    assert "<iwxxm:surfaceWind>" not in xml


def test_missing_speed_omits_the_block() -> None:
    assert _taf_wind_block({}) == ""
    assert _taf_wind_block({"wind_variable": True}) == ""


def test_stored_metres_per_second_wins_over_a_stored_knot_speed() -> None:
    xml = _taf_wind_block(
        {
            "wind_variable": True,
            "wind_speed_mps": 4.0,
            "wind_speed_kt": 99,
            "wind_gust_mps": 8.0,
            "wind_gust_kt": 77,
        }
    )
    assert '<iwxxm:meanWindSpeed uom="m/s">4</iwxxm:meanWindSpeed>' in xml
    assert '<iwxxm:windGustSpeed uom="m/s">8</iwxxm:windGustSpeed>' in xml
    assert "99" not in xml
    assert "77" not in xml
    assert "[kn_i]" not in xml


def test_fractional_metres_per_second_keeps_the_tenth() -> None:
    base = _taf_wind_block({"wind_variable": True, "wind_speed_mps": 5.5, "_base_wind_decimal": True})
    change = _taf_wind_block({"wind_dir_deg": 90, "wind_speed_mps": 5.5, "wind_gust_mps": 7.5})
    assert '<iwxxm:meanWindSpeed uom="m/s">5.5</iwxxm:meanWindSpeed>' in base
    assert "meanWindDirection" not in base
    assert '<iwxxm:meanWindDirection uom="deg">90</iwxxm:meanWindDirection>' in change
    assert '<iwxxm:meanWindSpeed uom="m/s">5.5</iwxxm:meanWindSpeed>' in change
    assert '<iwxxm:windGustSpeed uom="m/s">7.5</iwxxm:windGustSpeed>' in change
