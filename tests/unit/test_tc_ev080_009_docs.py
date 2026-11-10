"""TC-EV080-009 — standing docs + ADR-007 cite 100% coverage gate.

[Corpus: tests] [Corpus: adr/ADR-007] [Corpus: tech-spec] EV-080 / #1077
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

ADR = ROOT / "docs" / "adr" / "ADR-007-universal-coverage-gate.md"
TECH = ROOT / "docs" / "tech-spec.md"
TECH_REQ = ROOT / "docs" / "technical-requirements.md"
TEST_PLAN = ROOT / "docs" / "test-plan.md"
AGENTS = ROOT / "AGENTS.md"


@pytest.mark.unit
class TestTcEv080StandingDocs:
    """AC6 / TC-EV080-009 — docs greppable for 100% gate."""

    def test_adr_007_title_and_floor(self) -> None:
        if not ADR.is_file():
            pytest.skip("local ADR tree not in git (EV-repo-docs-cleanup)")
        text = ADR.read_text(encoding="utf-8")
        assert "100%" in text
        assert "Universal 100% Coverage Gate" in text
        assert "fail_under = 100" in text or "fail_under **100**" in text

    def test_typing_policy_coverage_section(self) -> None:
        # typing-policy.md removed; coverage floor lives in tech-spec + AGENTS.
        tech = TECH.read_text(encoding="utf-8")
        tech_req = TECH_REQ.read_text(encoding="utf-8") if TECH_REQ.is_file() else ""
        agents = AGENTS.read_text(encoding="utf-8")
        text = tech + "\n" + tech_req + "\n" + agents
        assert "**100%** line and branch" in text or "100% line+branch" in text
        assert "fail_under = 100" in text or "fail_under **100**" in text
        assert (
            "scripts/**/*.py" in text or "scripts/**/*.sh" in text or "scripts/" in text
        )

    def test_test_plan_metrics_and_tc_block(self) -> None:
        text = TEST_PLAN.read_text(encoding="utf-8")
        assert "**100%** line+branch" in text
        assert "TC-EV080-009" in text
        assert "ADR-007" in text
