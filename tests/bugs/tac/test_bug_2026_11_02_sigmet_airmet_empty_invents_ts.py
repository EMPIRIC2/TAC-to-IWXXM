"""BUG-2026-11-02 — Empty SIGMET/AIRMET body must not invent phenomenon TS.

``_detect_phenomenon`` falls back to ``TS`` when the body has no phenomenon
token. Header-only / empty-body TAC then encodes a fabricated thunderstorm
instead of fail-closed or an explicit missing/nil phenomenon.

Also: ``CNL SIGMET N`` without a cancelled validity group does not match the
cancel parser and falls into the same default-TS path.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest

from tac2iwxxm import convert

_TS_HREF = "AirWxPhenomena/TS"

_EMPTY_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO-="
_FIR_ONLY_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO-\nYUDD SHANLON FIR="
_EMPTY_AIRMET = "YUDD AIRMET 1 VALID 151520/151800 YUSO-="
_INCOMPLETE_CNL = (
    "YUDD SIGMET 3 VALID 101345/101600 YUSO-\nYUDD SHANLON FIR/UIR CNL SIGMET 2="
)


def _phenomenon_hrefs(xml: str) -> list[str]:
    return re.findall(r'phenomenon[^>]*xlink:href="([^"]+)"', xml or "")


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_EMPTY_SIGMET, "SIGMET"),
        (_FIR_ONLY_SIGMET, "SIGMET"),
        (_EMPTY_AIRMET, "AIRMET"),
    ],
)
def test_bug_2026_11_02_empty_body_must_not_invent_ts(tac: str, product: str) -> None:
    """Empty / FIR-only body must not encode AirWxPhenomena/TS."""
    result = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    hrefs = _phenomenon_hrefs(result.xml or "")
    assert not any(_TS_HREF in href for href in hrefs), (
        f"invented TS phenomenon in {product} convert: {hrefs!r}"
    )
    # Prefer hard fail or translation-failed / missing phenomenon over silent TS.
    assert result.ok is False or "nilReason" in (result.xml or "")


def test_bug_2026_11_02_incomplete_cnl_must_not_invent_ts() -> None:
    """CNL without cancelled period must not be treated as a TS SIGMET."""
    result = convert(
        _INCOMPLETE_CNL,
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    xml = result.xml or ""
    hrefs = _phenomenon_hrefs(xml)
    assert not any(_TS_HREF in href for href in hrefs), hrefs
    # Either fail closed or a real cancel report — never a normal TS analysis.
    is_cancel = 'isCancelReport="true"' in xml or "isCancelReport>true" in xml
    assert result.ok is False or is_cancel
