"""TC-F29-002 / T1.2 - three-engine runners + needs-fixture skip policy."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.quality_matrices.loaders import RuleCase, load_rule_cases
from tests.quality_matrices.runners import (
    apply_skip_policy,
    run_convert_case,
    run_lint_case,
    run_rule_case,
    run_validate_case,
)

_TESTDATA = Path(__file__).resolve().parent / "testdata"
_LINT_VIS = _TESTDATA / "lint" / "metar_speci" / "INVALID_VISIBILITY.yml"
_CONVERT_NIL = _TESTDATA / "convert" / "metar_speci" / "metar_nil.yml"
_VALIDATE_HAPPY = (
    _TESTDATA
    / "validate"
    / "metar_speci"
    / "METAR_SPECI.MeteorologicalAerodromeObservationReport-1.yml"
)


def _case(path: Path, bucket: str, case_id: str = "01") -> RuleCase:
    for case in load_rule_cases(path):
        if case.bucket == bucket and case.case_id == case_id:
            return case
    raise AssertionError(f"missing {path.name}/{bucket}/{case_id}")


def test_skip_policy_needs_fixture() -> None:
    with pytest.raises(pytest.skip.Exception, match="needs-fixture"):
        apply_skip_policy(_case(_LINT_VIS, "edge_pass"))


def test_skip_policy_oos(tmp_path: Path) -> None:
    path = tmp_path / "oos.yml"
    path.write_text(
        "rule_id: X\nengine: lint\ncases:\n"
        "  - bucket: sad\n    case_id: '01'\n    status: oos\n"
        "    meta: {cite: 'S02.M2'}\n",
        encoding="utf-8",
    )
    case = load_rule_cases(path)[0]
    with pytest.raises(pytest.skip.Exception, match=r"oos - S02\.M2"):
        apply_skip_policy(case)


def test_run_lint_happy_and_sad() -> None:
    run_lint_case(_case(_LINT_VIS, "happy"))
    run_lint_case(_case(_LINT_VIS, "sad"))


def test_run_lint_skips_needs_fixture() -> None:
    with pytest.raises(pytest.skip.Exception, match="needs-fixture"):
        run_rule_case(_case(_LINT_VIS, "edge_fail"))


def test_run_convert_happy() -> None:
    run_convert_case(_case(_CONVERT_NIL, "happy"))


def test_run_validate_happy() -> None:
    run_validate_case(_case(_VALIDATE_HAPPY, "happy"))


@pytest.mark.parametrize(
    ("path", "bucket"),
    [
        (_LINT_VIS, "happy"),
        (_CONVERT_NIL, "happy"),
        (_VALIDATE_HAPPY, "happy"),
    ],
    ids=["lint", "convert", "validate"],
)
def test_run_rule_case_dispatch(path: Path, bucket: str) -> None:
    run_rule_case(_case(path, bucket))
