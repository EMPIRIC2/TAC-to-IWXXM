"""TC-F29-002 / T1.2 — three-engine runners + needs-fixture skip policy."""

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
_VALIDATE_HAPPY = _TESTDATA / "validate" / "metar_speci" / "metar_happy_path.yml"


def _by_bucket(path: Path) -> dict[str, RuleCase]:
    return {c.bucket: c for c in load_rule_cases(path)}


def test_skip_policy_needs_fixture() -> None:
    cases = _by_bucket(_LINT_VIS)
    with pytest.raises(pytest.skip.Exception, match="needs-fixture"):
        apply_skip_policy(cases["edge_pass"])


def test_skip_policy_oos(tmp_path: Path) -> None:
    path = tmp_path / "oos.yml"
    path.write_text(
        "rule_id: X\nengine: lint\ncases:\n"
        "  - bucket: sad\n    case_id: '01'\n    status: oos\n"
        "    meta: {cite: 'S02.M2'}\n",
        encoding="utf-8",
    )
    case = load_rule_cases(path)[0]
    with pytest.raises(pytest.skip.Exception, match=r"oos — S02\.M2"):
        apply_skip_policy(case)


def test_run_lint_happy_and_sad() -> None:
    cases = _by_bucket(_LINT_VIS)
    run_lint_case(cases["happy"])
    run_lint_case(cases["sad"])


def test_run_lint_skips_needs_fixture() -> None:
    cases = _by_bucket(_LINT_VIS)
    with pytest.raises(pytest.skip.Exception, match="needs-fixture"):
        run_rule_case(cases["edge_fail"])


def test_run_convert_happy() -> None:
    cases = _by_bucket(_CONVERT_NIL)
    run_convert_case(cases["happy"])


def test_run_validate_happy() -> None:
    cases = _by_bucket(_VALIDATE_HAPPY)
    run_validate_case(cases["happy"])


@pytest.mark.parametrize(
    "path,bucket",
    [
        (_LINT_VIS, "happy"),
        (_CONVERT_NIL, "happy"),
        (_VALIDATE_HAPPY, "happy"),
    ],
    ids=["lint", "convert", "validate"],
)
def test_run_rule_case_dispatch(path: Path, bucket: str) -> None:
    run_rule_case(_by_bucket(path)[bucket])
