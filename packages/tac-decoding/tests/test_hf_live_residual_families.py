"""Hotfix: explain live residual families (A01, wx remarks, WST ellipsis, …).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.decode import decode_tac


def _codes(tac: str, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _residual_text(tac: str, product: str) -> str:
    return " ".join(item.text for item in decode_tac(tac, product=product).residuals)


def test_ao1_digit_form_and_short_precip() -> None:
    tac = "METAR K18H 031455Z AUTO 15007KT 090V170 CLR 28/23 A2993 RMK A01"
    codes = _codes(tac, "METAR")
    assert "automated" in codes["A01"].lower()
    assert "A01" not in _residual_text(tac, "METAR")
    precip = "METAR KSVE 031455Z AUTO 26003KT 9SM CLR 00/00 A3008 RMK A01 P000"
    codes_p = _codes(precip, "METAR")
    assert "A01" in codes_p
    assert "P000" in codes_p
    assert "P000" not in _residual_text(precip, "METAR")
    assert "automated" in _codes("METAR KMOB 031456Z 08011KT 7SM OVC014 23/19 A3005 RMK A02", "METAR")["A02"].lower()


def test_supplemental_wx_remarks() -> None:
    sfc = "SPECI KCVG 022131Z 16006KT 2 1/2SM -RA BR BKN010 OVC019 14/13 A3018 RMK AO2 SFC VIS 5"
    codes = _codes(sfc, "SPECI")
    assert codes["SFC"] == "Surface"
    assert "visibility" in codes["VIS"].lower() or codes["VIS"] == "Visibility"
    twr = "SPECI KACY 031219Z 00000KT 2 1/2SM BR OVC001 06/06 A3034 RMK AO2 TWR VIS 10"
    assert _codes(twr, "SPECI")["TWR"] == "Tower"
    binovc = "SPECI KATL 031341Z 09013KT 10SM BKN014 BKN027 OVC033 16/13 A3023 RMK AO2 BINOVC"
    assert "break" in _codes(binovc, "SPECI")["BINOVC"].lower()
    ohd = "SPECI PTRO 030440Z 35003KT 8SM -SHRA BKN015TCU BKN120 27/24 A2986 RMK TCU OHD"
    assert "overhead" in _codes(ohd, "SPECI")["OHD"].lower()
    apch = "SPECI WAAA 030624Z 31013KT 5000 -TSRA FEW018CB SCT019 27/24 Q1011 RMK CB IN APCH"
    codes_a = _codes(apch, "SPECI")
    assert codes_a["IN"] == "In"
    assert "approach" in codes_a["APCH"].lower()
    ltg = "METAR KDJT 031453Z 08015G23KT 10SM SCT020 28/24 A3003 RMK AO2 OCNL LTGICCG DSNT SW"
    codes_l = _codes(ltg, "METAR")
    assert "occasional" in codes_l["OCNL"].lower()
    assert "lightning" in codes_l["LTGICCG"].lower()
    for tok in ("SFC", "TWR", "BINOVC", "OHD", "APCH", "OCNL", "LTGICCG"):
        assert tok not in _residual_text(
            sfc
            if tok == "SFC"
            else twr
            if tok == "TWR"
            else binovc
            if tok == "BINOVC"
            else ohd
            if tok == "OHD"
            else apch
            if tok == "APCH"
            else ltg,
            "SPECI" if tok != "LTGICCG" and tok != "OCNL" else "METAR",
        )


def test_layer_icing_and_missing_temp() -> None:
    ice = "METAR KGPI 031355Z AUTO 00000KT 10SM CLR M05/M06 A3025 RMK AO2 I1000 T10501056"
    codes = _codes(ice, "METAR")
    assert "ice" in codes["I1000"].lower()
    assert "I1000" not in _residual_text(ice, "METAR")
    missing = "SPECI YCFS 031011Z AUTO 03009KT 9999 VCTS BKN053 OVC068 22/// Q1009"
    codes_m = _codes(missing, "SPECI")
    assert "22///" in codes_m
    assert "dewpoint" in codes_m["22///"].lower() or "temperature" in codes_m["22///"].lower()
    assert "22///" not in _residual_text(missing, "SPECI")
    fg = "METAR CYQK 031300Z 34013G22KT 1SM -DZ BR VV002 08/08 A2983 RMK FG8 SLP114"
    assert "okta" in _codes(fg, "METAR")["FG8"].lower() or "fog" in _codes(fg, "METAR")["FG8"].lower()


def test_wind_aloft_and_sea_state() -> None:
    wind = "METAR ENBR 031450Z 17004KT CAVOK 07/04 Q1038 NOSIG RMK WIND 1200FT 03005KT"
    codes = _codes(wind, "METAR")
    assert codes["WIND"] == "Wind"
    assert "1200" in codes["1200FT"]
    assert "ft" in codes["1200FT"].lower()
    assert "WIND" not in _residual_text(wind, "METAR")
    assert "1200FT" not in _residual_text(wind, "METAR")
    sea = "METAR ENHE 031450Z 25029KT 8000 OVC007 08/08 Q1031 W10/S4"
    codes_s = _codes(sea, "METAR")
    assert "W10/S4" in codes_s
    assert "sea" in codes_s["W10/S4"].lower() or "wave" in codes_s["W10/S4"].lower()
    assert "W10/S4" not in _residual_text(sea, "METAR")


def test_rwy_and_bird_hazard() -> None:
    rwy = "METAR LTBJ 031450Z 14008KT 120V180 9999 SCT030 BKN100 18/15 Q1013 NOSIG RMK RWY16 16009KT"
    codes = _codes(rwy, "METAR")
    assert "runway" in codes["RWY16"].lower()
    assert "RWY16" not in _residual_text(rwy, "METAR")
    bird = "METAR SPQT 031400Z VRB01KT 9999 FEW008 28/24 Q1014 NOSIG RMK BIRD HAZARD RWY 06/24"
    codes_b = _codes(bird, "METAR")
    assert codes_b["BIRD"] == "Bird"
    assert "hazard" in codes_b["HAZARD"].lower()
    assert "BIRD" not in _residual_text(bird, "METAR")


def test_sigmet_ellipsis_hazards() -> None:
    tac = (
        "WSUS32 KKCI 022355\n"
        "MKCC WST 022355\n"
        "CONVECTIVE SIGMET 55C\n"
        "VALID UNTIL 0155Z\n"
        "TX OK KS\n"
        "FROM SLN-60WSW MCI-40NW TTT-50E ABI-50SSE CDS-SLN\n"
        "AREA SEV TS MOV FROM 22035KT. TOPS ABV FL450.\n"
        "TORNADOES...HAIL TO 1 IN...WIND GUSTS TO 60KT POSS.\n"
    )
    codes = _codes(tac, "SIGMET")
    assert "tornado" in codes["TORNADOES...HAIL"].lower()
    assert "hail" in codes["TORNADOES...HAIL"].lower() or "hail" in codes.get("HAIL", "").lower()
    assert "inch" in codes["IN...WIND"].lower() or "wind" in codes["IN...WIND"].lower()
    residual = _residual_text(tac, "SIGMET")
    assert "TORNADOES...HAIL" not in residual
    assert "IN...WIND" not in residual


def test_taf_not_sked_and_metwatch() -> None:
    not_sked = "TAF KCGI 031120Z 0312/0412 17012G20KT P6SM OVC050 FM040900 19005KT P6SM SCT009 BKN015 AMD NOT SKED"
    codes = _codes(not_sked, "TAF")
    assert codes["NOT"] == "Not"
    assert "scheduled" in codes["SKED"].lower()
    assert "NOT" not in _residual_text(not_sked, "TAF")
    assert "SKED" not in _residual_text(not_sked, "TAF")
    metwatch = (
        "TAF KNID 030700Z 0307/0407 VRB06KT 9999 FEW250 QNH2993INS "
        "AUTOMATED SENSOR METWATCH 0307 TIL 0316 TX22/0321Z TN07/0314Z"
    )
    codes_m = _codes(metwatch, "TAF")
    assert "automated" in codes_m["AUTOMATED"].lower()
    assert "sensor" in codes_m["SENSOR"].lower()
    assert "metwatch" in codes_m["METWATCH"].lower() or "watch" in codes_m["METWATCH"].lower()
    for tok in ("AUTOMATED", "SENSOR", "METWATCH"):
        assert tok not in _residual_text(metwatch, "TAF")


def test_sigmet_fir_name_and_coord_scraps() -> None:
    fir = (
        "WSRS31 RURD 022242\n"
        "URRV SIGMET 2 VALID 022300/030230 URRR-\n"
        "URRV ROSTOV-NA-DONU FIR EMBD TS OBS N OF LINE N4928 E04021 TOP FL360=\n"
    )
    codes = _codes(fir, "SIGMET")
    assert "ROSTOV-NA-DONU" in codes
    assert "FIR" in codes["ROSTOV-NA-DONU"] or "name" in codes["ROSTOV-NA-DONU"].lower()
    assert "ROSTOV-NA-DONU" not in _residual_text(fir, "SIGMET")
    colon = (
        "WSCA31 MDSD 022215\n"
        "MDCS SIGMET 2\n"
        "VALID 022215/030215 MDSD-\n"
        "MDCS SANTO DOMINGO FIR: EMBD TS OBS AT 2205Z WI N2023 W07028 TOP FL450=\n"
    )
    codes_c = _codes(colon, "SIGMET")
    assert "FIR:" in codes_c or "FIR" in codes_c
    # leading hyphen on latitude scrap
    poly = (
        "WSBC31 FBSK 022030\n"
        "FBGR SIGMET A06 VALID 022030/030030 FBSK-\n"
        "FBGR GABORONE FIR FRQ TS OBS WI S2033 E02124 -S2233 E02549 TOP FL430=\n"
    )
    codes_p = _codes(poly, "SIGMET")
    assert "-S2233" in codes_p or "S2233" in {k.lstrip("-") for k in codes_p}
    residual = _residual_text(poly, "SIGMET")
    assert "-S2233" not in residual
