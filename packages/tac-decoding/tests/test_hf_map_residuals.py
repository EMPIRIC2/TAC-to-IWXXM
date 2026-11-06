"""Groups that showed up as residuals on the live map."""

from __future__ import annotations

from tac_decoding.decode import (
    _boundary_points,
    _explain_sigmet_airmet,
    _lat_lon_phrase,
    _tenths_c,
    decode_tac,
)

_CONVECTIVE = """WSUS31 KKCI 051455
MKCE WST 051455
CONVECTIVE SIGMET 27E
VALID UNTIL 1655Z
NY LO
FROM 50WSW MSS-30S MSS-60ENE SYR
AREA EMBD TS MOV FROM 26030KT. TOPS TO FL450.
CSTL WTRS MOV LTL."""

_OCEANIC = """WSNT12 KKCI 042305
KZMA KZHU SIGMET LIMA 4 VALID 042305/050305 KKCI-
MIAMI OCEANIC FIR HOUSTON OCEANIC FIR FRQ TS OBS AT 2305Z WI
N2831 W08804 - N2722 W08416 - N2606 W08444 - N2715 W08853 - N2831
W08804. TOP FL470. MOV E 15KT. NC."""


def test_metar_and_speci_remarks_from_the_map_are_explained() -> None:
    metar = decode_tac(
        "METAR CWNH 052300Z AUTO 24006KT 060V190 9SM OVC039/// 09/03 A2992 RMK T00861033 $",
        product="METAR",
    )
    speci = decode_tac(
        "SPECI CYBR 051151Z AUTO 09006KT 3/4SM TS WSHFT",
        product="SPECI",
    )
    metar_codes = {segment.code: segment.explanation for segment in metar.segments}
    speci_codes = {segment.code: segment.explanation for segment in speci.segments}
    assert metar_codes["AUTO"] == "Automated report"
    assert metar_codes["060V190"] == "Wind direction varying from 60° to 190°"
    assert "8.6" in metar_codes["T00861033"]
    assert "-3.3" in metar_codes["T00861033"]
    assert "type not reported" in metar_codes["OVC039///"]
    assert metar_codes["$"] == "Station needs maintenance"
    assert speci_codes["3/4SM"] == "Prevailing visibility 3/4 statute mile"
    assert speci_codes["TS"] == "Thunderstorm"
    assert speci_codes["WSHFT"] == "Wind shift"
    missing = decode_tac("METAR KJFK 052300Z // ///", product="METAR")
    missing_codes = {segment.code: segment.explanation for segment in missing.segments}
    assert missing_codes["//"] == "Missing data"
    assert missing_codes["///"] == "Missing data"
    assert _tenths_c("1100") == "-10.0"


def test_convective_sigmet_text_is_explained_even_as_an_airmet() -> None:
    result = decode_tac(_CONVECTIVE, product="AIRMET")
    by_code = {segment.code: segment.explanation for segment in result.segments}
    residual = " ".join(item.text for item in result.residuals)
    assert by_code["CONVECTIVE"] == "Convective"
    assert by_code["SIGMET"] == "Report type (SIGMET)"
    assert by_code["27E"] == "Sequence number (27E)"
    assert by_code["WST"] == "Convective SIGMET bulletin"
    assert by_code["051455"] == "Issue time day 5 14:55 UTC"
    assert by_code["UNTIL"] == "Until"
    assert by_code["50WSW"] == "Boundary 50 nm West-southwest"
    assert by_code["MSS-30S"] == "Boundary MSS to 30 nm South"
    assert by_code["26030KT."] == "Moving from 260° at 30 kt"
    assert by_code["TOPS"] == "Cloud tops"
    assert by_code["TO"] == "To"
    assert by_code["FL450."] == "Flight level 450"
    assert by_code["LTL."] == "Little"
    assert by_code["CSTL"] == "Coastal"
    assert by_code["WTRS"] == "Waters"
    assert "UNTIL" not in residual.split()
    assert "27E" not in residual.split()


def test_oceanic_sigmet_series_periods_and_second_fir_name() -> None:
    result = decode_tac(_OCEANIC, product="SIGMET")
    by_code = {segment.code: segment.explanation for segment in result.segments}
    assert by_code["LIMA"] == "SIGMET series (Lima)"
    assert by_code["4"] == "Sequence number (4)"
    assert by_code["MIAMI"] == "FIR name (MIAMI)"
    assert by_code["HOUSTON"] == "FIR name (HOUSTON)"
    assert by_code["W08804."] == "Longitude 88°04' W"
    assert by_code["FL470."] == "Flight level 470"
    assert by_code["15KT."] == "Speed 15 kt"
    assert by_code["NC."] == "No change"
    kinabalu = decode_tac(
        "WBFC SIGMET 6 VALID 050916/051130 WBKK- WBFC KOTA KINABALU FIR EMBD TS=",
        product="SIGMET",
    )
    names = {segment.code: segment.explanation for segment in kinabalu.segments}
    assert names["KOTA"] == "FIR name (KOTA)"
    assert names["KINABALU"] == "FIR name (KINABALU)"
    lima = decode_tac(
        "SPIM SIGMET A9 VALID 052132/052350 SPJC- SPIM LIMA FIR EMBD TS=",
        product="SIGMET",
    )
    lima_codes = {segment.code: segment.explanation for segment in lima.segments}
    assert lima_codes["A9"] == "Sequence number (A9)"
    assert lima_codes["LIMA"] == "FIR name (LIMA)"
    glued = decode_tac(
        "SPIM SIGMET 2 VALID 052132/052350 SPJC- SPIM LIMA FIR WI N1346W09652=",
        product="SIGMET",
    )
    glued_codes = {segment.code: segment.explanation for segment in glued.segments}
    assert "13°46'" in glued_codes["N1346W09652"]
    assert "96°52'" in glued_codes["N1346W09652"]


def test_boundary_and_coordinate_helpers_reject_incomplete_groups() -> None:
    assert _boundary_points("50WSW-") is None
    assert _boundary_points("50XYZ") is None
    assert _boundary_points("MSS") is None
    assert _boundary_points("50WSWMSS") == "Boundary 50 nm West-southwest of MSS"
    leftover = decode_tac(
        "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD FIR FROM ABCD WI N54=",
        product="SIGMET",
    )
    leftover_codes = {segment.code: segment.explanation for segment in leftover.segments}
    assert leftover_codes["FROM"] == "From"
    assert _lat_lon_phrase("ZZ", "YY") is None
    assert _lat_lon_phrase("N54", "W012") == "Latitude 54°00' N, longitude 12°00' W"
    assert _explain_sigmet_airmet("TO", product="SIGMET", seen={}) is None
    assert _explain_sigmet_airmet("FROM", product="SIGMET", seen={}) == "Originating FIR / location indicator (FROM)"
