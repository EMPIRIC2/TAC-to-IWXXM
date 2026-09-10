"""TC-EV970-001 — convert/metar_speci has no needs-fixture scaffolds (EV-970 S1)."""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import load_rule_cases_tree

_CONVERT_ROOT = Path(__file__).resolve().parent / "testdata" / "convert" / "metar_speci"


def test_tc_ev970_001_convert_needs_fixture_cleared() -> None:
    """Convert pilot slots are ready or intentional oos — not indefinite scaffolds."""
    cases = [c for c in load_rule_cases_tree(_CONVERT_ROOT) if c.engine == "convert"]
    assert cases, "expected convert RuleCases"
    needs = [c.node_id for c in cases if c.status == "needs-fixture"]
    assert not needs, "convert needs-fixture remaining (EV-970 S1): " + ", ".join(
        needs[:20]
    )
    ready = sum(1 for c in cases if c.status == "ready")
    oos = sum(1 for c in cases if c.status == "oos")
    assert ready >= 200, f"expected material ready fill, got ready={ready}"
    assert ready + oos == len(cases)
