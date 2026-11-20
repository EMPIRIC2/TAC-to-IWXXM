"""Validity day wording: day N means day N of the current month.

Covers evolve-auto test-matrix permutations for the decode-panel formatter
(``_fmt_valid_period`` / SIGMET·AIRMET·TAF validity groups).
"""

from __future__ import annotations

import pytest
from tac_decoding.decode import _SIG_VALID, _TAF_VALID, _fmt_valid_period, decode_tac

_SAME_DAY = "Valid on day 13 of the current month from 18:15 UTC to 22:15 UTC"
_CROSS_DAY = "Valid from day 13 of the current month at 18:15 UTC to day 14 of the current month at 02:00 UTC"
_INSTANT = "Valid on day 13 of the current month from 18:15 UTC to 18:15 UTC"
_TAF_SAME = "Valid on day 13 of the current month from 18:00 UTC to 24:00 UTC"
_TAF_CROSS = "Valid from day 13 of the current month at 18:00 UTC to day 14 of the current month at 24:00 UTC"


def _explanation_for(tac: str, *, product: str, code: str) -> str | None:
    result = decode_tac(tac, product=product)
    for segment in result.segments:
        if segment.code == code:
            return segment.explanation
    return None


def _meanings(tac: str, *, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


# --- S / V+: formatter success (unit) -------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        (
            {
                "day1": 13,
                "hour1": "18",
                "minute1": "15",
                "day2": 13,
                "hour2": "22",
                "minute2": "15",
            },
            _SAME_DAY,
        ),
        (
            {
                "day1": 13,
                "hour1": "18",
                "minute1": "15",
                "day2": 14,
                "hour2": "02",
                "minute2": "00",
            },
            _CROSS_DAY,
        ),
        (
            {
                "day1": 13,
                "hour1": "18",
                "minute1": "15",
                "day2": 13,
                "hour2": "18",
                "minute2": "15",
            },
            _INSTANT,
        ),
    ],
)
def test_fmt_valid_period_success_templates(kwargs: dict[str, object], expected: str) -> None:
    """Happy-path same-day, cross-day, and single-instant templates."""
    assert _fmt_valid_period(**kwargs) == expected  # type: ignore[arg-type]
    assert "of the current month" in expected
    assert "UTC" in expected


def test_fmt_valid_period_repeats_current_month_on_cross_day() -> None:
    text = _fmt_valid_period(
        day1=5,
        hour1="09",
        minute1="00",
        day2=6,
        hour2="11",
        minute2="30",
    )
    assert text.count("of the current month") == 2


# --- S / V+: product decode success ---------------------------------------------------


@pytest.mark.parametrize(
    ("tac", "product", "code", "expected"),
    [
        (
            "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS=",
            "SIGMET",
            "131815/132215",
            _SAME_DAY,
        ),
        (
            "YUDD SIGMET 2 VALID 131815/140200 YUSO- YUDD FIR EMBD TS=",
            "SIGMET",
            "131815/140200",
            _CROSS_DAY,
        ),
        (
            "YUDD SIGMET 2 VALID 131815/131815 YUSO- YUDD FIR EMBD TS=",
            "SIGMET",
            "131815/131815",
            _INSTANT,
        ),
        (
            "YUDD AIRMET 2 VALID 131815/132215 YUSO- YUDD FIR MT OBSC=",
            "AIRMET",
            "131815/132215",
            _SAME_DAY,
        ),
        (
            "YUDD AIRMET 2 VALID 131815/140200 YUSO- YUDD FIR MT OBSC=",
            "AIRMET",
            "131815/140200",
            _CROSS_DAY,
        ),
        (
            "TAF KJFK 131755Z 1318/1324 18010KT=",
            "TAF",
            "1318/1324",
            _TAF_SAME,
        ),
        (
            "TAF KJFK 131755Z 1318/1424 18010KT=",
            "TAF",
            "1318/1424",
            _TAF_CROSS,
        ),
    ],
)
def test_decode_validity_wording_by_product(
    tac: str,
    product: str,
    code: str,
    expected: str,
) -> None:
    """SIGMET, AIRMET, and TAF emit the locked current-month wording."""
    assert _explanation_for(tac, product=product, code=code) == expected


# --- V-: validation failure (malformed day/time groups) -------------------------------


@pytest.mark.parametrize(
    "token",
    [
        "1318/13",  # truncated TAF
        "131815/1322",  # truncated SIGMET
        "131815132215",  # missing slash
        "13AB15/132215",  # non-digit hour
        "VALID",  # marker only
        "",  # missing times
    ],
)
def test_malformed_validity_tokens_do_not_match_period_regexes(token: str) -> None:
    """Malformed day/time groups fail schema match (validation failure)."""
    assert _SIG_VALID.fullmatch(token) is None
    assert _TAF_VALID.fullmatch(token) is None


