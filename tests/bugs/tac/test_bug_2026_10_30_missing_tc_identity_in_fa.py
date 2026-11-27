"""BUG-2026-10-30 — MISSING_TC_IDENTITY on TC IN-FA OBS AT (no PSN keyword).

US WC form names the cyclone and gives a position via ``OBS AT … N/E``
without ``PSN``. Identity regex required ``TC … PSN`` only.

Live-map full-world probe 2026-10-30: KZAK TC IN-FA, pass=true.
Ticket: #1478. [Corpus: product §F23] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint

_KZAK = """WCPA07 PHFO 300118

KZAK SIGMET TANGO 31 VALID 300120/300720 PHFO-
OAKLAND OCEANIC FIR TC IN-FA OBS AT 0000Z N1755 E14750. CB TOP FL520
WI 160NM OF CENTER. MOV WNW 18KT. NC. FCST 0600Z TC CENTER N1840
E14610."""

_WITH_PSN = """WCJP31 RJTD 301909
RJJJ SIGMET K01 VALID 301909/310109 RJTD-
RJJJ FUKUOKA FIR TC IN-FA PSN N2030 E14325 CB OBS AT 1800Z WI 110NM
OF TC CENTRE TOP FL540 NC
FCST AT 0000Z TC CENTRE PSN N2120 E14255="""

_OF_CENTRE_ONLY = (
    "YUCC SIGMET 3 VALID 251600/252200 YUDO-\n"
    "YUCC AMSWELL FIR CB OBS AT 1600Z WI 250NM OF TC CENTRE TOP FL500 NC="
)

_BARE_TC_OBS = (
    "YUCC SIGMET 3 VALID 251600/252200 YUDO-\n"
    "YUCC AMSWELL FIR TC OBS AT 1600Z WI 250NM OF TC CENTRE TOP FL500 NC="
)


@pytest.mark.parametrize(
    "tac",
    [_KZAK, _WITH_PSN],
    ids=["obs_at_hyphenated", "psn_hyphenated"],
)
def test_bug_2026_10_30_tc_in_fa_identity_accepted(tac: str) -> None:
    codes = {i.code for i in lint(tac, product="SIGMET").issues}
    assert "MISSING_TC_IDENTITY" not in codes
    assert "TC_CYCLONE_IDENTITY" in codes


@pytest.mark.parametrize(
    "tac",
    [_OF_CENTRE_ONLY, _BARE_TC_OBS],
    ids=["of_tc_centre_no_name", "bare_tc_obs_at_no_name"],
)
def test_bug_2026_10_30_tc_without_named_identity_still_missing(tac: str) -> None:
    codes = {i.code for i in lint(tac, product="SIGMET").issues}
    assert "MISSING_TC_IDENTITY" in codes
