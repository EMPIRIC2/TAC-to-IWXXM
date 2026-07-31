"""Parser-branch coverage for METAR/SPECI US REMARKS (S032 push gate)."""

from __future__ import annotations

from tac2iwxxm.products import metar_speci as ms


def test_lightning_type_and_sector_matrix() -> None:
    assert ms._lightning_type_code("") is None
    assert ms._lightning_type_code("XX") is None
    assert ms._lightning_type_code("ICCCCG") == "CCCGIC"
    assert ms._lightning_type_code("ICCG") == "ICCG"
    assert ms._lightning_type_code("CCCG") == "CCCG"
    assert ms._lightning_type_code("ICCC") == "ICCC"
    assert ms._lightning_type_code("CG") == "CG"
    assert ms._lightning_sector(None) is None
    assert ms._lightning_sector("ALQDS") == {"in_all_quadrants": True}
    assert ms._lightning_sector("ZZ") is None
    sector = ms._lightning_sector("N-E")
    assert sector is not None
    assert sector["in_all_quadrants"] is False


def test_sky_convective_hail_precip_recent_helpers() -> None:
    assert ms._sky_level_field("/", 30)["nil_reason"]
    sky = ms._parse_sky_types_remark("8////")
    assert sky is not None
    assert "low_nil_reason" in sky
    mixed = ms._parse_sky_types_remark("8/12/")
    assert mixed is not None
    assert "low_href" in mixed
    assert "high_nil_reason" in mixed
    conv = ms._parse_convective_remark("CB DSNT N MOV N")
    assert conv is not None
    assert conv["direction_of_motion_deg"] == 360.0
    assert ms._parse_hail_size_remark("GR LT 1/4") is not None
    assert ms._parse_hail_size_remark("GR 1 1/2") is not None
    assert ms._parse_hail_size_remark("GR 1/4") is not None
    assert ms._parse_hail_size_remark("GR 2") is not None
    assert ms._precip_6_period(18) == "PT6H"
    assert ms._precip_6_period(17) == "PT3H"
    recent = ms._parse_recent_weather_remarks("RAB05E15 RAE1545")
    assert len(recent) >= 1
    assert any("begin_minute" in r for r in recent)
    qty = ms._parse_processed_precip("P0000 60009 70015", hour=18)
    assert len(qty) == 3


def test_trend_wx_and_remarks_free_text() -> None:
    ir = {"day": 15, "hour": 18, "minute": 0, "station": "KJFK"}
    trend = ms._parse_trend_group(ir, "TEMPO", "1200 -RA BR NSC")
    assert trend is not None
    assert trend.get("weather")
    assert trend.get("cloud_nsc") is True
    cavok = ms._parse_trend_group(ir, "BECMG", "CAVOK")
    assert cavok is not None
    assert cavok.get("cavok") is True
    leftover = ms._remarks_free_text("AO2 SLP125 T01230101 EXTRA TEXT")
    assert "EXTRA" in leftover or "TEXT" in leftover


def test_convective_partial_and_rvr_metre_ft() -> None:
    assert ms._parse_convective_remark("TS") is not None
    assert ms._parse_convective_remark("CB VC N") is not None
    assert ms._parse_hail_size_remark("GR") is None
    recent = ms._parse_recent_weather_remarks("RAB1805E1845")
    assert any(r.get("begin_hour") == 18 for r in recent)
    from tac2iwxxm.products.metar_speci import parse_metar_speci

    ir_m = parse_metar_speci(
        "METAR KJFK 151800Z 18008KT 3SM R04/M0200V0600N 10/05 A2992",
        product="METAR",
    )
    assert ir_m["rvr"]["variable"] is True
    assert ir_m["rvr"]["below_sensor_minimum"] is True
    ir_ft = parse_metar_speci(
        "METAR KJFK 151800Z 18008KT 3SM R04/P6000FT 10/05 A2992",
        product="METAR",
    )
    assert ir_ft["rvr"]["mean_m"] > 1000
