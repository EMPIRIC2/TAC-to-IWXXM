"""Product-specific TAC checklist and template-gate rules (F12 / E10-21).

Cite paraphrase tables in ``docs/domain/TAC_VALIDATION.md`` only - no Annex prose.
"""

# pyright: reportUnusedImport=false, reportPrivateUsage=false

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import (  # noqa: F401
    _append_remark_issue,
    _body_span,
    _check_c1_multi_report,
    _check_metar_speci_field_order,
    _check_phenomenon_membership,
    _check_r8_pack,
    _cloud_candidate_tokens,
    _emit_token_info,
    _first_icao,
    _first_icao_index,
    _is_valid_cloud_token,
    _is_valid_weather_token,
    _issue,
    _membership_issue,
    _report_segment_count,
    _token_index,
    _token_span_in_core,
    _weather_candidate_tokens,
    _weather_in_register,
)
from tac_validate.product_rules_pkg.metar_speci import _check_metar_speci
from tac_validate.product_rules_pkg.sigmet_airmet import (  # noqa: F401
    _check_sigmet_airmet,
    _sigmet_validity_hours,
)
from tac_validate.product_rules_pkg.swxa import _check_swxa
from tac_validate.product_rules_pkg.taf import _check_taf
from tac_validate.product_rules_pkg.tca import _check_tca
from tac_validate.product_rules_pkg.vaa import _check_vaa
from tac_validate.product_rules_pkg.vona import _check_vona


def check_product_rules(
    tac_text: str,
    product: str,
    *,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Run product checklist / template-gate rules after parse-gate success.

    Parameters
    ----------
    tac_text :
        Raw TAC text.
    product :
        F6 product id.
    profile :
        ``annex3`` or ``iwxxm_us``. Reserved for L5 overlay gating (EV-050 T3.3);
        WMO L3 membership checks are shared across profiles today.

    Returns
    -------
    list[Issue]
        Error-severity findings with spans when possible.
    """
    if product in {"METAR", "SPECI"}:
        return _check_metar_speci(tac_text, product, profile=profile)
    if product == "TAF":
        return _check_taf(tac_text, profile=profile)
    if product in {"SIGMET", "AIRMET"}:
        return _check_sigmet_airmet(tac_text, product, profile=profile)
    if product == "VAA":
        return _check_vaa(tac_text)
    if product == "TCA":
        return _check_tca(tac_text, profile=profile)
    if product == "SWXA":
        return _check_swxa(tac_text, profile=profile)
    if product == "VONA":
        return _check_vona(tac_text)
    return []


__all__ = ["check_product_rules"]
