"""Failure-mode regressions from the Sep 2026 Downloads two-week dump.

Assert keep-as-error dispositions. Do not soften MISSING_VISIBILITY.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tests.bugs.live_tac_eval.fixtures.downloads_two_week import (
    FAILURE_MISSING_VISIBILITY,
)
from tests.bugs.live_tac_eval.helpers import assert_has_code, lint_annex3


@pytest.mark.parametrize(
    ("case_id", "product", "tac"),
    FAILURE_MISSING_VISIBILITY,
    ids=[row[0] for row in FAILURE_MISSING_VISIBILITY],
)
def test_missing_visibility_stays_error(case_id: str, product: str, tac: str) -> None:
    report = lint_annex3(tac, product=product)
    assert_has_code(report, "MISSING_VISIBILITY", severity="error")
