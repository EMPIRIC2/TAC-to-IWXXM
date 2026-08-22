"""Branch coverage for CA_ECCC emit helpers (EV-064 per-file coverage gate)."""

from __future__ import annotations

import pytest

from tac2iwxxm.profiles import ca_eccc as ca


def test_ca_gml_id_branches() -> None:
    assert ca._ca_gml_id({"station": "CYUL", "auto": True}, "METAR") == "metar.ca.auto.cyul"
    assert ca._ca_gml_id({"station": "CYUL", "visibility_sm": 3}, "METAR") == "metar.ca.vis.sm.cyul"
    assert ca._ca_gml_id({"station": "CYUL", "altimeter_inhg": 30.12}, "METAR") == "metar.ca.alt.a.cyul"
    assert ca._ca_gml_id({"station": "CYUL", "pressure_change_href": "PRESFR"}, "METAR") == "metar.ca.pres.cyul"
    assert ca._ca_gml_id({"station": "CYUL"}, "METAR") == "metar.ca.basic.cyul"


def test_prepare_ca_ir_skips_cavok_and_applies_sm() -> None:
    cavok = ca._prepare_ca_ir({"station": "CYUL", "cavok": True, "visibility_sm": 2})
    assert "visibility_display_uom" not in cavok
    sm = ca._prepare_ca_ir({"station": "CYUL", "visibility_sm": 2})
    assert sm["visibility_display_uom"] == "[mi_i]"
    assert sm["visibility_display_value"] == 2


def test_pressure_change_and_observing_system_hrefs() -> None:
    assert ca._ca_pressure_change_href({"pressure_change_href": "PRESFR"}) == ca.CA_PRES_FALLING
    assert ca._ca_pressure_change_href({"pressure_change_href": "PRESRR"}) == ca.CA_PRES_RISING
    assert ca._ca_pressure_change_href({"pressure_change_href": 1}) is None
    assert ca._ca_observing_system_href({"auto": True}) == ca.CA_OBS_AWOS
    assert ca._ca_observing_system_href({}) is None


def test_addendum_extension_remarks_and_slp() -> None:
    xml = ca._addendum_extension(
        {
            "auto": True,
            "remarks_free_text": "SLP123",
            "sea_level_pressure_hpa": 1012,
            "pressure_change_href": "PRESFR",
        }
    )
    assert "iwxxm-ca:Addendum" in xml
    assert "humanReadableText" in xml
    assert "seaLevelPressure" in xml
    assert ca._addendum_extension({}) == ""


def test_taf_and_airmet_helpers() -> None:
    assert (
        ca._ca_taf_gml_id(
            {"station": "CYUL", "nclws": {"layer_top_ft": 3000, "wind_dir_deg": 240, "wind_speed_kt": 20}}
        )
        == "taf.ca.nclws.cyul"
    )
    assert ca._ca_taf_gml_id({"station": "CYUL"}) == "taf.ca.basic.cyul"
    assert ca._nclws_extension({"station": "CYUL", "nclws": "bad"}) == ""
    assert ca._ca_airmet_gml_id({"fir": "CZUL", "ca_gfa_phenomenon": "FRQ_TCU"}) == ("airmet.ca.gfa.czul")
    assert ca._ca_airmet_gml_id({"fir": "CZUL"}) == "airmet.ca.basic.czul"
    assert ca._ca_airmet_phenomenon_href({"ca_gfa_phenomenon": "FRQ_TCU"}) is not None
    assert ca._ca_airmet_phenomenon_href({}) is None


def test_inject_helpers_noop_when_needle_missing() -> None:
    xml = "<iwxxm:TAF/>"
    assert ca._inject_ca_taf_namespace(xml, iwxxm_version=ca.CA_IWXXM_VERSION) == xml
    assert ca._inject_ca_airmet_namespace(xml, iwxxm_version=ca.CA_IWXXM_VERSION) == xml


def test_emit_wrong_version_raises() -> None:
    ir = {"station": "CYUL", "day": 23, "hour": 18, "minute": 0}
    with pytest.raises(ValueError, match="3.0.0"):
        ca.emit_metar_speci_ca_eccc(ir, product="METAR", iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="3.0.0"):
        ca.emit_taf_ca_eccc(ir, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="3.0.0"):
        ca.emit_airmet_ca_eccc(ir, iwxxm_version="2025-2")
