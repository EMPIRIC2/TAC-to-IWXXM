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
    allow_any: bool = False  # G4 best-effort - any residual text permitted


# Doc-intentional G4 peers - fuller advisory decode tracked separately.
# EV-030 T3.2-T3.3: official ``vaa_a7_2`` / ``tca_a2_2`` reach residuals == []
# under structured field (+ AHL) decode; allow_any entries removed.
# EV-099: SWXA/VONA structured LABEL decode — drop allow_any for vona_a7_1 / swxa_a7_3.
EXPECTED_RESIDUALS: tuple[ExpectedResidual, ...] = (
    # TC SIGMET A6-2-TC catalog wmoPass (EV-032 / #835); decode still leaves
    # cyclone name / radius / CENTRE tokens until F9 TC deepen.
    ExpectedResidual(
        catalog_id="sigmet_a6_2_tc",
        doc_intent="F9 G4 / TC SIGMET decode deepen (post-#835 convert equality)",
        issue="#835",
        residual_text="GLORIA",
    ),
    ExpectedResidual(
        catalog_id="sigmet_a6_2_tc",
        doc_intent="F9 G4 / TC SIGMET decode deepen (post-#835 convert equality)",
        issue="#835",
        residual_text="250NM",
    ),
    ExpectedResidual(
        catalog_id="sigmet_a6_2_tc",
        doc_intent="F9 G4 / TC SIGMET decode deepen (post-#835 convert equality)",
        issue="#835",
        residual_text="CENTRE",
    ),
)


def allowlisted_texts(catalog_id: str) -> set[str]:
    return {e.residual_text for e in EXPECTED_RESIDUALS if e.catalog_id == catalog_id and e.residual_text is not None}


def allows_any_residual(catalog_id: str) -> bool:
    return any(e.allow_any and e.catalog_id == catalog_id for e in EXPECTED_RESIDUALS)
