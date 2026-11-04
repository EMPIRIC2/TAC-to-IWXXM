"""Live residual: valid NWS ``DVLPG AREA`` must not lint-error.

Product-rule-fix for ``DVLPG_AREA_QUALIFIER`` (#1554 / epic #1551): the
canonical developing-area hazard lead-in after a closed FROM ring is valid
NWS convective SIGMET grammar. Prefer lint must not emit the code on those
live forms; misplaced or incomplete ``DVLPG`` still raises.

[Corpus: product §F15] [Corpus: product §F23] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest
from tac_validate.api import lint_with_profile

# Live WST residuals that previously false-errored on DVLPG_AREA_QUALIFIER.
_DVLPG_AREA_LIVE: tuple[tuple[str, str], ...] = (
    (
        "sigmet-055d7ff848506dae",
        """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB-50WSW END-20N CDS-30ESE AMA-10E MMB
DVLPG AREA TS MOV FROM 22025KT. TOPS TO FL340.
""",
    ),
    (
        "sigmet-62bc3b350e0fe313",
        """\
WSUS32 KKCI 021755
MKCC WST 021755
CONVECTIVE SIGMET 24C
VALID UNTIL 1955Z
OK KS
FROM 30W OSW-40NNW ADM-50N SPS-30NNE END-30W OSW
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL320.
""",
    ),
    (
        "sigmet-83fc4f347eccb160",
        """\
WSUS32 KKCI 022055
MKCC WST 022055
CONVECTIVE SIGMET 41C
VALID UNTIL 2255Z
KS
FROM 60ENE HLC-40NNW SLN-50WNW ICT-50E GCK-60ENE HLC
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL380.
""",
    ),
    (
        "sigmet-9779da4a4c5a9ff8",
        """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 29C
VALID UNTIL 2055Z
IA NE SD
FROM 60ESE ABR-70S FSD-10NNW OBH-50E PIR-60ESE ABR
DVLPG AREA TS MOV FROM 22050KT. TOPS TO FL320.
""",
    ),
    (
        "sigmet-issue-1554-sample",
        """\
WSUS32 KKCI 031655
MKCC WST 031655
CONVECTIVE SIGMET 75C
VALID UNTIL 1855Z
MO KS NE
FROM 60N MCI-30NW BUM-50E SLN-10SSW PWE-60N MCI
DVLPG AREA TS MOV FROM 23010KT. TOPS TO FL260.
""",
    ),
)

# Misplaced DVLPG inside the FROM ring (VOR-offset abuse) — still an error.
_DVLPG_IN_FROM_RING = """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB DVLPG-20N CDS-30ESE AMA-10E MMB
AREA TS MOV FROM 22025KT. TOPS TO FL340.
"""

# Incomplete developing qualifier (DVLPG without AREA) — still an error.
_DVLPG_WITHOUT_AREA = """\
WSUS32 KKCI 021855
MKCC WST 021855
CONVECTIVE SIGMET 30C
VALID UNTIL 2055Z
TX OK
FROM 10E MMB-50WSW END-20N CDS-30ESE AMA-10E MMB
DVLPG TS MOV FROM 22025KT. TOPS TO FL340.
"""


@pytest.mark.parametrize(
    ("place_key", "tac"), _DVLPG_AREA_LIVE, ids=[p for p, _ in _DVLPG_AREA_LIVE]
)
def test_dvlpg_area_live_prefer_lint_no_false_error(place_key: str, tac: str) -> None:
    """Success: prefer lint accepts canonical DVLPG AREA after FROM ring."""
    report = lint_with_profile(tac, product="SIGMET", profile="annex3", icao="KKCI")
    matched = [i for i in report.issues if i.code == "DVLPG_AREA_QUALIFIER"]
    assert not matched, (
        place_key,
        [(i.code, i.severity, i.message) for i in report.issues],
    )


def test_dvlpg_in_from_ring_still_errors() -> None:
    """Failure: DVLPG glued into the FROM ring still raises DVLPG_AREA_QUALIFIER."""
    report = lint_with_profile(
        _DVLPG_IN_FROM_RING, product="SIGMET", profile="annex3", icao="KKCI"
    )
    matched = [i for i in report.issues if i.code == "DVLPG_AREA_QUALIFIER"]
    assert matched
    assert all(i.severity == "error" for i in matched)
    joined = " ".join(i.message for i in matched)
    assert "DVLPG" in joined
    assert not re.search(r"\b(?:ADR-|EV-|Corpus:|F15|F23)\b", joined)


def test_dvlpg_without_area_still_errors() -> None:
    """Failure: incomplete DVLPG (no AREA) still raises DVLPG_AREA_QUALIFIER."""
    report = lint_with_profile(
        _DVLPG_WITHOUT_AREA, product="SIGMET", profile="annex3", icao="KKCI"
    )
    matched = [i for i in report.issues if i.code == "DVLPG_AREA_QUALIFIER"]
    assert matched
    assert all(i.severity == "error" for i in matched)
