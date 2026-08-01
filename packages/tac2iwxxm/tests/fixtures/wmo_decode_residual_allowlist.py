"""Expected-residual allowlist for EV-027 / TC-EV027-003 (S02.M1 package SoT).

Entries require standing-doc intent (F9 G4 / ADR-025) and a linked child issue.
Unexpected residuals must not be papered over here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExpectedResidual:
    """One allowlisted residual span for a catalog-registered official peer."""

    catalog_id: str
    residual_text: str
    doc_intent: str  # e.g. "F9 G4" / "ADR-025"
    issue: str


# Start empty — populate only with doc-intentional residuals + child issues (S02.M2=2).
EXPECTED_RESIDUALS: tuple[ExpectedResidual, ...] = ()


def allowlisted_texts(catalog_id: str) -> set[str]:
    return {e.residual_text for e in EXPECTED_RESIDUALS if e.catalog_id == catalog_id}
