"""BUG-2026-11-02 — Inverted / zero SIGMET validPeriod must not encode as-is.

``VALID 101600/101200`` currently emits begin 16:00Z and end 12:00Z (end before
begin). ``VALID 101200/101200`` emits a zero-length period. Both succeed.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re
from datetime import datetime

import pytest

from tac2iwxxm import convert

_END_BEFORE = """\
YUDD SIGMET 2 VALID 101600/101200 YUSO-
YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""

_ZERO_LENGTH = """\
YUDD SIGMET 2 VALID 101200/101200 YUSO-
YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""


def _period_bounds(xml: str) -> tuple[datetime, datetime] | None:
    begin = re.search(r"<gml:beginPosition>([^<]+)</gml:beginPosition>", xml or "")
    end = re.search(r"<gml:endPosition>([^<]+)</gml:endPosition>", xml or "")
    if not begin or not end:
        return None
    return (
        datetime.fromisoformat(begin.group(1).replace("Z", "+00:00")),
        datetime.fromisoformat(end.group(1).replace("Z", "+00:00")),
    )


@pytest.mark.parametrize("tac", [_END_BEFORE, _ZERO_LENGTH])
def test_bug_2026_11_02_inverted_or_zero_valid_period_rejected(tac: str) -> None:
    """Convert must not emit end <= begin for VALID groups."""
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    bounds = _period_bounds(result.xml or "")
    if result.ok and bounds is not None:
        begin, end = bounds
        assert end > begin, (
            f"invalid validPeriod begin={begin.isoformat()} end={end.isoformat()}"
        )
    else:
        assert result.ok is False
