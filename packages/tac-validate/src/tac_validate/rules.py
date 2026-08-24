"""Shared TAC business-rule pack skeleton (F6 products + F28 SWXA)."""

from __future__ import annotations

from tac_validate.issue_registry import issue_from
from tac_validate.models import Fix, Issue
from tac_validate.products import PRODUCT_KEYWORDS, PRODUCTS


def _content_bounds(tac_text: str) -> tuple[int, int, str]:
    """
    Return inclusive start, exclusive end, and stripped body for ``tac_text``.

    Offsets are relative to the original string so editors can highlight in-place.
    Empty / whitespace-only input spans the entire original string.
    """
    stripped = tac_text.strip()
    if not stripped:
        return 0, len(tac_text), ""
    leading = len(tac_text) - len(tac_text.lstrip())
    return leading, leading + len(stripped), stripped


_CA_METAR_FAMILY_LEADS: tuple[str, ...] = ("METAR", "LWIS", "SAWR")


def _parse_gate_keywords(product: str, profile: str) -> tuple[str, ...]:
    base = PRODUCT_KEYWORDS[product]
    if profile == "ca_eccc" and product == "METAR":
        return _CA_METAR_FAMILY_LEADS
    return base


def check_parse_gate(
    tac_text: str,
    product: str,
    *,
    profile: str = "annex3",
) -> tuple[list[Issue], list[Fix]]:
    """
    Run parse-gate checks shared across products.

    Parameters
    ----------
    tac_text :
        Raw TAC text.
    product :
        F6 product id.

    Returns
    -------
    issues, fixes
        Structured findings and optional repairs. Issues include ``start``/``end``
        character offsets when the rule can locate a span in ``tac_text``.
    """
    issues: list[Issue] = []
    fixes: list[Fix] = []

    if product not in PRODUCTS:
        issues.append(
            issue_from(
                "UNKNOWN_PRODUCT",
                product=product,
                expected=list(PRODUCTS),
            )
        )
        return issues, fixes

    start, end, stripped = _content_bounds(tac_text)
    if not stripped:
        issues.append(
            issue_from(
                "EMPTY_TAC",
                location="body",
                start=start,
                end=end,
            )
        )
        return issues, fixes

    keywords = _parse_gate_keywords(product, profile)
    upper = stripped.upper()
    if not any(keyword in upper for keyword in keywords):
        issues.append(
            issue_from(
                "MISSING_PRODUCT_KEYWORD",
                product=product,
                keywords=list(keywords),
                location="header",
                start=start,
                end=end,
            )
        )

    # Common repairable: missing report terminator '=' on METAR/SPECI/TAF
    if product in {"METAR", "SPECI", "TAF"} and not stripped.rstrip().endswith("="):
        if not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in issues):
            core = stripped.rstrip()
            # Highlight the final character of the report (terminator should follow).
            term_end = start + len(core)
            term_start = term_end - 1 if core else start
            issues.append(
                issue_from(
                    "MISSING_TERMINATOR",
                    location="terminator",
                    start=term_start,
                    end=term_end,
                )
            )
            fixes.append(
                Fix(
                    code="add_terminator",
                    message="Add '='",
                    replacement=stripped.rstrip() + "=",
                )
            )

    return issues, fixes


def check_product_rules(
    tac_text: str,
    product: str,
    *,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Product-specific checklist / template-gate rules (F12 / E10-21).

    Delegates to ``product_rules`` after parse-gate success.
    ``profile`` is reserved for L5 gating (EV-050); L3 membership is shared.
    """
    from tac_validate.product_rules import check_product_rules as _impl

    return _impl(tac_text, product, profile=profile)


__all__ = ["check_parse_gate", "check_product_rules"]
