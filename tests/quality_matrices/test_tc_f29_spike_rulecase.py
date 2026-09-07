"""TC-F29-005 spike - YAML RuleCase load + node-id shape (S037 / EV-030 T0.3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.quality_matrices.loaders import BUCKETS, RuleCase, load_rule_cases

_SPIKE = (
    Path(__file__).resolve().parent
    / "testdata"
    / "lint"
    / "metar_speci"
    / "INVALID_VISIBILITY.yml"
)


def test_tc_f29_spike_load_yaml_rule_cases() -> None:
    cases = load_rule_cases(_SPIKE)
    assert len(cases) == 20
    assert all(isinstance(c, RuleCase) for c in cases)
    assert {c.bucket for c in cases} == set(BUCKETS)
    assert all(c.rule_id == "INVALID_VISIBILITY" for c in cases)
    assert all(c.engine == "lint" for c in cases)
    ready = [c for c in cases if c.status == "ready"]
    assert len(ready) == 2
    assert {c.bucket for c in ready} == {"happy", "sad"}


@pytest.mark.parametrize(
    ("bucket", "case_id", "expected_node"),
    [
        ("happy", "01", "INVALID_VISIBILITY/happy/01"),
        ("sad", "01", "INVALID_VISIBILITY/sad/01"),
        ("edge_pass", "01", "INVALID_VISIBILITY/edge_pass/01"),
        ("edge_fail", "01", "INVALID_VISIBILITY/edge_fail/01"),
    ],
)
def test_tc_f29_spike_node_id_shape(
    bucket: str, case_id: str, expected_node: str
) -> None:
    cases = {(c.bucket, c.case_id): c for c in load_rule_cases(_SPIKE)}
    assert cases[(bucket, case_id)].node_id == expected_node


def test_tc_f29_spike_needs_fixture_status() -> None:
    cases = load_rule_cases(_SPIKE)
    pending = [c for c in cases if c.status == "needs-fixture"]
    assert len(pending) == 18
    assert all(c.tac is None for c in pending)


def test_tc_f29_spike_rejects_bad_case_id(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text(
        'rule_id: X\nengine: lint\ncases:\n  - bucket: happy\n    case_id: "1"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="two digits"):
        load_rule_cases(bad)
