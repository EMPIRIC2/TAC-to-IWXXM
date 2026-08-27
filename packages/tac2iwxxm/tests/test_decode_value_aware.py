"""TC-F9-001 - value-aware decode explanations (S013 / EV-009, F9).

Explanations must carry parsed values (wind direction/speed/gusts, temps,
visibility, pressure, times, change groups) - not only group labels - while
segment ``start``/``end`` offsets stay identical to pre-F9 behavior (additive
contract; ADR-025).
"""

from __future__ import annotations

import itertools

from tac2iwxxm.decode import decode_tac

METAR_GOLDEN = "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011="


def _explanation_for(tac: str, product: str, code: str) -> str:
    result = decode_tac(tac, product=product)
    for seg in result.segments:
        if seg.code == code:
            return seg.explanation
    raise AssertionError(f"no segment for {code!r} in {product} decode of {tac!r}")


# --- TC-F9-001 §1 - METAR golden fixture values ---


def test_metar_wind_direction_and_speed() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "18004KT")
    assert "180°" in text
    assert "4 kt" in text


def test_metar_temperature_and_dewpoint() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "24/18")
    assert "24 °C" in text
    assert "dewpoint 18 °C" in text


def test_metar_altimeter_inhg() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "A3011")
    assert "30.11 inHg" in text


def test_metar_observation_time() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "121251Z")
    assert "day 12" in text
    assert "12:51 UTC" in text


def test_metar_visibility_statute_miles() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "10SM")
    assert "10 statute mile" in text


def test_metar_cloud_amount_and_height() -> None:
    text = _explanation_for(METAR_GOLDEN, "METAR", "FEW250")
    assert "few" in text.lower()
    assert "25,000 ft" in text


# --- TC-F9-001 §2 - negative temps, gusts, VRB, QNH, metre visibility ---


def test_negative_temperature_and_dewpoint() -> None:
    tac = "METAR KJFK 121251Z 18004KT 10SM M05/M12 A3011="
    text = _explanation_for(tac, "METAR", "M05/M12")
    assert "-5 °C" in text
    assert "dewpoint -12 °C" in text


def test_wind_with_gusts() -> None:
    tac = "SPECI KJFK 232045Z 24012G22KT 8SM BKN020 12/06 A3001="
    text = _explanation_for(tac, "SPECI", "24012G22KT")
    assert "240°" in text
    assert "12 kt" in text
    assert "gust" in text.lower()
    assert "22 kt" in text


def test_variable_wind() -> None:
    tac = "METAR KJFK 121251Z VRB03KT 10SM 24/18 A3011="
    text = _explanation_for(tac, "METAR", "VRB03KT")
    assert "variable" in text.lower()
    assert "3 kt" in text


def test_qnh_hectopascals() -> None:
    tac = "METAR LFPG 231751Z 18012KT 2000 RA BKN012 15/07 Q1013="
    text = _explanation_for(tac, "METAR", "Q1013")
    assert "1013 hPa" in text


def test_metre_visibility() -> None:
    tac = "METAR LFPG 231751Z 18012KT 4000 RA BKN012 15/07 Q1013="
    text = _explanation_for(tac, "METAR", "4000")
    assert "4000 m" in text


def test_weather_group_value_aware() -> None:
    tac = "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001="
    text = _explanation_for(tac, "SPECI", "-SN")
    assert "light" in text.lower()
    assert "snow" in text.lower()


# --- TC-F9-001 §3 - TAF change groups carry parsed period/values ---


def test_taf_fm_group_parsed_time() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT P6SM FM161200 18010KT 9999 BKN020="
    text = _explanation_for(tac, "TAF", "FM161200")
    assert "day 16" in text
    assert "12:00 UTC" in text


def test_taf_validity_period_parsed() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9999 BKN020="
    text = _explanation_for(tac, "TAF", "1600/1618")
    assert "day 16" in text
    assert "00:00 UTC" in text
    assert "18:00 UTC" in text


def test_taf_tempo_and_becmg_wording() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9999 TEMPO 1606/1612 4000 -RA BECMG 1612/1614 BKN010="
    tempo = _explanation_for(tac, "TAF", "TEMPO")
    assert "temporar" in tempo.lower()
    becmg = _explanation_for(tac, "TAF", "BECMG")
    assert "becoming" in becmg.lower() or "gradual" in becmg.lower()


def test_taf_prob_percentage() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9999 PROB30 1606/1612 4000 -RA="
    text = _explanation_for(tac, "TAF", "PROB30")
    assert "30%" in text


# --- TC-F9-001 §4 - SIGMET/AIRMET/VAA/TCA best-effort values; residuals kept ---


def test_sigmet_validity_period_parsed() -> None:
    tac = "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD OBSC TS FCST ="
    text = _explanation_for(tac, "SIGMET", "101200/101600")
    assert "day 10" in text
    assert "12:00 UTC" in text
    assert "16:00 UTC" in text


def test_vaa_tca_best_effort_residuals_unchanged() -> None:
    vaa = "VA ADVISORY DTG: 20260716/0100Z VAAC: TOKYO VOLCANO: ASAMA"
    result = decode_tac(vaa, product="VAA")
    assert result.segments or result.residuals
    # Residual spans still reconstruct the source text exactly.
    for res in result.residuals:
        assert vaa[res.start : res.end] == res.text


# --- TC-F9-001 §5 - offsets unchanged (additive contract) ---


def test_segment_offsets_slice_back_to_code() -> None:
    result = decode_tac(METAR_GOLDEN, product="METAR")
    for seg in result.segments:
        assert METAR_GOLDEN[seg.start : seg.end] == seg.code
    # Segments stay ordered and non-overlapping (editor span contract).
    spans = [(seg.start, seg.end) for seg in result.segments]
    assert spans == sorted(spans)
    for (_, prev_end), (nxt_start, _) in itertools.pairwise(spans):
        assert nxt_start >= prev_end


def test_golden_metar_segment_codes_unchanged() -> None:
    """The set of explained tokens must not shrink relative to pre-F9 decode."""
    result = decode_tac(METAR_GOLDEN, product="METAR")
    codes = {seg.code for seg in result.segments}
    assert {
        "METAR",
        "KJFK",
        "121251Z",
        "18004KT",
        "10SM",
        "FEW250",
        "24/18",
        "A3011",
    } <= codes
