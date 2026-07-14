"""Shared TAC business-rule pack skeleton (seven products)."""

from __future__ import annotations

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


def check_parse_gate(tac_text: str, product: str) -> tuple[list[Issue], list[Fix]]:
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
            Issue(
                severity="error",
                code="UNKNOWN_PRODUCT",
                message=f"Unknown product {product!r}; expected one of {list(PRODUCTS)}",
            )
        )
        return issues, fixes

    start, end, stripped = _content_bounds(tac_text)
    if not stripped:
        issues.append(
            Issue(
                severity="error",
                code="EMPTY_TAC",
                message="TAC text is empty",
                location="body",
                start=start,
                end=end,
            )
        )
        return issues, fixes

    keywords = PRODUCT_KEYWORDS[product]
    upper = stripped.upper()
    if not any(keyword in upper for keyword in keywords):
        issues.append(
            Issue(
                severity="error",
                code="MISSING_PRODUCT_KEYWORD",
                message=f"{product} TAC must contain one of {list(keywords)}",
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
                Issue(
                    severity="error",
                    code="MISSING_TERMINATOR",
                    message=f"{product} TAC should end with '='",
                    location="terminator",
                    start=term_start,
                    end=term_end,
                )
            )
            fixes.append(
                Fix(
                    code="normalize_terminator",
                    message="Append report terminator '='",
                    replacement=stripped.rstrip() + "=",
                )
            )

    return issues, fixes


def check_product_rules(tac_text: str, product: str) -> list[Issue]:
    """
    Product-specific skeleton rules (expanded in later milestones).

    Currently a no-op placeholder once parse-gate passes — keeps dispatch
    wired for all seven products.
    """
    _ = tac_text, product
    return []


__all__ = ["check_parse_gate", "check_product_rules"]
