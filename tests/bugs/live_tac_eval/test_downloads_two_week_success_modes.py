"""Success-mode regressions from the Sep 2026 Downloads two-week dump.

Caribbean VCSH/VCTS/TS and MKJP //// must not reintroduce dump false positives.
Clean reports must stay free of error-severity lint.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tests.bugs.live_tac_eval.fixtures.downloads_two_week import (
    SUCCESS_NO_INVALID_WEATHER,
    SUCCESS_NO_LINT_ERRORS,
    SUCCESS_NO_MISSING_VISIBILITY,
    T007_COR,
    T020_CLEAN,
)
from tests.bugs.live_tac_eval.helpers import (
    assert_absent_codes,
    assert_has_code,
    assert_no_error_severity,
    lint_annex3,
)


@pytest.mark.parametrize(
    ("case_id", "product", "tac"),
    SUCCESS_NO_INVALID_WEATHER,
    ids=[row[0] for row in SUCCESS_NO_INVALID_WEATHER],
)
def test_annex3_weather_tokens_not_invalid_weather(
    case_id: str, product: str, tac: str
) -> None:
    report = lint_annex3(tac, product=product)
    assert_absent_codes(report, ("INVALID_WEATHER",))


@pytest.mark.parametrize(
    ("case_id", "product", "tac"),
    SUCCESS_NO_MISSING_VISIBILITY,
    ids=[row[0] for row in SUCCESS_NO_MISSING_VISIBILITY],
)
def test_mkjp_slash_visibility_not_missing(
    case_id: str, product: str, tac: str
) -> None:
    report = lint_annex3(tac, product=product)
    assert_absent_codes(report, ("MISSING_VISIBILITY",))


@pytest.mark.parametrize(
    ("case_id", "product", "tac"),
    SUCCESS_NO_LINT_ERRORS,
    ids=[row[0] for row in SUCCESS_NO_LINT_ERRORS],
)
def test_success_cases_have_no_error_severity(
    case_id: str, product: str, tac: str
) -> None:
    report = lint_annex3(tac, product=product)
    assert_no_error_severity(report)


def test_clean_metar_may_emit_nosig_info() -> None:
    report = lint_annex3(T020_CLEAN, product="METAR")
    assert_has_code(report, "NOSIG_PRESENT", severity="info")
    assert_no_error_severity(report)


def test_cor_metar_emits_cor_info_not_error() -> None:
    report = lint_annex3(T007_COR, product="METAR")
    assert_has_code(report, "COR_PRESENT", severity="info")
    assert_no_error_severity(report)
