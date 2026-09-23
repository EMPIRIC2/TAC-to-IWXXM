"""Public ``lint()`` entrypoint for TAC parse gate + rule pack."""

from __future__ import annotations

from collections.abc import Sequence

from tac_validate.ahl import lint_ahl_bulletin, looks_like_ahl
from tac_validate.lint_profile_catalog import apply_profile_deltas, lint_profile_spec
from tac_validate.match_port import DecodeMatch, MatchPort, match_port_spans, spans_from_port
from tac_validate.models import LintReport
from tac_validate.products import PRODUCTS
from tac_validate.profiles import (
    PROFILE_ANNEX3,
    ca_eccc_applicable,
    in_imd_applicable,
    iwxxm_us_lint_applicable,
    normalize_profile,
)
from tac_validate.rules import check_parse_gate, check_product_rules


def _lint_tac_report(
    tac_text: str,
    product: str,
    profile: str,
) -> LintReport:
    """
    Internal helper ``_lint_tac_report``.

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    product_u = product.upper()
    issues, fixes = check_parse_gate(tac_text, product_u, profile=profile)
    if not any(i.severity == "error" for i in issues):
        issues.extend(check_product_rules(tac_text, product_u, profile=profile))
    ok = not any(i.severity == "error" for i in issues)
    return LintReport(ok=ok, product=product_u, issues=issues, fixes=fixes)


def lint(
    tac_text: str,
    *,
    product: str = "METAR",
    profile: str = PROFILE_ANNEX3,
    match_port: MatchPort | Sequence[DecodeMatch] | None = None,
) -> LintReport:
    """
    Lint TAC text for ``product`` using the shared rule-pack skeleton.

    When ``tac_text`` starts with a WMO AHL, the heading is treated as
    communications format and each contained report is linted as ``product``.

    Parameters
    ----------
    tac_text :
        TAC report, fragment, or WMO AHL bulletin.
    product :
        One of AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA, SWXA, VONA.
    profile :
        ``annex3`` (default), ``iwxxm_us``, ``ca_eccc``, ``in_imd``, or another
        id in the lint profile catalog. Profiles that do not differ run the
        Annex 3 rules and keep the requested profile on the report. Calling a
        profile for a product it does not list raises ``ValueError``.

    match_port :
        Optional decode spans. ``None`` keeps the TAC scan. An empty sequence
        makes annex3 METAR theme packs emit ``MISSING_DECODE_MATCH``.

    Returns
    -------
    LintReport
        ``ok`` is ``False`` when any error-severity issue is present.
        Optional ``fixes`` may suggest repairs (Q9=C).

    Raises
    ------
    ValueError
        Unsupported profile name, or ``iwxxm_us`` for a product without US profile.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint)
    2
    """
    profile_l = normalize_profile(profile)
    product_u = product.upper()
    if profile_l == "iwxxm_us" and not iwxxm_us_lint_applicable(product_u):
        raise ValueError(f"profile iwxxm_us is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "ca_eccc" and not ca_eccc_applicable(product_u):
        raise ValueError(f"profile ca_eccc is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "in_imd" and not in_imd_applicable(product_u):
        raise ValueError(f"profile in_imd is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l not in {"annex3", "iwxxm_us", "ca_eccc", "in_imd"}:
        spec = lint_profile_spec(profile_l)
        if spec is None or product_u not in spec.products:
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")

    spans = spans_from_port(match_port)
    token = match_port_spans.set(spans) if spans is not None else None
    try:
        if looks_like_ahl(tac_text):
            report = lint_ahl_bulletin(
                tac_text,
                product=product_u,
                profile=profile_l,
                lint_report=_lint_tac_report,
            )
        else:
            report = _lint_tac_report(tac_text, product_u, profile_l)
        return apply_profile_deltas(report, profile=profile_l, product=product_u)
    finally:
        if token is not None:
            match_port_spans.reset(token)


__all__ = ["PRODUCTS", "lint"]
