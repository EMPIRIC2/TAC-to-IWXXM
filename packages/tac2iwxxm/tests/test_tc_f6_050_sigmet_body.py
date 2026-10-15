"""TC-F6-052: SIGMET body normalizer for wrapped coordinates and cancellations.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.decode import decode_tac
from tac2iwxxm.slot_builders.sigmet_airmet import parse_sigmet
from tac2iwxxm.slot_builders.sigmet_body import (
    compound_movement_degrees,
    direction_midpoint,
    flight_information_region_name,
    is_latitude_token,
    is_longitude_token,
    unwrap_wrapped_coordinates,
    use_volcanic_ash_locations,
    without_cancellation_remark,
)

from tac2iwxxm import convert

GUYANA = """WSGY31 SYCJ 081650
SYGC SIGMET A1 VALID 081450/081850 SYCJ -
SYGC GEORGETOWN FIR ISOL EMBD TS OBS AT 1450Z WI N0829 W05925 -
N0641 W05820 - N0601 W05908 - N0756 W06012 -  N0829 W05925 TOP FL500
MOV W-NW INTSF="""

CANCELLATION = """WCCA31 TTPP 141815

TTZP SIGMET A4 VALID 141815/142145 TTPP-
TTZP PIARCO FIR CNL SIGMET A3 VALID
141545/142145 RMK: TC LORENZO MOV TO KZWY FIR="""

SIMPLE = (
    "TTZP SIGMET 1 VALID 261150/261550 TTPP- "
    "TTZP PIARCO FIR EMBD TS OBS AT 1145Z WI N1800 W05839 - N1800 W05450 - "
    "N1635 W05450 - N1635 W05839 - N1800 W05839 TOP ABV FL310 MOV NW 15KT WKN="
)

BARE_CANCELLATION = "TTZP SIGMET A4 VALID 141815/142145 TTPP- TTZP PIARCO FIR CNL SIGMET A3 141545/142145="


def test_cancellation_with_remark_converts_as_cancellation() -> None:
    ir = parse_sigmet(CANCELLATION, product="SIGMET")
    assert ir["sequence"] == 4
    assert ir["sequence_label"] == "A4"
    assert ir["cancel"] is True
    assert ir["cancelled_sequence"] == 3
    assert ir["cancelled_sequence_label"] == "A3"
    assert ir.get("phenomenon") is None
    assert "tropical_cyclone_name" not in ir
    assert ir["fir_name"] == "PIARCO FIR"
    result = convert(CANCELLATION, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert result.xml is not None
    assert 'isCancelReport="true"' in result.xml
    assert "cancelledReportSequenceNumber>3<" in result.xml
    assert "LORENZO" not in result.xml
    assert "RMK" not in result.xml
    assert "<aixm:type>FIC</aixm:type>" in result.xml
    assert "aerodrome" not in result.xml.lower()


def test_guyana_wrapped_coordinates_convert() -> None:
    ir = parse_sigmet(GUYANA, product="SIGMET")
    assert ir["sequence"] == 1
    assert ir["sequence_label"] == "A1"
    geometry = ir["geometry"]
    assert geometry["kind"] == "polygon"
    pos_list = geometry["pos_list"]
    for vertex in ("8.4833 -59.4167", "6.6833 -58.3333", "6.0167 -59.1333", "7.9333 -60.2000"):
        assert vertex in pos_list
    result = convert(GUYANA, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert result.xml is not None
    assert "8.4833 -59.4167" in result.xml
    assert "6.6833 -58.3333" in result.xml


def test_compound_west_northwest_movement_is_represented() -> None:
    ir = parse_sigmet(GUYANA, product="SIGMET")
    assert ir["motion_dir_deg"] == 292.5
    assert ir["intensity_change"] == "INTENSIFY"
    result = convert(GUYANA, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.xml is not None
    assert 'directionOfMotion uom="deg">292.5</iwxxm:directionOfMotion>' in result.xml


def test_fir_name_is_kept_and_not_an_unexplained_residual() -> None:
    ir = parse_sigmet(GUYANA, product="SIGMET")
    assert ir["fir"] == "SYGC"
    assert ir["mwo"] == "SYCJ"
    assert ir["fir_name"] == "GEORGETOWN FIR"
    result = convert(GUYANA, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.xml is not None
    assert "<aixm:name>GEORGETOWN FIR</aixm:name>" in result.xml
    assert "<aixm:designator>SYGC</aixm:designator>" in result.xml
    assert "<aixm:type>FIC</aixm:type>" in result.xml
    assert "aerodrome" not in result.xml.lower()
    decoded = decode_tac(GUYANA, product="SIGMET")
    residual_text = " ".join(item.text for item in decoded.residuals)
    assert "GEORGETOWN" not in residual_text
    assert "FIR" not in residual_text


def test_simple_sample_still_keeps_tops_movement_and_intensity() -> None:
    ir = parse_sigmet(SIMPLE, product="SIGMET")
    assert ir["top_fl"] == 310
    assert ir["top_qualifier"] == "ABV"
    assert ir["motion_dir_deg"] == 315
    assert ir["motion_speed_kt"] == 15
    assert ir["intensity_change"] == "WEAKEN"
    assert "locations" not in ir
    bare = parse_sigmet(BARE_CANCELLATION, product="SIGMET")
    assert bare["cancel"] is True
    assert bare.get("phenomenon") is None


def test_direction_midpoint_uses_the_shorter_arc() -> None:
    assert direction_midpoint(270.0, 315.0) == 292.5
    assert direction_midpoint(315.0, 270.0) == 292.5
    assert direction_midpoint(0.0, 180.0) == 90.0
    assert direction_midpoint(180.0, 0.0) == 270.0
    assert direction_midpoint(0.0, 270.0) == 315.0
    assert direction_midpoint(10.0, 350.0) == 0.0
    assert direction_midpoint(350.0, 10.0) == 0.0
    assert compound_movement_degrees("MOV W-NW INTSF") == 292.5
    assert compound_movement_degrees("MOV W - NW") == 292.5
    assert compound_movement_degrees("MOV NW-W") == 292.5
    assert compound_movement_degrees("MOV NW 15KT") is None
    assert compound_movement_degrees("MOV W-XX") is None
    assert compound_movement_degrees("STNR") is None


def test_volcanic_ash_locations_stay_limited_to_ash() -> None:
    assert use_volcanic_ash_locations("VA", "EMBD TS") is True
    assert use_volcanic_ash_locations("va", "EMBD TS") is True
    assert use_volcanic_ash_locations("EMBD_TS", "VA CLD OBS") is True
    assert use_volcanic_ash_locations("EMBD_TS", "VA ERUPTION MT ASH") is True
    assert use_volcanic_ash_locations("EMBD_TS", "EMBD TS OBS AT 1200Z") is False
    assert use_volcanic_ash_locations("TS", "VALID 141545/142145") is False


def test_cancellation_remark_is_ignored_only_on_a_cancellation() -> None:
    assert without_cancellation_remark("PIARCO FIR CNL SIGMET A3 VALID 141545/142145 RMK: TC LORENZO") == (
        "PIARCO FIR CNL SIGMET A3 VALID 141545/142145"
    )
    assert without_cancellation_remark("FIR CNL AIRMET 2 010000/010400 RMK ICE") == "FIR CNL AIRMET 2 010000/010400"
    assert without_cancellation_remark("EMBD TS RMK: KEEP") == "EMBD TS RMK: KEEP"
    assert without_cancellation_remark("CNL SIGMET A3 141545/142145") == "CNL SIGMET A3 141545/142145"
    assert without_cancellation_remark("CNL SIGMET A3 REMARK ONLY") == "CNL SIGMET A3 REMARK ONLY"
    assert without_cancellation_remark("RMK: NOTE CNL SIGMET A3 141545/142145") == ""


def test_flight_information_region_name_keeps_the_name() -> None:
    assert flight_information_region_name("SYGC GEORGETOWN FIR ISOL", "SYGC", "SYCJ") == "GEORGETOWN FIR"
    assert flight_information_region_name("SYCJ GEORGETOWN FIR EMBD", "SYGC", "SYCJ") == "GEORGETOWN FIR"
    assert flight_information_region_name("SOOO CAYENNE FIR/UIR EMBD", "SOOO", "TFFF") == "CAYENNE FIR/UIR"
    assert (
        flight_information_region_name("NEW YORK OCEANIC FIR MIAMI OCEANIC FIR", "KZWY", "KKCI")
        == "NEW YORK OCEANIC FIR"
    )
    assert flight_information_region_name("SLLF LA PAZ FIR EMBD", "SLLF", "") == "LA PAZ FIR"
    assert (
        flight_information_region_name("ALPHA BRAVO CHARLIE DELTA ECHO FIR", "YYYY", "")
        == "BRAVO CHARLIE DELTA ECHO FIR"
    )
    assert flight_information_region_name("A PAZ FIR", "SLLF", "") == "PAZ FIR"
    assert flight_information_region_name("12 GEORGETOWN FIR", "SYGC", "") == "GEORGETOWN FIR"
    assert flight_information_region_name("SYGC FIR EMBD", "SYGC", "SYCJ") == "SYGC"
    assert flight_information_region_name("EMBD TS OBS", "SYGC", "") == "SYGC"
    assert flight_information_region_name("GEORGETOWN FIR", "sygc", "sycj") == "GEORGETOWN FIR"


def test_unwrap_joins_a_split_pair_and_a_hyphen_continuation() -> None:
    assert unwrap_wrapped_coordinates("N2853\nW05650") == "N2853 W05650"
    assert unwrap_wrapped_coordinates("N2853-\nW05650 - N2611 W04611") == "N2853 W05650 - N2611 W04611"
    assert unwrap_wrapped_coordinates("WI N0829 W05925 -\nN0641 W05820 TOP FL500") == (
        "WI N0829 W05925 - N0641 W05820 TOP FL500"
    )
    assert unwrap_wrapped_coordinates("MOV W-NW") == "MOV W-NW"
    assert unwrap_wrapped_coordinates("TOP FL500\nMOV W-NW") == "TOP FL500 MOV W-NW"
    assert unwrap_wrapped_coordinates("\nN0829 W05925") == "N0829 W05925"
    assert unwrap_wrapped_coordinates("-\nTOP FL300") == "- TOP FL300"
    glued = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
        "YUDD SHANLON FIR/UIR EMBD TS OBS AT 1200Z WI N2853-\n"
        "W05650 - N2951 W04604 - N2611 W04611 - N2853 W05650 TOP FL300 MOV N 10KT NC="
    )
    ir = parse_sigmet(glued, product="SIGMET")
    assert "28.8833 -56.8333" in ir["geometry"]["pos_list"]
    assert ir["fir_name"] == "SHANLON FIR/UIR"
    assert ir["top_fl"] == 300
    assert ir["motion_dir_deg"] == 0


def test_coordinate_token_bounds() -> None:
    assert is_latitude_token("") is False
    assert is_latitude_token(".") is False
    assert is_latitude_token("N082") is False
    assert is_latitude_token("N0829") is True
    assert is_latitude_token("N08293") is True
    assert is_latitude_token("N082930") is True
    assert is_latitude_token("n082930") is True
    assert is_latitude_token("S082930") is True
    assert is_latitude_token("N0829301") is False
    assert is_latitude_token("E0829") is False
    assert is_latitude_token("N082A") is False
    assert is_longitude_token("") is False
    assert is_longitude_token("W0592") is False
    assert is_longitude_token("W05925") is True
    assert is_longitude_token("E059251") is True
    assert is_longitude_token("w0592512") is True
    assert is_longitude_token("W0592512") is True
    assert is_longitude_token("W05925123") is False
    assert is_longitude_token("N05925") is False
    assert is_longitude_token("W0592A") is False
    assert unwrap_wrapped_coordinates("S0829-\nE0592512") == "S0829 E0592512"
    assert unwrap_wrapped_coordinates("N0829-\nW05650.") == "N0829 W05650"
    assert unwrap_wrapped_coordinates("N082-\nW05925") == "N082- W05925"
    assert unwrap_wrapped_coordinates("N0829301-\nW05925") == "N0829301- W05925"
    assert unwrap_wrapped_coordinates("N082930-\nW05925") == "N082930 W05925"
    assert unwrap_wrapped_coordinates("E0829-\nW05925") == "E0829- W05925"
    assert unwrap_wrapped_coordinates("N082A-\nW05925") == "N082A- W05925"
    assert unwrap_wrapped_coordinates("N0829-\nW0592") == "N0829- W0592"
    assert unwrap_wrapped_coordinates("N0829-\nW05925") == "N0829 W05925"
    assert unwrap_wrapped_coordinates("N0829-\nW0592512") == "N0829 W0592512"
    assert unwrap_wrapped_coordinates("N0829-\nW05925123") == "N0829- W05925123"
    assert unwrap_wrapped_coordinates("N0829-\nN05925") == "N0829 - N05925"
    assert unwrap_wrapped_coordinates("N0829-\nQ05925") == "N0829- Q05925"
    assert unwrap_wrapped_coordinates("N0829-\nW0592A") == "N0829- W0592A"
    assert unwrap_wrapped_coordinates("WI N2853\nW05650") == "WI N2853 W05650"
    assert unwrap_wrapped_coordinates("WI N2853-\nW05650") == "WI N2853 W05650"
    assert unwrap_wrapped_coordinates("N2853\nW05650 -") == "N2853 W05650 -"
    assert unwrap_wrapped_coordinates("W05925-\nN0641 W05820") == "W05925 - N0641 W05820"
    assert unwrap_wrapped_coordinates("TOP FL500\nN0641") == "TOP FL500 N0641"
    assert unwrap_wrapped_coordinates("TOP FL500\nMOV N") == "TOP FL500 MOV N"
    assert unwrap_wrapped_coordinates("N0829 .\nW05925") == "N0829 . W05925"
    assert unwrap_wrapped_coordinates("N0829\n.") == "N0829 ."
    assert unwrap_wrapped_coordinates("-\nW05925") == "- W05925"
    assert unwrap_wrapped_coordinates("HDR\nN2853-\nW05650\nMOV N") == "HDR N2853 W05650 MOV N"
    assert unwrap_wrapped_coordinates("  MOV W-NW  ") == "MOV W-NW"
    assert unwrap_wrapped_coordinates("") == ""


def test_ash_location_without_a_polygon_is_skipped() -> None:
    tac = (
        "WVXX01 YUSO 101200\n"
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
        "YUDD SHANLON FIR/UIR VA CLD OBS AT 1200Z WI NONE NC="
    )
    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["phenomenon"] == "VA"
    assert "locations" not in ir
