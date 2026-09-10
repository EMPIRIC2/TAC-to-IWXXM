"""TC-EV970-002 — lint/metar_speci has no needs-fixture scaffolds (EV-970 S2)."""

from __future__ import annotations

from pathlib import Path

from tests.quality_matrices.loaders import load_rule_cases_tree

_LINT_ROOT = Path(__file__).resolve().parent / "testdata" / "lint" / "metar_speci"


def test_tc_ev970_002_lint_needs_fixture_cleared() -> None:
    """Lint pilot slots are ready (or intentional oos) — not indefinite scaffolds."""
    cases = [c for c in load_rule_cases_tree(_LINT_ROOT) if c.engine == "lint"]
    assert cases, "expected lint RuleCases"
    needs = [c.node_id for c in cases if c.status == "needs-fixture"]
    assert not needs, "lint needs-fixture remaining (EV-970 S2): " + ", ".join(
        needs[:20]
    )
    ready = sum(1 for c in cases if c.status == "ready")
    assert ready >= 700, f"expected material ready fill, got ready={ready}"
