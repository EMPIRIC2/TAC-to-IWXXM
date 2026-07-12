"""T4.4: soft-fail sub-second benches for convert + lint→convert→validate (ADR-016 Q11=C).

Soft until cutover — over-budget runs warn only; hard-fail is T4.5 / cutover gate.
"""

from __future__ import annotations

import time
import warnings

from iwxxm_validate import validate
from tac_validate import lint

from tac2iwxxm import convert

SOFT_BUDGET_S = 1.0
METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="


def _soft_assert_under_budget(elapsed: float, label: str) -> None:
    if elapsed > SOFT_BUDGET_S:
        warnings.warn(
            f"SOFT PERF: {label} took {elapsed:.3f}s (budget {SOFT_BUDGET_S}s); "
            "hard-fail deferred to cutover (ADR-016 Q11=C / ADR-017)",
            stacklevel=2,
        )


def test_bench_convert_alone_soft() -> None:
    start = time.perf_counter()
    result = convert(METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    elapsed = time.perf_counter() - start
    assert result.ok is True and result.xml
    _soft_assert_under_budget(elapsed, "tac2iwxxm.convert")


def test_bench_lint_convert_validate_lib_path_soft() -> None:
    """Q11 path B: lint → convert → Schematron/XSD library chain (soft)."""
    start = time.perf_counter()
    lint_report = lint(METAR, product="METAR")
    assert lint_report.ok is True
    conv = convert(METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert conv.ok and conv.xml
    val = validate(
        conv.xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("xsd", "schematron"),
    )
    elapsed = time.perf_counter() - start
    assert hasattr(val, "ok")
    _soft_assert_under_budget(elapsed, "lint→convert→validate")
