"""Dual-profile lint compare harness (S059 / EV-050 / TC-EV050-007 / AC7).

Compares issue-code multisets for the same TAC under ``annex3`` vs ``iwxxm_us``.
Divergent codes must appear in the intentional allowlist or the compare **fails**.
Products without an ``iwxxm_us`` profile return disposition ``na`` (not a fail).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from tac_validate.api import lint
from tac_validate.profiles import (
    PROFILE_ANNEX3,
    PROFILE_IWXXM_US,
    iwxxm_us_applicable,
)

# Codes that may differ across profiles by design (L5 US overlay / awareness).
# Expand in T3.2/T3.3 as disposition table grows; unknown diffs fail the harness.
INTENTIONAL_PROFILE_DIVERGENCE_CODES: Final[frozenset[str]] = frozenset(
    {
        # Present today under both profiles (shared awareness); reserved if gating splits later.
        "REMARK_US_EXTENSION",
    }
)


@dataclass(frozen=True)
class ProfileLintCompare:
    """Result of comparing annex3 vs iwxxm_us lint outcomes for one TAC."""

    product: str
    disposition: str  # "dual" | "na"
    annex3_codes: frozenset[str]
    iwxxm_us_codes: frozenset[str] | None
    divergent_codes: frozenset[str]
    unclassified_divergent: frozenset[str]
    ok: bool
    note: str = ""


def _issue_codes(tac_text: str, *, product: str, profile: str) -> frozenset[str]:
    report = lint(tac_text, product=product, profile=profile)
    return frozenset(i.code for i in report.issues)


def compare_lint_profiles(tac_text: str, *, product: str) -> ProfileLintCompare:
    """
    Lint ``tac_text`` under both profiles (or mark N/A) and classify divergences.

    Parameters
    ----------
    tac_text :
        TAC report text.
    product :
        F6 / deepen product id.

    Returns
    -------
    ProfileLintCompare
        ``ok`` is False only when dual-applicable and unclassified codes diverge.
    """
    product_u = product.upper()
    annex3_codes = _issue_codes(tac_text, product=product_u, profile=PROFILE_ANNEX3)

    if not iwxxm_us_applicable(product_u):
        return ProfileLintCompare(
            product=product_u,
            disposition="na",
            annex3_codes=annex3_codes,
            iwxxm_us_codes=None,
            divergent_codes=frozenset(),
            unclassified_divergent=frozenset(),
            ok=True,
            note="iwxxm_us unsupported for product - N/A (not fail)",
        )

    iwxxm_us_codes = _issue_codes(tac_text, product=product_u, profile=PROFILE_IWXXM_US)
    divergent = annex3_codes.symmetric_difference(iwxxm_us_codes)
    unclassified = divergent - INTENTIONAL_PROFILE_DIVERGENCE_CODES
    return ProfileLintCompare(
        product=product_u,
        disposition="dual",
        annex3_codes=annex3_codes,
        iwxxm_us_codes=iwxxm_us_codes,
        divergent_codes=divergent,
        unclassified_divergent=unclassified,
        ok=not unclassified,
        note="" if not unclassified else f"unclassified divergent codes: {sorted(unclassified)}",
    )


__all__ = [
    "INTENTIONAL_PROFILE_DIVERGENCE_CODES",
    "ProfileLintCompare",
    "compare_lint_profiles",
]
