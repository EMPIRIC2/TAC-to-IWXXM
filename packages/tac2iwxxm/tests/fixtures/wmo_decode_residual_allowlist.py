"""Expected-residual allowlist for EV-027 / TC-EV027-003 (S02.M1 package SoT).

Entries require standing-doc intent (F9 G4 / ADR-025) and a linked child issue.
Unexpected residuals must not be papered over here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExpectedResidual:
    """Allowlisted residual policy for a catalog-registered official peer."""

    catalog_id: str
    doc_intent: str  # e.g. "F9 G4" / "ADR-025"
    issue: str
    residual_text: str | None = None  # exact match when set
    allow_any: bool = False  # G4 best-effort — any residual text permitted


# Doc-intentional G4 peers (#820) — fuller VAA/TCA decode tracked separately.
EXPECTED_RESIDUALS: tuple[ExpectedResidual, ...] = (
    ExpectedResidual(
        catalog_id="vaa_a7_2",
        doc_intent="F9 G4 / ADR-025 sparse best-effort",
        issue="#820",
        allow_any=True,
    ),
    ExpectedResidual(
        catalog_id="tca_a2_2",
        doc_intent="F9 G4 / ADR-025 sparse best-effort",
        issue="#820",
        allow_any=True,
    ),
)


def allowlisted_texts(catalog_id: str) -> set[str]:
    return {e.residual_text for e in EXPECTED_RESIDUALS if e.catalog_id == catalog_id and e.residual_text is not None}


def allows_any_residual(catalog_id: str) -> bool:
    return any(e.allow_any and e.catalog_id == catalog_id for e in EXPECTED_RESIDUALS)
