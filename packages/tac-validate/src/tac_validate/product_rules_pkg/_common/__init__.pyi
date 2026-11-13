"""Type stub for Auto-split package (exec chunks) — basedpyright."""
from typing import Any
from tac_validate.models import Issue as Issue
from pathlib import Path as Path

__all__ = ['Issue', 'Path', '_AHL_HEADING_LINE', '_AIRMET_FAMILIES', '_AIRMET_NO_SEQ', '_AIRMET_PHENOM_CANDIDATE', '_AIRMET_SEQ', '_ALT_INHG_BODY', '_ALT_NOT_OBS_BODY', '_CA_GFA_PHENOM', '_CB_LINE', '_CLOUD_LIKE', '_CLOUD_OK', '_CLOUD_START', '_DANGLING_SEP_RE', '_DTG_LINE', '_DUR_LINE', '_EMPTY_PARENS_RE', '_FN_THEME_RE', '_GFA_CHART', '_ICAO', '_LAYER_CLOUD_PARTS', '_LAYER_CLOUD_TOKEN', '_MAX_WIND_LINE', '_METAR_SPECI_SKIP', '_NCLWS_TAC', '_NO_SWX_EXP', '_NO_VA_EXP', '_NXT_ADVISORY_LINE', '_NXT_MSG_LINE', '_OBS_SWX_LINE', '_OBS_TIME', '_ONSET_LINE', '_PLANNING_REF_RE', '_QNH', '_QNH_NOT_OBS', '_RECENT_WX', '_RESEARCH_REF_RE', '_RMK_AO', '_RMK_LINE', '_RMK_NOSPECI', '_RMK_PK_VAL', '_RMK_PRES_CA', '_RMK_P_OK', '_RMK_SECTOR_VIS_IN_TEXT', '_RMK_SLP_OK', '_RMK_T_OK', '_RVR', '_RVR_OK', '_RVR_RUNWAY_STATE', '_SIGMET_CNL', '_SIGMET_CNL_FIR_MOVED', '_SIGMET_COR', '_SIGMET_FAMILIES', '_SIGMET_FIR_CTA', '_SIGMET_INTENSITY', '_SIGMET_LEVEL_RANGE', '_SIGMET_MOV', '_SIGMET_MOV_DIR', '_SIGMET_MOV_STNR_ADJACENT', '_SIGMET_NO_SEQ', '_SIGMET_NO_VA_EXP', '_SIGMET_OBS_FCST', '_SIGMET_OF_TC_CENTRE', '_SIGMET_PHENOM_CANDIDATE', '_SIGMET_POINT_COORD', '_SIGMET_SEQ', '_SIGMET_SINGLE_LEVEL', '_SIGMET_STNR', '_SIGMET_TC_IDENTITY', '_SIGMET_TC_NAME', '_SIGMET_TC_TOKEN', '_SIGMET_TOP_ABV_BLW', '_SIGMET_VALID_PAIR', '_SIGMET_VA_CLD', '_SIGMET_VA_TOKEN', '_SIGMET_VA_VOLCANO', '_SIGMET_WI', '_SVO_LINE', '_SWXC_LINE', '_SWX_EFFECT_LINE', '_SWX_EFFECT_PREFIX', '_TAF_AT', '_TAF_FM', '_TAF_PROB', '_TAF_SKIP', '_TAF_TL', '_TAF_TX_TN', '_TAF_VALIDITY', '_TAF_VIS_SM', '_TC_LINE', '_TEMP', '_TEMP_DEWPOINT_NIL', '_THEME_CRUMB_RE', '_TRAILING_SEP_RE', '_VAAC_LINE', '_VAGUE_FILLER_RE', '_VALID_PERIOD', '_VIS_BAD', '_VIS_METERS', '_VIS_NOT_OBS', '_VIS_OK', '_VIS_SOLIDUS', '_VOLCANO_LINE', '_WC_MAX_VALIDITY_HOURS', '_WIND', '_WIND_DIR_VAR', '_WIND_PARSE', '_WIND_TOKEN', '_WS_MAX_VALIDITY_HOURS', '_WV_MAX_VALIDITY_HOURS', '_WX_DESCRIPTORS', '_WX_PHENOMENA', '_WX_SIGNIFICANT', '_WX_SPECIAL', '_WX_STANDALONE', '_WX_TOKEN_SHAPE', '_append_remark_issue', '_body_span', '_check_c1_multi_report', '_check_ca_gfa_airmet', '_check_ca_manair', '_check_ca_manobs', '_check_in_imd_taf', '_check_metar_speci_field_order', '_check_phenomenon_membership', '_check_r8_pack', '_check_us_remarks', '_cloud_candidate_tokens', '_consume_wx_descriptors', '_emit_nsc_layer_exclusivity', '_emit_token_info', '_first_icao', '_first_icao_index', '_forecast_or_obs_segments', '_is_valid_cloud_token', '_is_valid_weather_token', '_issue', '_membership_issue', '_report_segment_count', '_strip_research_refs', '_token_index', '_token_span_in_core', '_weather_candidate_tokens', '_weather_in_register', 'issue_from']

