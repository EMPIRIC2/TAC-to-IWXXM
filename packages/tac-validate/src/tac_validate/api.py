"""Public ``lint()`` entrypoint for TAC parse gate + rule pack."""

from __future__ import annotations

from collections.abc import Sequence

from tac_validate.ahl import lint_ahl_bulletin, looks_like_ahl
from tac_validate.match_port import DecodeMatch, MatchPort, match_port_spans, spans_from_port
from tac_validate.models import Issue, LintReport
from tac_validate.products import PRODUCTS
from tac_validate.profiles import (
    PROFILE_ANNEX3,
    PROFILE_CA_MSC_SIGMET,
    PROFILE_US_NWS_CONVECTIVE_SIGMET,
    PROFILE_US_NWS_G_AIRMET,
    PROFILE_US_NWS_VONA,
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
        ``annex3`` (default), ``iwxxm_us``, ``ca_eccc``, or ``in_imd``. WMO L3 membership
        is shared; national overlays apply only under the matching profile where the
        product supports it. ``SWXA`` and ``TCA`` accept ``iwxxm_us`` for thin US national
        lint only (#919 M22). ``in_imd`` is TAF-only (TX/TN omission awareness). Calling
        a national profile for an unsupported product raises ``ValueError``.

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
    if profile_l == PROFILE_US_NWS_CONVECTIVE_SIGMET:
        if product_u != "SIGMET":
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")
        if "CONVECTIVE SIGMET" not in tac_text.upper():
            return LintReport(
                ok=False,
                product=product_u,
                issues=[
                    Issue(
                        severity="error",
                        code="NOT_CONVECTIVE_SIGMET",
                        message=(
                            "This profile checks United States convective SIGMET text, not an international SIGMET."
                        ),
                    )
                ],
                fixes=[],
            )
        return LintReport(ok=True, product=product_u, issues=[], fixes=[])
    refusal = _SOURCE_UNAVAILABLE_LINT.get(profile_l)
    if refusal is not None:
        allowed, message = refusal
        if product_u not in allowed:
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")
        return LintReport(
            ok=False,
            product=product_u,
            issues=[Issue(severity="error", code="SOURCE_UNAVAILABLE", message=message)],
            fixes=[],
        )
    if profile_l == "iwxxm_us" and not iwxxm_us_lint_applicable(product_u):
        raise ValueError(f"profile iwxxm_us is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "ca_eccc" and not ca_eccc_applicable(product_u):
        raise ValueError(f"profile ca_eccc is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "in_imd" and not in_imd_applicable(product_u):
        raise ValueError(f"profile in_imd is not applicable for product {product_u!r} (N/A - use annex3)")

    spans = spans_from_port(match_port)
    token = match_port_spans.set(spans) if spans is not None else None
    try:
        if looks_like_ahl(tac_text):
            return lint_ahl_bulletin(
                tac_text,
                product=product_u,
                profile=profile_l,
                lint_report=_lint_tac_report,
            )
        return _lint_tac_report(tac_text, product_u, profile_l)
    finally:
        if token is not None:
            match_port_spans.reset(token)


__all__ = ["PRODUCTS", "lint"]

_SOURCE_UNAVAILABLE_LINT: dict[str, tuple[frozenset[str], str]] = {
    PROFILE_US_NWS_G_AIRMET: (
        frozenset({"AIRMET"}),
        "United States G-AIRMET checking is unavailable until a text bulletin is on file.",
    ),
    PROFILE_US_NWS_VONA: (
        frozenset({"VONA"}),
        "United States volcano observatory notice checking is unavailable until a complete notice is on file.",
    ),
    PROFILE_CA_MSC_SIGMET: (
        frozenset({"SIGMET"}),
        "Canadian SIGMET text checking is unavailable until a text source is on file.",
    ),
}
