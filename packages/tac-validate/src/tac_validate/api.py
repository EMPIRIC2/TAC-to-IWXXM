"""Public ``lint()`` entrypoint for TAC parse gate + rule pack."""

from __future__ import annotations

from tac_validate.ahl import lint_ahl_bulletin, looks_like_ahl
from tac_validate.models import LintReport
from tac_validate.products import PRODUCTS
from tac_validate.profiles import PROFILE_ANNEX3, iwxxm_us_applicable, normalize_profile
from tac_validate.rules import check_parse_gate, check_product_rules


def _lint_tac_report(
    tac_text: str,
    product: str,
    profile: str,
) -> LintReport:
    """Lint a single TAC report (no AHL split)."""
    product_u = product.upper()
    issues, fixes = check_parse_gate(tac_text, product_u)
    if not any(i.severity == "error" for i in issues):
        issues.extend(check_product_rules(tac_text, product_u, profile=profile))
    ok = not any(i.severity == "error" for i in issues)
    return LintReport(ok=ok, product=product_u, issues=issues, fixes=fixes)


def lint(
    tac_text: str,
    *,
    product: str = "METAR",
    profile: str = PROFILE_ANNEX3,
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
        ``annex3`` (default) or ``iwxxm_us``. WMO L3 membership is shared; L5 US
        overlay applies only under ``iwxxm_us`` where the product supports it.
        Calling ``iwxxm_us`` for an unsupported product raises ``ValueError``
        (dual-profile harness treats those rows as N/A without calling lint).

    Returns
    -------
    LintReport
        ``ok`` is ``False`` when any error-severity issue is present.
        Optional ``fixes`` may suggest repairs (Q9=C).

    Raises
    ------
    ValueError
        Unsupported profile name, or ``iwxxm_us`` for a product without US profile.
    """
    profile_l = normalize_profile(profile)
    product_u = product.upper()
    if profile_l == "iwxxm_us" and not iwxxm_us_applicable(product_u):
        raise ValueError(f"profile iwxxm_us is not applicable for product {product_u!r} (N/A — use annex3)")

    if looks_like_ahl(tac_text):
        return lint_ahl_bulletin(
            tac_text,
            product=product_u,
            profile=profile_l,
            lint_report=_lint_tac_report,
        )

    return _lint_tac_report(tac_text, product_u, profile_l)


__all__ = ["PRODUCTS", "lint"]
