"""Public ``lint()`` entrypoint for TAC parse gate + rule pack."""

from __future__ import annotations

from tac_validate.models import LintReport
from tac_validate.products import PRODUCTS
from tac_validate.rules import check_parse_gate, check_product_rules


def lint(tac_text: str, *, product: str = "METAR") -> LintReport:
    """
    Lint TAC text for ``product`` using the shared rule-pack skeleton.

    Parameters
    ----------
    tac_text :
        TAC report or fragment.
    product :
        One of AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA.

    Returns
    -------
    LintReport
        ``ok`` is ``False`` when any error-severity issue is present.
        Optional ``fixes`` may suggest repairs (Q9=C).
    """
    issues, fixes = check_parse_gate(tac_text, product)
    if not any(i.severity == "error" for i in issues):
        issues.extend(check_product_rules(tac_text, product))

    ok = not any(i.severity == "error" for i in issues)
    return LintReport(ok=ok, product=product, issues=issues, fixes=fixes)


__all__ = ["PRODUCTS", "lint"]