@pytest.mark.parametrize(
    ("tac", "product", "bad_code"),
    [
        (
            "YUDD SIGMET 2 VALID 131815/1322 YUSO- YUDD FIR EMBD TS=",
            "SIGMET",
            "131815/1322",
        ),
        (
            "TAF KJFK 131755Z 1318/13 18010KT=",
            "TAF",
            "1318/13",
        ),
    ],
)
def test_malformed_validity_in_bulletin_is_not_explained_as_valid(
    tac: str,
    product: str,
    bad_code: str,
) -> None:
    """Rejected validity groups must not receive Valid … current month wording."""
    meanings = _meanings(tac, product=product)
    explanation = meanings.get(bad_code)
    if explanation is not None:
        assert "of the current month" not in explanation
        assert not explanation.startswith("Valid on day")
        assert not explanation.startswith("Valid from day")


def test_valid_payload_accepted_when_group_matches() -> None:
    """Validation success: well-formed groups match and get wording."""
    assert _SIG_VALID.fullmatch("131815/132215") is not None
    assert _TAF_VALID.fullmatch("1318/1424") is not None
    assert (
        _explanation_for(
            "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS=",
            product="SIGMET",
            code="131815/132215",
        )
        == _SAME_DAY
    )


# --- M: mutation modes (create / update / delete) via re-decode -----------------------


def test_mutation_create_validity_on_redecode() -> None:
    """Create: bulletin without a period, then with one — wording appears."""
    before = "YUDD SIGMET 2 YUSO- YUDD FIR EMBD TS="
    after = "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS="
    assert _explanation_for(before, product="SIGMET", code="131815/132215") is None
    assert _explanation_for(after, product="SIGMET", code="131815/132215") == _SAME_DAY


def test_mutation_update_validity_same_to_cross_day() -> None:
    """Update: change same-day period to cross-day — wording updates."""
    same = "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS="
    cross = "YUDD SIGMET 2 VALID 131815/140200 YUSO- YUDD FIR EMBD TS="
    assert _explanation_for(same, product="SIGMET", code="131815/132215") == _SAME_DAY
    assert _explanation_for(cross, product="SIGMET", code="131815/140200") == _CROSS_DAY


def test_mutation_delete_validity_removes_wording() -> None:
    """Delete: strip the period token — Valid wording is gone."""
    with_period = "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS="
    without = "YUDD SIGMET 2 VALID YUSO- YUDD FIR EMBD TS="
    assert _explanation_for(with_period, product="SIGMET", code="131815/132215") == _SAME_DAY
    meanings = _meanings(without, product="SIGMET")
    assert "131815/132215" not in meanings
    assert all("of the current month" not in text for text in meanings.values())


def test_mutation_update_validation_fail_keeps_no_valid_wording() -> None:
    """Update + validation fail: replace good period with truncated token."""
    good = "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS="
    bad = "YUDD SIGMET 2 VALID 131815/1322 YUSO- YUDD FIR EMBD TS="
    assert _explanation_for(good, product="SIGMET", code="131815/132215") == _SAME_DAY
    bad_meanings = _meanings(bad, product="SIGMET")
    assert "131815/132215" not in bad_meanings
    explanation = bad_meanings.get("131815/1322")
    if explanation is not None:
        assert "of the current month" not in explanation


def test_mutation_create_validation_fail_rejects_truncated_taf() -> None:
    """Create + validation fail: TAF with truncated validity is not Valid-worded."""
    tac = "TAF KJFK 131755Z 1318/13 18010KT="
    meanings = _meanings(tac, product="TAF")
    explanation = meanings.get("1318/13")
    if explanation is not None:
        assert "of the current month" not in explanation


# --- Read / query fault surface -------------------------------------------------------


def test_read_query_missing_validity_has_no_period_segment() -> None:
    """Read/query fault: bulletin with VALID marker but no day/time group."""
    meanings = _meanings("YUDD SIGMET 2 VALID YUSO- YUDD FIR EMBD TS=", product="SIGMET")
    assert meanings.get("VALID") == "Validity period marker"
    assert all(not code[:1].isdigit() or "/" not in code for code in meanings)


def test_old_wording_absent_from_decode_output() -> None:
    """Regression: legacy 'Valid day N HH:MM' phrasing must not appear."""
    result = decode_tac(
        "YUDD SIGMET 2 VALID 131815/132215 YUSO- YUDD FIR EMBD TS=",
        product="SIGMET",
    )
    joined = " ".join(segment.explanation for segment in result.segments)
    assert "Valid day 13 18:15" not in joined
    assert "to day 13 22:15" not in joined
    assert _SAME_DAY in joined