_AHL_HEADING_LINE: Any
_AIRMET_FAMILIES: Any
_AIRMET_NO_SEQ: Any
_AIRMET_PHENOM_CANDIDATE: Any
_AIRMET_SEQ: Any
_ALT_INHG_BODY: Any
_ALT_NOT_OBS_BODY: Any
_CA_GFA_PHENOM: Any
_CB_LINE: Any
_CLOUD_LIKE: Any
_CLOUD_OK: Any
_CLOUD_START: Any
_DANGLING_SEP_RE: Any
_DTG_LINE: Any
_DUR_LINE: Any
_EMPTY_PARENS_RE: Any
_FN_THEME_RE: Any
_GFA_CHART: Any
_ICAO: Any
_LAYER_CLOUD_PARTS: Any
_LAYER_CLOUD_TOKEN: Any
_MAX_WIND_LINE: Any
_METAR_SPECI_SKIP: Any
_NCLWS_TAC: Any
_NO_SWX_EXP: Any
_NO_VA_EXP: Any
_NXT_ADVISORY_LINE: Any
_NXT_MSG_LINE: Any
_OBS_SWX_LINE: Any
_OBS_TIME: Any
_ONSET_LINE: Any
_PLANNING_REF_RE: Any
_QNH: Any
_QNH_NOT_OBS: Any
_RECENT_WX: Any
_RESEARCH_REF_RE: Any
_RMK_AO: Any
_RMK_LINE: Any
_RMK_NOSPECI: Any
_RMK_PK_VAL: Any
_RMK_PRES_CA: Any
_RMK_P_OK: Any
_RMK_SECTOR_VIS_IN_TEXT: Any
_RMK_SLP_OK: Any
_RMK_T_OK: Any
_RVR: Any
_RVR_OK: Any
_RVR_RUNWAY_STATE: Any
_SIGMET_CNL: Any
_SIGMET_CNL_FIR_MOVED: Any
_SIGMET_COR: Any
_SIGMET_FAMILIES: Any
_SIGMET_FIR_CTA: Any
_SIGMET_INTENSITY: Any
_SIGMET_LEVEL_RANGE: Any
_SIGMET_MOV: Any
_SIGMET_MOV_DIR: Any
_SIGMET_MOV_STNR_ADJACENT: Any
_SIGMET_NO_SEQ: Any
_SIGMET_NO_VA_EXP: Any
_SIGMET_OBS_FCST: Any
_SIGMET_OF_TC_CENTRE: Any
_SIGMET_PHENOM_CANDIDATE: Any
_SIGMET_POINT_COORD: Any
_SIGMET_SEQ: Any
_SIGMET_SINGLE_LEVEL: Any
_SIGMET_STNR: Any
_SIGMET_TC_IDENTITY: Any
_SIGMET_TC_NAME: Any
_SIGMET_TC_TOKEN: Any
_SIGMET_TOP_ABV_BLW: Any
_SIGMET_VALID_PAIR: Any
_SIGMET_VA_CLD: Any
_SIGMET_VA_TOKEN: Any
_SIGMET_VA_VOLCANO: Any
_SIGMET_WI: Any
_SVO_LINE: Any
_SWXC_LINE: Any
_SWX_EFFECT_LINE: Any
_SWX_EFFECT_PREFIX: Any
_TAF_AT: Any
_TAF_FM: Any
_TAF_PROB: Any
_TAF_SKIP: Any
_TAF_TL: Any
_TAF_TX_TN: Any
_TAF_VALIDITY: Any
_TAF_VIS_SM: Any
_TC_LINE: Any
_TEMP: Any
_TEMP_DEWPOINT_NIL: Any
_THEME_CRUMB_RE: Any
_TRAILING_SEP_RE: Any
_VAAC_LINE: Any
_VAGUE_FILLER_RE: Any
_VALID_PERIOD: Any
_VIS_BAD: Any
_VIS_METERS: Any
_VIS_NOT_OBS: Any
_VIS_OK: Any
_VIS_SOLIDUS: Any
_VOLCANO_LINE: Any
_WC_MAX_VALIDITY_HOURS: Any
_WIND: Any
_WIND_DIR_VAR: Any
_WIND_PARSE: Any
_WIND_TOKEN: Any
_WS_MAX_VALIDITY_HOURS: Any
_WV_MAX_VALIDITY_HOURS: Any
_WX_DESCRIPTORS: Any
_WX_PHENOMENA: Any
_WX_SIGNIFICANT: Any
_WX_SPECIAL: Any
_WX_STANDALONE: Any
_WX_TOKEN_SHAPE: Any
def _append_remark_issue(*args: Any, **kwargs: Any) -> Any: ...
def _body_span(*args: Any, **kwargs: Any) -> Any: ...
def _check_c1_multi_report(*args: Any, **kwargs: Any) -> Any: ...
def _check_ca_gfa_airmet(*args: Any, **kwargs: Any) -> Any: ...
def _check_ca_manair(*args: Any, **kwargs: Any) -> Any: ...
def _check_ca_manobs(*args: Any, **kwargs: Any) -> Any: ...
def _check_in_imd_taf(*args: Any, **kwargs: Any) -> Any: ...
def _check_metar_speci_field_order(*args: Any, **kwargs: Any) -> Any: ...
def _check_phenomenon_membership(*args: Any, **kwargs: Any) -> Any: ...
def _check_r8_pack(*args: Any, **kwargs: Any) -> Any: ...
def _check_us_remarks(*args: Any, **kwargs: Any) -> Any: ...
def _cloud_candidate_tokens(*args: Any, **kwargs: Any) -> Any: ...
def _consume_wx_descriptors(*args: Any, **kwargs: Any) -> Any: ...
def _emit_nsc_layer_exclusivity(*args: Any, **kwargs: Any) -> Any: ...
def _emit_token_info(*args: Any, **kwargs: Any) -> Any: ...
def _first_icao(*args: Any, **kwargs: Any) -> Any: ...
def _first_icao_index(*args: Any, **kwargs: Any) -> Any: ...
def _forecast_or_obs_segments(*args: Any, **kwargs: Any) -> Any: ...
def _is_valid_cloud_token(*args: Any, **kwargs: Any) -> Any: ...
def _is_valid_weather_token(*args: Any, **kwargs: Any) -> Any: ...
def _issue(*args: Any, **kwargs: Any) -> Any: ...
def _membership_issue(*args: Any, **kwargs: Any) -> Any: ...
def _report_segment_count(*args: Any, **kwargs: Any) -> Any: ...
def _strip_research_refs(*args: Any, **kwargs: Any) -> Any: ...
def _token_index(*args: Any, **kwargs: Any) -> Any: ...
def _token_span_in_core(*args: Any, **kwargs: Any) -> Any: ...
def _weather_candidate_tokens(*args: Any, **kwargs: Any) -> Any: ...
def _weather_in_register(*args: Any, **kwargs: Any) -> Any: ...
def issue_from(*args: Any, **kwargs: Any) -> Any: ...
