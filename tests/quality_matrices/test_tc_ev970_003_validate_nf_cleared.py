"""TC-EV970-003 — validate/metar_speci has no needs-fixture scaffolds (EV-970 S3)."""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import load_rule_cases_tree

_VALIDATE_ROOT = (
    Path(__file__).resolve().parent / "testdata" / "validate" / "metar_speci"
)


def test_tc_ev970_003_validate_needs_fixture_cleared() -> None:
    """Validate pilot slots are ready or intentional oos — not indefinite scaffolds."""
    cases = [c for c in load_rule_cases_tree(_VALIDATE_ROOT) if c.engine == "validate"]
    assert cases, "expected validate RuleCases"
    needs = [c.node_id for c in cases if c.status == "needs-fixture"]
    assert not needs, "validate needs-fixture remaining (EV-970 S3): " + ", ".join(
        needs[:20]
    )
    ready = sum(1 for c in cases if c.status == "ready")
    oos = sum(1 for c in cases if c.status == "oos")
    assert ready >= 650, f"expected material ready fill incl. S3c, got ready={ready}"
    assert ready + oos == len(cases)
    sch_neg = [
        c
        for c in cases
        if c.status == "ready"
        and c.bucket in {"sad", "edge_fail"}
        and "sch_ids" in c.expect
    ]
    assert len(sch_neg) >= 250, f"expected probed SCH negatives, got {len(sch_neg)}"
    assert oos <= 200, f"expected S3c residual oos budget, got oos={oos}"
