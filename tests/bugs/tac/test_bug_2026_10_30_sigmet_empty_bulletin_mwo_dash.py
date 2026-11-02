"""BUG-2026-10-30 — SIGMET AHL + MWO space/omitted dash must not empty_bulletin.

Live-map SIGMETs often put a space before the MWO hyphen (``OEJN -``) or omit
the hyphen (``TTPP`` then FIR line). Bulletin split must still find the FIR
report so convert does not return empty_bulletin.

[Corpus: product §F6] [Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.heading_paste import reports_for_convert

from tac2iwxxm import BulletinSplitError, split_bulletin

# Staging live-map place sigmet-00d0da4360d3a62a (space before MWO hyphen).
_OEJD_SPACE_DASH = """\
WSSD20 OEJD 301402
OEJD SIGMET 02 VALID 301400/301800 OEJN -
OEJD JEDDAH FIR EMBD TS OBS WI N2830 E04125 - N2748 E04407 - N2449
E04122 - N1720 E04346 -
N1624 E04235 - N2421 E03825 - N2830 E04125
TOP ABV FL390  MOV E INTSF=
"""

# Staging shape: MWO CCCC with no trailing hyphen on the VALID line.
_TTPP_NO_DASH = """\
WSCA31 TTPP 301815
TTZP SIGMET 5 VALID 301815/302215 TTPP
TTZP PIARCO FIR EMBD TS OBS AT 1800Z WI N1226 W06323 - N1402 W06423
- N1414 W06228 - N1303 W06203 - N1226 W06323 TOP ABV FL420 STNR WKN=
"""

# Tight dash must keep working (prior hotfix corpus).
_TIGHT_DASH = """\
WSNT04 KKCI 260210
KZWY SIGMET DELTA 10 VALID 260210/260610 KKCI-
NEW YORK OCEANIC FIR FRQ TS OBS AT 0210Z WI N2617 W07254 - N2617 W06818
- N2319 W06726 - N2617 W07254. TOP FL530. MOV ENE 15KT. INTSF.
"""


def _assert_splits(text: str, *, starts_with: str) -> None:
    result = split_bulletin(text, product="SIGMET")
    assert result.meta.report_count >= 1
    assert result.reports[0].upper().startswith(starts_with.upper())
    pasted = reports_for_convert(text, "SIGMET")
    assert pasted is not None
    assert len(pasted.reports) >= 1
    report_text, _offset = pasted.reports[0]
    assert report_text.upper().startswith(starts_with.upper())


def test_bug_2026_10_30_oejd_space_before_mwo_dash_not_empty_bulletin() -> None:
    _assert_splits(_OEJD_SPACE_DASH, starts_with="OEJD SIGMET")


def test_bug_2026_10_30_mwo_without_hyphen_not_empty_bulletin() -> None:
    _assert_splits(_TTPP_NO_DASH, starts_with="TTZP SIGMET")


def test_bug_2026_10_30_tight_mwo_dash_still_splits() -> None:
    _assert_splits(_TIGHT_DASH, starts_with="KZWY SIGMET")


def test_bug_2026_10_30_heading_only_still_empty_bulletin() -> None:
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin("WSSD20 OEJD 301402\n", product="SIGMET")
    assert exc_info.value.code == "empty_bulletin"
