"""T2.7: soft-fail sub-second benches for lint + validate alone (ADR-016 Q11=C).

Soft until cutover — failures are reported as warnings / xfail-soft, not hard CI red.
"""

from __future__ import annotations

import time
import warnings

import pytest
from iwxxm_validate import validate
from tac_validate import lint

SOFT_BUDGET_S = 1.0

METAR = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034="
XML = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2023-1"
             xmlns:gml="http://www.opengis.net/gml/3.2"
             gml:id="uuid.bench"
             reportStatus="NORMAL"
             permissibleUsage="OPERATIONAL"/>
"""


def _soft_assert_under_budget(elapsed: float, label: str) -> None:
    if elapsed > SOFT_BUDGET_S:
        warnings.warn(
            f"SOFT PERF: {label} took {elapsed:.3f}s (budget {SOFT_BUDGET_S}s); "
            "hard-fail deferred to cutover (ADR-016 Q11=C)",
            stacklevel=2,
        )


def test_bench_lint_alone_soft() -> None:
    start = time.perf_counter()
    report = lint(METAR, product="METAR")
    elapsed = time.perf_counter() - start
    assert report.ok is True
    _soft_assert_under_budget(elapsed, "tac_validate.lint")


def test_bench_validate_alone_soft() -> None:
    start = time.perf_counter()
    report = validate(
        XML, iwxxm_version="2023-1", profile="annex3", levels=("xsd", "schematron")
    )
    elapsed = time.perf_counter() - start
    assert hasattr(report, "ok")
    _soft_assert_under_budget(elapsed, "iwxxm_validate.validate")


@pytest.mark.parametrize("label,fn", [("lint", "lint"), ("validate", "validate")])
def test_bench_entrypoints_callable(label: str, fn: str) -> None:
    assert label and callable(lint if fn == "lint" else validate)
