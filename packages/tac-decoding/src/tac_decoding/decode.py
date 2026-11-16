"""TAC decode/annotate segments for the operator decode panel (F7 / #702).

Produces ordered ``code`` | explanation segments with character offsets, plus
explicit residuals for undecoded spans. VAA/TCA/SWXA/VONA use structured
``LABEL:`` fields; leftover tokens stay explicit (G4).

Models live in ``tac_decoding.models``; helpers are split by responsibility.
[Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.decode_advisory_fields import (
    _iter_advisory_fields,
    _ordinal_day,
    _plain_advisory_value,
    _token_indices_covering,
)
from tac_decoding.decode_api import (
    _decode_bulletin,
    _decode_single_report,
    _leading_report_product,
    _looks_like_ahl_bulletin,
    _shift_decode,
    decode_single_report,
    decode_tac,
    set_bulletin_splitter,
    shift_decode,
)
from tac_decoding.decode_classify import (
    _build_summary,
    _classify,
    _coalesce_residuals,
    _sentence_from_segment,
)
from tac_decoding.decode_explain_advisory import (
    _COMPASS_RE,
    _MONTHS,
    _advisory_field_finder,
    _advisory_field_title,
    _explain_advisory,
    _iter_advisory_ahl,
    _iter_ahl_heading,
)
from tac_decoding.decode_explain_metar import _explain_metar_remark, _explain_metar_speci
from tac_decoding.decode_explain_sigmet import _explain_sigmet_airmet
from tac_decoding.decode_explain_taf import _explain_taf
from tac_decoding.decode_fir import (
    _FIR_NAME_STOP,
    _extend_fir_name_span,
    _fir_name_continuation_token,
)
from tac_decoding.decode_format import (
    _explain_recent_weather,
    _fmt_cloud,
    _fmt_qnh,
    _fmt_time,
    _fmt_valid_period,
    _fmt_vis_sm,
    _fmt_wind,
    _fmt_wx,
    _signed_temp,
)
from tac_decoding.decode_geo import (
    _boundary_points,
    _coord_token,
    _in_convective_area,
    _lat_lon_phrase,
)
from tac_decoding.decode_patterns import (
    _SIG_VALID,
    _TAF_VALID,
)
from tac_decoding.decode_tokens import (
    _canadian_clouds,
    _depth_phrase,
    _friction_phrase,
    _iter_tokens,
    _navaid_chain,
    _okta_phrase,
    _precip_amount,
    _pressure_tendency,
    _qfe,
    _runway_state,
    _rvr_bound,
    _spaced_cavok_span,
    _tenths_c,
    _varying_rvr,
    _whole_miles,
    _wx_began_or_ended,
    _wx_clock,
    _wx_four_digits,
)
from tac_decoding.models.bulletin import _BulletinMeta, _BulletinSplit
from tac_decoding.models.decode_result import DecodeResidual, DecodeResult, DecodeSegment

__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_single_report",
    "decode_tac",
    "set_bulletin_splitter",
    "shift_decode",
]


def __getattr__(name: str) -> object:
    """Lazy re-export of decode_api module state (bulletin splitter port)."""
    if name == "_bulletin_splitter":
        from tac_decoding import decode_api

        return decode_api._bulletin_splitter
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
