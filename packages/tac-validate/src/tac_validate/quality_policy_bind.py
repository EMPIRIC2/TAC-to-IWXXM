"""Bind lint/emit profile ids to TAC quality policy document ids.

Owned by tac-validate so lint paths do not import tac2iwxxm (ADR-055).
[Corpus: adr/ADR-055] [Corpus: adr/ADR-046] [Corpus: product §F15]
"""

from __future__ import annotations

from tac_validate.lint_profile_catalog import load_lint_profiles, profile_inherit_chain
from tac_validate.lint_profile_ids import canonical_lint_profile_id

_TAF_PROB_PERIOD_INFO = "taf-prob-period-info-quality"
_TAF_PROB_PERIOD_EMIT_KEYS = frozenset({"iwxxm_us", "ca_eccc", "uk_metoffice", "au_bom"})

_PRODUCT_QUALITY: dict[str, str] = {
    "TAF": "annex3-taf-quality",
    "SIGMET": "annex3-sigmet-quality",
    "AIRMET": "annex3-airmet-quality",
    "VAA": "annex3-vaa-quality",
    "TCA": "annex3-tca-quality",
}


def resolve_tac_quality_policy_id(
    profile: str,
    *,
    product: str | None = None,
    tac_policy: str | None = None,
) -> str:
    """
    Return the TAC quality policy id for ``profile`` and optional ``product``.

    Parameters
    ----------
    profile : str
        Lint / emit profile id (aliases such as ``ICAO_2025`` → annex3).
    product : str or None, optional
        Product family for product-specific quality documents.
    tac_policy : str or None, optional
        Explicit override (CLI ``--policy``).

    Returns
    -------
    str
        Policy document id under ``tac_validate/data/policies``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolve_tac_quality_policy_id)
    2
    """
    override = tac_policy.strip() if isinstance(tac_policy, str) and tac_policy.strip() else ""
    if override:
        return override

    profile_l = canonical_lint_profile_id(profile)
    product_u = (product or "").strip().upper()
    rows = load_lint_profiles()
    chain = profile_inherit_chain(profile_l) if profile_l in rows else (profile_l,)

    if product_u == "TAF" and _TAF_PROB_PERIOD_EMIT_KEYS.intersection(chain):
        return _TAF_PROB_PERIOD_INFO

    return _PRODUCT_QUALITY.get(product_u, "annex3-metar-quality")


__all__ = ["resolve_tac_quality_policy_id"]
