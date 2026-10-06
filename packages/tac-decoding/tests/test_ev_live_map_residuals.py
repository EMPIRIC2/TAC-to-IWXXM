"""Regression coverage for residual families still on the live map."""

from __future__ import annotations

from tac_decoding.decode import (
    _canadian_clouds,
    _coord_token,
    _in_convective_area,
    _navaid_chain,
    _precip_amount,
    _pressure_tendency,
    _whole_miles,
    _wx_began_or_ended,
    decode_tac,
)


def _codes(tac: str, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def test_pressure_tendency_group() -> None:
    codes = _codes("METAR CWNH 052300Z RMK 53002", "METAR")
    assert codes["53002"] == ("Pressure tendency: decreasing or steady, then increasing, change 0.2 hPa in 3 hours")
    assert _pressure_tendency("99999") is None


def test_precipitation_amount_and_not_available() -> None:
    codes = _codes("SPECI KAUG 051512Z RMK P0000 P0001 PNO SLPNO", "SPECI")
    assert codes["P0000"] == "Precipitation trace in the past hour"
    assert codes["P0001"] == "Precipitation 0.01 inches in the past hour"
    assert codes["PNO"] == "Precipitation amount not available"
    assert codes["SLPNO"] == "Sea-level pressure not available"
    assert _precip_amount("P12") is None


def test_distant_weather_and_cumulonimbus() -> None:
    codes = _codes("METAR KBIL 052253Z RMK DSNT S-W CB", "METAR")
    assert codes["DSNT"] == "Distant"
    assert codes["S-W"] == "From South to West"
    assert codes["CB"] == "Cloud type (cumulonimbus)"
    prose = _codes("SPECI CYQB 051933Z RMK DIST CB", "SPECI")
    assert prose["DIST"] == "Distant"


def test_canadian_remark_clouds() -> None:
    codes = _codes("METAR CYQQ 052300Z RMK ST3CU1CI1 SF8 AC", "METAR")
    assert codes["ST3CU1CI1"] == "Clouds: stratus 3 oktas, cumulus 1 okta, cirrus 1 okta"
    assert codes["SF8"] == "Clouds: stratus fractus 8 oktas"
    assert codes["AC"] == "Cloud type (altocumulus)"
    assert _canadian_clouds("ZZZ") is None


def test_density_altitude() -> None:
    codes = _codes("METAR CYCG 052300Z RMK DENSITY ALT 2700FT", "METAR")
    assert codes["DENSITY"] == "Density"
    assert codes["ALT"] == "Altitude"
    assert codes["2700FT"] == "Density altitude 2700 ft"
    negative = _codes("METAR CYBG 052300Z RMK DENSITY ALT -12FT", "METAR")
    assert negative["-12FT"] == "Density altitude -12 ft"
    cleared = _codes("METAR CYBG 052300Z RMK DENSITY ALT SLP040", "METAR")
    assert cleared["SLP040"] == "Sea-level pressure (FMH-1 SLP code)"
    assert "ALT" not in _codes("METAR CYCG 052300Z RMK ALT", "METAR")


def test_correction_and_delayed_report() -> None:
    speci = _codes("SPECI CYQT 051112Z CCA 28005KT", "SPECI")
    assert speci["CCA"] == "Correction (CCA)"
    assert _codes("METAR KJFK 052300Z RRA", "METAR")["RRA"] == "Delayed report (RRA)"
    assert _codes("YUDD SIGMET 2 VALID 101200/101600 YUSO- CCA=", "SIGMET")["CCA"] == "Correction (CCA)"
    assert _codes("YUDD SIGMET 2 VALID 101200/101600 YUSO- UNTIL 1600Z=", "SIGMET")["UNTIL"] == "Until"
    delayed = _codes(
        "WSCA31 TTPP 051430 RRA\nTTZP SIGMET 4 VALID 051430/051830 TTPP-",
        "SIGMET",
    )
    assert delayed["RRA"] == "Delayed report (RRA)"


def test_observed_and_forecast_token() -> None:
    codes = _codes(
        "OIIX SIGMET 10 VALID 042002/042330 OIII- OIIX TEHRAN FIR EMBD TS OBS/FCST WI N3459 E04528=",
        "SIGMET",
    )
    assert codes["OBS/FCST"] == "Observed and forecast"


def test_short_fir_names() -> None:
    la_paz = _codes(
        "SLLP SIGMET A2 VALID 051300/051600 SLLP- SLLF LA PAZ FIR EMBD TS=",
        "SIGMET",
    )
    assert la_paz["LA"] == "FIR name (LA)"
    assert la_paz["PAZ"] == "FIR name (PAZ)"
    new_york = _codes(
        "KZWY SIGMET BRAVO 3 VALID 051310/051710 KKCI- NEW YORK OCEANIC FIR EMBD TS=",
        "SIGMET",
    )
    assert new_york["NEW"] == "FIR name (NEW)"
    assert new_york["YORK"] == "FIR name (YORK)"
    sal = _codes(
        "GVSC SIGMET 1 VALID 051703/052103 GVAC- GVSC SAL OCEANIC FIR/UIR EMBD TS=",
        "SIGMET",
    )
    assert sal["SAL"] == "FIR name (SAL)"


def test_convective_states_lakes_and_reference() -> None:
    codes = _codes(
        "WSUS32 KKCI 051455\n"
        "MKCC WST 051455\n"
        "CONVECTIVE SIGMET 32C\n"
        "VALID UNTIL 1655Z\n"
        "LA TX NC AND CSTL WTRS\n"
        "FROM 30SE LCH-30SW LEV\n"
        "AREA TS MOV LTL. NC.\n"
        "REF INTL SIGMET FOXTROT SERIES.",
        "AIRMET",
    )
    assert codes["LA"] == "State (Louisiana)"
    assert codes["TX"] == "State (Texas)"
    assert codes["NC"] == "State (North Carolina)"
    assert codes["NC."] == "No change"
    assert codes["REF"] == "Reference"
    assert codes["INTL"] == "International"
    assert codes["SIGMET"] == "Referenced report (SIGMET)"
    assert codes["FOXTROT"] == "Referenced SIGMET series (Foxtrot)"
    assert codes["SERIES."] == "Series"
    lakes = _codes(
        "WSUS31 KKCI 051455\nCONVECTIVE SIGMET 27E\nVALID UNTIL 1655Z\nNY LO\nFROM MSS=",
        "SIGMET",
    )
    assert lakes["NY"] == "State (New York)"
    assert lakes["LO"] == "Lake (Ontario)"
    assert not _in_convective_area({})
    assert not _in_convective_area({"convective": 1})
    assert not _in_convective_area({"convective": 1, "until": 1, "from_line": 1})
    assert not _in_convective_area({"convective": 1, "until": 1, "area": 1})
    assert not _in_convective_area({"convective": 1, "until": 1, "tops": 1})
    repeat = _codes("YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD FIR SIGMET=", "SIGMET")
    assert repeat["SIGMET"] == "Report type (SIGMET)"


def test_navaid_segment_without_a_distance() -> None:
    codes = _codes(
        "WSUS31 KKCI 051455\nCONVECTIVE SIGMET 26E\nVALID UNTIL 1655Z\nFL\nFROM TRV-PBI CEW-TLH TRV-TRV\nAREA TS=",
        "SIGMET",
    )
    assert codes["FL"] == "State (Florida)"
    assert codes["TRV-PBI"] == "Navaids TRV to PBI"
    assert codes["CEW-TLH"] == "Navaids CEW to TLH"
    assert codes["TRV-TRV"] == "Navaids TRV to TRV"
    assert _navaid_chain("TRV") is None
    assert _navaid_chain("TRV-") is None
    assert _navaid_chain("TRV-40W") is None


def test_whole_miles_before_a_fraction() -> None:
    codes = _codes("SPECI CYBR 051151Z 1 3/4SM", "SPECI")
    assert codes["1"] == "Visibility 1 statute mile, plus the following fraction"
    assert codes["3/4SM"] == "Prevailing visibility 3/4 statute mile"
    remark = _codes("METAR CYQQ 052300Z RMK VIS 1/2 SM NE", "METAR")
    assert remark["1/2"] == "Visibility 1/2 statute mile"
    assert remark["SM"] == "Statute miles"
    assert remark["NE"] == "Northeast"
    lone = _codes("METAR KJFK 052300Z 9", "METAR")
    assert "9" not in lone
    assert _whole_miles("10SM", "") is None
    assert _whole_miles("1", "10SM") is None


def test_peak_wind_and_past_hour() -> None:
    codes = _codes("METAR CWDQ 052300Z RMK PK WND 28019/2200 2PAST HR", "METAR")
    assert codes["28019/2200"] == "Peak wind 280° at 19 kt at 22:00 UTC"
    assert codes["2PAST"] == "In the past 2 hours"
    assert codes["HR"] == "Hour"
    one = _codes("METAR CWDQ 052300Z RMK 1PAST", "METAR")
    assert one["1PAST"] == "In the past 1 hour"


def test_canadian_remark_prose() -> None:
    codes = _codes(
        "METAR CYBG 052300Z RMK PCPN VRY LGT DIST SH ALQDS FG BANK QUAD CVCTV CLD EMBD LWR DNWND LO TOPS ACSL TR",
        "METAR",
    )
    assert codes["PCPN"] == "Precipitation"
    assert codes["VRY"] == "Very"
    assert codes["LGT"] == "Light"
    assert codes["ALQDS"] == "All quadrants"
    assert codes["SH"] == "Showers"
    assert codes["FG"] == "Weather: Fog"
    assert codes["CVCTV"] == "Convective"
    assert codes["CLD"] == "Cloud"
    assert codes["EMBD"] == "Embedded"
    assert codes["LWR"] == "Lower"
    assert codes["DNWND"] == "Downwind"
    assert codes["LO"] == "Low"
    assert codes["TOPS"] == "Tops"
    assert codes["ACSL"] == "Altocumulus standing lenticular"
    assert codes["TR"] == "Trace"


def test_longitude_glued_to_a_hyphen() -> None:
    codes = _codes(
        "VCCF SIGMET B01 VALID 050915/051245 VCBI- VCCF COLOMBO FIR EMBD TS OBS WI N0750 E08046-=",
        "SIGMET",
    )
    assert "80°46'" in codes["E08046-"]
    assert _coord_token("N54") == "N54"
    assert _coord_token("50WSW-") == "50WSW-"
    assert _coord_token("E08046-") == "E08046"


def test_surface_to_feet_and_radius() -> None:
    codes = _codes(
        "YMMM SIGMET N04 VALID 052200/060200 YMRF- YMMM MELBOURNE FIR SEV TURB FCST WI S4040 E14520 "
        "SFC/6000FT STNR NC=",
        "SIGMET",
    )
    assert codes["SFC/6000FT"] == "Surface to 6000 ft"
    radius = _codes(
        "KZAK SIGMET OSCAR 50 VALID 050740/051340 PHFO- OAKLAND OCEANIC FIR TC NOLO WI 200NM OF CENTER=",
        "SIGMET",
    )
    assert radius["200NM"] == "Within 200 nautical miles"
    assert radius["NOLO"] == "Tropical cyclone (NOLO)"
    assert radius["CENTER"] == "Center"
    metres = _codes("YMMM SIGMET 1 VALID 052200/060200 YMRF- YMMM FIR SFC/6000M=", "SIGMET")
    assert metres["SFC/6000M"] == "Surface to 6000 m"
    named = _codes(
        "RJJJ SIGMET F04 VALID 051909/060109 RJTD- RJJJ FUKUOKA FIR TC CHOI-WAN OBS=",
        "SIGMET",
    )
    assert named["CHOI-WAN"] == "Tropical cyclone (CHOI-WAN)"
    observed = _codes("RJJJ SIGMET 1 VALID 051909/060109 RJTD- RJJJ FIR TC OBS=", "SIGMET")
    assert observed["OBS"] == "Observed"


def test_runway_range_vertical_visibility_and_weather_times() -> None:
    codes = _codes(
        "METAR EIKN 051830Z 1100 R08///// R35R/2600V3000FT R32/2600VP6000FT "
        "R12/M0500V1500 VV002 VV/// //////CB //// RMK RAB19 RAE19 0.8MM PAST "
        "PRESRR PRESFR PWINO ASOCTD CONTRAILS VIRGA LTNG MOD MOV ICE TSB33",
        "METAR",
    )
    assert codes["R08/////"] == "Runway visual range runway 08: not reported"
    assert codes["R35R/2600V3000FT"] == ("Runway visual range runway 35R: varying from 2600 ft to 3000 ft")
    assert "more than 6000 ft" in codes["R32/2600VP6000FT"]
    assert codes["R12/M0500V1500"] == ("Runway visual range runway 12: varying from less than 500 m to 1500 m")
    assert codes["VV002"] == "Vertical visibility 200 ft"
    assert codes["VV///"] == "Vertical visibility not reported"
    assert codes["//////CB"] == "Cloud amount not reported, cumulonimbus"
    assert codes["////"] == "Cloud amount not reported"
    assert codes["RAB19"] == "Rain began at 19 minutes past the hour"
    assert codes["RAE19"] == "Rain ended at 19 minutes past the hour"
    assert codes["TSB33"] == "Thunderstorm began at 33 minutes past the hour"
    assert codes["0.8MM"] == "Precipitation 0.8 mm"
    assert codes["PAST"] == "Past"
    assert codes["PRESRR"] == "Pressure rising rapidly"
    assert codes["PRESFR"] == "Pressure falling rapidly"
    assert codes["PWINO"] == "Present weather not available"
    assert codes["ASOCTD"] == "Associated"
    assert codes["CONTRAILS"] == "Contrails"
    assert codes["VIRGA"] == "Virga"
    assert codes["LTNG"] == "Lightning"
    assert codes["MOD"] == "Moderate"
    assert codes["MOV"] == "Moving"
    assert codes["ICE"] == "Ice"
    chained = _codes(
        "SPECI KBIX 052123Z RMK RAE2055DZB08E10RAB10E23 CIG 014V021 LTG AND",
        "SPECI",
    )
    assert chained["RAE2055DZB08E10RAB10E23"] == (
        "Rain ended at 20:55. "
        "Drizzle began at 08 minutes past the hour and ended at 10 minutes past the hour. "
        "Rain began at 10 minutes past the hour and ended at 23 minutes past the hour"
    )
    assert chained["CIG"] == "Ceiling"
    assert chained["014V021"] == "Ceiling varying from 1400 ft to 2100 ft"
    assert chained["LTG"] == "Lightning"
    assert chained["AND"] == "And"
    began = _codes("SPECI KBML 051323Z RMK RAB1253E06", "SPECI")
    assert began["RAB1253E06"] == "Rain began at 12:53 and ended at 06 minutes past the hour"
    assert _codes("METAR KJFK 052300Z RMK CIG SLP040", "METAR")["SLP040"].startswith("Sea-level")
    assert _wx_began_or_ended("RAB1253") == "Rain began at 12:53"
    assert _wx_began_or_ended("RA") is None
    assert _wx_began_or_ended("RAB1") is None
    assert _wx_began_or_ended("RAB1234X") is None
    miles = _codes("SPECI CYBR 051151Z RMK VIS NW 2 1/2", "SPECI")
    assert miles["2"] == "Visibility 2 statute mile, plus the following fraction"
    assert miles["1/2"] == "Visibility 1/2 statute mile"
