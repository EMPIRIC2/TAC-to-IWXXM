"""International SIGMET forms: freezing rain, line geometry, and speed units."""

from __future__ import annotations

from tac_decoding.decode import _explain_sigmet_airmet, decode_tac

_TYUMEN = (
    "USTV SIGMET 2 VALID 051330/051730 USTR-\n"
    "USTV TYUMEN FIR SEV ICE (FZRA) FCST E OF LINE N6310 E08435 - N6321 E07730 "
    "SFC/FL100 MOV NE 20KMH NC="
)


def test_tyumen_sigmet_explains_freezing_rain_line_and_kilometres() -> None:
    result = decode_tac(_TYUMEN, product="SIGMET")
    by_code = {segment.code: segment.explanation for segment in result.segments}
    residual = " ".join(item.text for item in result.residuals)
    assert by_code["(FZRA)"] == "Freezing rain"
    assert by_code["LINE"] == "Line of coordinates"
    assert by_code["-"] == "Line vertex separator"
    assert by_code["20KMH"] == "Speed 20 kilometres per hour"
    assert "(FZRA)" not in residual
    assert "LINE" not in residual.split()
    assert "20KMH" not in residual


def test_spaced_speed_and_sixteen_point_direction() -> None:
    tac = "USTV SIGMET 3 VALID 051330/051730 USTR- USTV TYUMEN FIR SEV TURB FCST SFC/FL100 MOV NNE 20 KMH NC="
    result = decode_tac(tac, product="SIGMET")
    by_code = {segment.code: segment.explanation for segment in result.segments}
    assert by_code["NNE"] == "Movement direction (North-northeast)"
    assert by_code["20"] == "Speed 20"
    assert by_code["KMH"] == "kilometres per hour"


def test_slash_kilometres_per_hour() -> None:
    glued = decode_tac(
        "USTV SIGMET 4 VALID 051330/051730 USTR- USTV TYUMEN FIR SEV TURB FCST SFC/FL100 MOV E 25KM/H NC=",
        product="SIGMET",
    )
    by_code = {segment.code: segment.explanation for segment in glued.segments}
    assert by_code["25KM/H"] == "Speed 25 kilometres per hour"
    spaced = decode_tac(
        "USTV SIGMET 5 VALID 051330/051730 USTR- USTV TYUMEN FIR SEV TURB FCST SFC/FL100 MOV E 25 KM/H NC=",
        product="SIGMET",
    )
    spaced_codes = {segment.code: segment.explanation for segment in spaced.segments}
    assert spaced_codes["KM/H"] == "kilometres per hour"


def test_metres_per_second_and_polygon_dash_without_a_line() -> None:
    assert _explain_sigmet_airmet("15MPS", product="SIGMET", seen={}) == "Speed 15 metres per second"
    assert _explain_sigmet_airmet("-", product="SIGMET", seen={}) == "Polygon vertex separator"
    assert _explain_sigmet_airmet("\u2013", product="SIGMET", seen={"line": 1}) == "Line vertex separator"
    assert _explain_sigmet_airmet("ESE", product="SIGMET", seen={}) == "East-southeast"
    seen = {"mov": 1}
    assert _explain_sigmet_airmet("NNW", product="SIGMET", seen=seen) == "Movement direction (North-northwest)"
    assert seen["mov_dir"] == 1
