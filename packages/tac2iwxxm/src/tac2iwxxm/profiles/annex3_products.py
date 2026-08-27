"""Backward-compatible re-exports for annex3 product emitters (EV-037 TD-2)."""

# pyright: reportPrivateUsage=false

from tac2iwxxm.profiles.annex3_emit import (
    emit_airmet_annex3,
    emit_convective_sigmet_annex3,
    emit_sigmet_annex3,
    emit_swxa_annex3,
    emit_taf_annex3,
    emit_tca_annex3,
    emit_vaa_annex3,
    emit_vona_annex3,
)
from tac2iwxxm.profiles.annex3_emit.sigmet import (
    _is_wmo_sigmet_multi_location_va_yudd,
    _is_wmo_sigmet_va_eggx,
    _sigmet_geometry_xml,
    _sigmet_tc_forecast_xml,
    _sigmet_tc_position_xml,
    _sigmet_tropical_cyclone_xml,
    _sigmet_volcano_xml,
    _wmo_multi_location_va_pos_list,
)
from tac2iwxxm.profiles.annex3_emit.swxa import _assert_swxa_advisory_xml, _swxa_analysis_xml
from tac2iwxxm.profiles.annex3_emit.taf import _fmt_taf_speed
from tac2iwxxm.profiles.annex3_emit.tca import _assert_tca_advisory_xml
from tac2iwxxm.profiles.annex3_emit.vona import (
    _assert_vona_xml,
    _vona_ash_movement_token,
)

__all__ = [
    "emit_airmet_annex3",
    "emit_convective_sigmet_annex3",
    "emit_sigmet_annex3",
    "emit_swxa_annex3",
    "emit_taf_annex3",
    "emit_tca_annex3",
    "emit_vaa_annex3",
    "emit_vona_annex3",
    "_assert_swxa_advisory_xml",
    "_assert_tca_advisory_xml",
    "_assert_vona_xml",
    "_fmt_taf_speed",
    "_is_wmo_sigmet_multi_location_va_yudd",
    "_is_wmo_sigmet_va_eggx",
    "_sigmet_geometry_xml",
    "_sigmet_tc_forecast_xml",
    "_sigmet_tc_position_xml",
    "_sigmet_tropical_cyclone_xml",
    "_sigmet_volcano_xml",
    "_swxa_analysis_xml",
    "_vona_ash_movement_token",
    "_wmo_multi_location_va_pos_list",
]
